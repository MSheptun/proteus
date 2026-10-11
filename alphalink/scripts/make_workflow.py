#!/usr/bin/env python3
"""Derive the AlphaLink CI workflow from upstream's flutter-build.yml.

Usage: make_workflow.py <upstream-checkout> <output-dir>

Writes alphalink.yml (+ the two reusable workflows it calls) into <output-dir>.

Keeps only the Flutter Android (arm64), Windows (x64), macOS and Linux (x86_64)
jobs, swaps every `checkout` for "checkout overlay + apply patches", and turns
the GitHub *release* uploads into plain workflow artifacts so that nothing is
published anywhere without the owner's decision.
"""
import os
import sys
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

KEEP = [
    "generate-bridge",
    "build-RustDeskTempTopMostWindow",
    "build-for-windows-flutter",
    "build-for-macOS",
    "build-rustdesk-android",
    "build-rustdesk-linux",
    "build-rustdesk-ios",
]
# matrix filters: job -> predicate over a matrix.job entry
MATRIX_KEEP = {
    "build-for-windows-flutter": lambda j: j.get("arch") == "x86_64",
    "build-rustdesk-android": lambda j: j.get("arch") == "aarch64",
    "build-rustdesk-linux": lambda j: j.get("arch") == "x86_64",
}

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096

CHECKOUT_PREFIX = "actions/checkout@"
RELEASE_PREFIX = "softprops/action-gh-release@"
PREPARE_RUN = 'bash plus/alphalink/scripts/prepare.sh "$GITHUB_WORKSPACE"'
counter = {"n": 0}


def load(path):
    with open(path) as f:
        return yaml.load(f)


def to_artifact_step(step, upload_action):
    """Turn a softprops/action-gh-release step into an upload-artifact step."""
    counter["n"] += 1
    new = CommentedMap()
    new["name"] = (step.get("name") or "Upload") + " (artifact)"
    if "if" in step:
        new["if"] = step["if"]
    new["uses"] = upload_action
    w = CommentedMap()
    w["name"] = "alphalink-${{ github.job }}-${{ strategy.job-index }}-%d" % counter["n"]
    w["path"] = step.get("with", {}).get("files", "")
    w["if-no-files-found"] = "warn"
    new["with"] = w
    return new


def rewrite_steps(job):
    if "steps" not in job:  # job that calls a reusable workflow
        return
    upload_action = None
    for step in job.get("steps", []):
        u = str(step.get("uses", ""))
        if u.startswith("actions/upload-artifact@"):
            upload_action = u
    upload_action = upload_action or "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"
    new_steps = CommentedSeq()
    for step in job.get("steps", []):
        u = str(step.get("uses", ""))
        if u.startswith(CHECKOUT_PREFIX):
            s1 = CommentedMap()
            s1["name"] = "Checkout AlphaLink overlay"
            s1["uses"] = u
            s1["with"] = CommentedMap(path="plus")
            new_steps.append(s1)
            s2 = CommentedMap()
            s2["name"] = "Prepare patched AlphaLink source"
            s2["shell"] = "bash"
            s2["run"] = PREPARE_RUN
            new_steps.append(s2)
        elif u.startswith(RELEASE_PREFIX):
            new_steps.append(to_artifact_step(step, upload_action))
        else:
            new_steps.append(step)
    if job.get("name") == "build rustdesk ios ipa":
        # `flutter build ipa --no-codesign` yields an .xcarchive, not an .ipa
        up = CommentedMap()
        up["name"] = "Upload unsigned iOS archive"
        up["uses"] = upload_action
        w = CommentedMap()
        w["name"] = "alphalink-ios-xcarchive"
        w["path"] = "flutter/build/ios/archive/Runner.xcarchive"
        w["if-no-files-found"] = "warn"
        up["with"] = w
        new_steps.append(up)
    job["steps"] = new_steps


def retarget_reusable(job, mapping):
    u = job.get("uses")
    if u and str(u) in mapping:
        job["uses"] = mapping[str(u)]


def main(up, out):
    wfdir = os.path.join(up, ".github/workflows")
    os.makedirs(out, exist_ok=True)
    mapping = {
        "./.github/workflows/bridge.yml": "./.github/workflows/alphalink-bridge.yml",
        "./.github/workflows/third-party-RustDeskTempTopMostWindow.yml":
            "./.github/workflows/alphalink-topmost.yml",
    }

    # --- reusable workflows: same checkout rewrite, nothing dropped
    for src_name, dst_name in (
        ("bridge.yml", "alphalink-bridge.yml"),
        ("third-party-RustDeskTempTopMostWindow.yml", "alphalink-topmost.yml"),
    ):
        wf = load(os.path.join(wfdir, src_name))
        for job in wf["jobs"].values():
            rewrite_steps(job)
        if src_name == "bridge.yml":
            # Only the default (Flutter 3.22.3) bridge is needed; the 3.44 one is for Windows arm64.
            m = wf["jobs"]["generate_bridge"]["strategy"]["matrix"]["job"]
            for i in reversed(range(len(m))):
                if m[i].get("artifact-name") != "bridge-artifact":
                    del m[i]
        with open(os.path.join(out, dst_name), "w") as f:
            yaml.dump(wf, f)

    # --- main workflow
    wf = load(os.path.join(wfdir, "flutter-build.yml"))
    wf["name"] = "Build AlphaLink (Android / Windows / macOS / Linux)"
    on = CommentedMap()
    on["workflow_dispatch"] = CommentedMap(
        inputs=CommentedMap(
            **{
                "upload-artifact": CommentedMap(type="boolean", default=True),
                "upload-tag": CommentedMap(type="string", default="alphalink"),
            }
        )
    )
    del wf["on"]
    wf.insert(1, "on", on)
    for name in list(wf["jobs"].keys()):
        if name not in KEEP:
            del wf["jobs"][name]
    for jname, job in wf["jobs"].items():
        needs = job.get("needs")
        if needs is not None:
            if isinstance(needs, str):
                needs = [needs]
            kept = [n for n in needs if n in wf["jobs"]]
            if kept:
                job["needs"] = kept
            else:
                del job["needs"]
        pred = MATRIX_KEEP.get(jname)
        if pred:
            m = job["strategy"]["matrix"]["job"]
            for i in reversed(range(len(m))):
                if not pred(m[i]):
                    del m[i]
        retarget_reusable(job, mapping)
        rewrite_steps(job)
    with open(os.path.join(out, "alphalink.yml"), "w") as f:
        yaml.dump(wf, f)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
