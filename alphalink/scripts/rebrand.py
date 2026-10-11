#!/usr/bin/env python3
"""Rename the user-visible product to AlphaLink in a patched RustDesk checkout.

Usage: rebrand.py <rustdesk-source-root>

The core of the rename is `APP_NAME`: RustDesk then runs in its built-in
"custom client" mode, which re-brands every translated string at run time,
keeps window lookup / install paths / service names consistent and, importantly,
disables the stock auto-update (which would otherwise replace AlphaLink with
the original RustDesk).

Everything else here is a native resource or a hard-coded display string.
Deliberately NOT renamed: binary and library file names, Rust/Dart identifiers,
protocol/IPC/channel names, device and driver names, URLs, licence and copyright
notices (AGPL requires them to stay).
"""
import re
import sys
from pathlib import Path

NAME = "AlphaLink"
root = Path(sys.argv[1]) if len(sys.argv) == 2 else sys.exit(__doc__)


def edit(rel, fn, count_min=1):
    p = root / rel
    s = p.read_text(encoding="utf-8")
    new, n = fn(s)
    if n < count_min:
        sys.exit(f"rebrand: nothing replaced in {rel} (upstream changed?)")
    p.write_text(new, encoding="utf-8")


def sub(old, new, regex=False):
    def f(s):
        if regex:
            return re.subn(old, new, s)
        return s.replace(old, new), s.count(old)
    return f


# --- core: application name (custom-client mode)
edit("libs/hbb_common/src/config.rs", sub('RwLock::new("RustDesk".to_owned())', f'RwLock::new("{NAME}".to_owned())'))

# --- Flutter UI
edit("flutter/lib/desktop/widgets/tabbar_widget.dart", sub('"RustDesk",', f'"{NAME}",'))

# --- Windows
edit("flutter/windows/runner/Runner.rc", sub('"RustDesk Remote Desktop"', f'"{NAME} Remote Desktop"'))
edit("flutter/windows/runner/Runner.rc", sub('VALUE "ProductName", "RustDesk"', f'VALUE "ProductName", "{NAME}"'))
edit("flutter/windows/runner/main.cpp", sub('std::wstring app_name = L"RustDesk";', f'std::wstring app_name = L"{NAME}";'))
edit("src/platform/windows.rs", sub('"RustDesk Output"', f'"{NAME} Output"'))

# --- macOS: display name (the .app bundle file name stays, build scripts rely on it)
edit(
    "flutter/macos/Runner/Info.plist",
    sub(
        r"(\t<key>CFBundleName</key>\n\t<string>\$\(PRODUCT_NAME\)</string>\n)",
        r"\1\t<key>CFBundleDisplayName</key>\n\t<string>" + NAME + "</string>\n",
        regex=True,
    ),
)

# --- Linux
edit("flutter/linux/my_application.cc", sub(r'gtk_(header_bar|window)_set_title\((\w+), "rustdesk"\)', rf'gtk_\1_set_title(\2, "{NAME}")', regex=True), 2)
for f in ("res/rustdesk.desktop", "res/rustdesk-link.desktop"):
    edit(f, sub("Name=RustDesk", f"Name={NAME}"))

# --- Android
for p in (root / "flutter/android/app/src/main/res").glob("values*/strings.xml"):
    s = p.read_text(encoding="utf-8")
    p.write_text(s.replace("RustDesk+", NAME).replace("RustDesk", NAME), encoding="utf-8")
edit("flutter/android/app/src/main/AndroidManifest.xml", sub('android:label="RustDesk Input"', f'android:label="{NAME} Input"'))
edit("flutter/android/app/src/main/AndroidManifest.xml", sub('android:label="RustDesk"', f'android:label="{NAME}"'))
kt = "flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/"
edit(kt + "BootReceiver.kt", sub('"RustDesk is Open"', f'"{NAME} is Open"'))
edit(kt + "MainService.kt", sub('DEFAULT_NOTIFY_TITLE = "RustDesk"', f'DEFAULT_NOTIFY_TITLE = "{NAME}"'))
edit(kt + "MainService.kt", sub('"RustDesk Service Channel"', f'"{NAME} Service Channel"'))
edit(kt + "MainService.kt", sub('"RustDesk Service"', f'"{NAME} Service"'))

# --- iOS (Xcode project)
edit("flutter/ios/Runner/Info.plist", sub(r"(<key>CFBundle(?:DisplayName|Name)</key>\s*<string>)RustDesk(</string>)", rf"\g<1>{NAME}\2", regex=True), 2)
edit("flutter/ios/Runner.xcodeproj/project.pbxproj", sub("PRODUCT_BUNDLE_IDENTIFIER = com.carriez.flutterHbb;", "PRODUCT_BUNDLE_IDENTIFIER = com.msheptun.alphalink;"), 3)
# upstream's Apple team id cannot sign for anybody else: pick your own team in Xcode
edit("flutter/ios/Runner.xcodeproj/project.pbxproj", sub("DEVELOPMENT_TEAM = HZF9JMC8YN;", 'DEVELOPMENT_TEAM = "";'), 3)
# push notifications are not used; the entitlement would block signing with a free Apple ID
edit("flutter/ios/Runner/Runner.entitlements", sub(r"\s*<key>aps-environment</key>\s*<string>development</string>", "", regex=True))
(root / "flutter/ios/exportOptions.plist").write_text(
    '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>method</key>
	<string>development</string>
	<key>signingStyle</key>
	<string>automatic</string>
	<key>teamID</key>
	<string>REPLACE_WITH_YOUR_TEAM_ID</string>
</dict>
</plist>
''',
    encoding="utf-8",
)

# --- hard-coded English display strings in Rust
edit("src/server/wayland.rs", sub("RustDesk", NAME))
for f in ("macos", "linux", "windows"):
    edit(f"src/whiteboard/{f}.rs", sub('"RustDesk whiteboard"', f'"{NAME} whiteboard"'))
edit("src/auth_2fa.rs", sub('const ISSUER: &str = "RustDesk";', f'const ISSUER: &str = "{NAME}";'))
edit("src/server/dbus.rs", sub('"RustDesk DBus Error: {}"', f'"{NAME} DBus Error: {{}}"'))

print(f"Rebranded to {NAME} in {root}")
