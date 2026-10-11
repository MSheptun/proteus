#!/usr/bin/env bash
# Prepare the AlphaLink iOS Xcode project on a Mac.
#
#   alphalink/scripts/build_ios.sh [target-dir] [--archive]
#
# Does, in order:
#   1. fetches upstream RustDesk, applies the AlphaLink patches (prepare.sh)
#   2. builds the native dependencies (vcpkg, triplet arm64-ios)
#   3. generates the flutter<->rust bridge
#   4. builds liblibrustdesk.a for aarch64-apple-ios
#   5. flutter pub get + pod install
# and prints how to open the project in Xcode. With --archive it also runs
# `flutter build ipa --no-codesign`.
#
# Needs: macOS, Xcode (+ command line tools), Homebrew, rustup, git, python3, and Flutter 3.24.5
# on PATH. The first run takes a long time (ffmpeg & co. are built from source).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$PWD/alphalink-ios-src}"
ARCHIVE=0
for a in "$@"; do [ "$a" = "--archive" ] && ARCHIVE=1; done
[ "${1:-}" = "--archive" ] && TARGET="$PWD/alphalink-ios-src"

# versions taken from upstream's CI (flutter-build.yml, 1.5.0)
RUST_VERSION="1.75"
FLUTTER_VERSION="3.24.5"
VCPKG_COMMIT_ID="9e593bb18ea69cc5095e012465dcd675a822ed0d"
CARGO_EXPAND_VERSION="1.0.95"
FRB_VERSION="1.80.1"
TRIPLET="arm64-ios"
RUST_TARGET="aarch64-apple-ios"

die() { echo "error: $*" >&2; exit 1; }
[ "$(uname -s)" = "Darwin" ] || die "this script must run on macOS"
command -v xcodebuild >/dev/null || die "Xcode is not installed (xcode-select --install and install Xcode)"
command -v brew >/dev/null || die "Homebrew is required"
command -v rustup >/dev/null || die "rustup is required (https://rustup.rs)"
command -v flutter >/dev/null || die "flutter $FLUTTER_VERSION is required on PATH"
flutter --version 2>/dev/null | grep -q "Flutter $FLUTTER_VERSION" \
  || echo "warning: Flutter $FLUTTER_VERSION is what upstream uses; you have a different version" >&2

echo "==> 1/5 source"
bash "$HERE/prepare.sh" "$TARGET"
cd "$TARGET"

echo "==> 2/5 native dependencies (vcpkg $TRIPLET)"
brew list nasm >/dev/null 2>&1 || brew install nasm
brew list yasm >/dev/null 2>&1 || brew install yasm
brew list pkg-config >/dev/null 2>&1 || brew install pkg-config
export VCPKG_ROOT="${VCPKG_ROOT:-$HOME/.alphalink-vcpkg}"
if [ ! -d "$VCPKG_ROOT/.git" ]; then
  git clone https://github.com/microsoft/vcpkg "$VCPKG_ROOT"
fi
git -C "$VCPKG_ROOT" fetch -q origin "$VCPKG_COMMIT_ID" 2>/dev/null || git -C "$VCPKG_ROOT" fetch -q origin
git -C "$VCPKG_ROOT" checkout -q "$VCPKG_COMMIT_ID"
[ -x "$VCPKG_ROOT/vcpkg" ] || "$VCPKG_ROOT/bootstrap-vcpkg.sh" -disableMetrics
"$VCPKG_ROOT/vcpkg" install --triplet "$TRIPLET" --x-install-root="$VCPKG_ROOT/installed"

echo "==> 3/5 flutter-rust bridge"
rustup toolchain install "$RUST_VERSION" --profile minimal -c rustfmt
rustup target add "$RUST_TARGET" --toolchain "$RUST_VERSION"
export RUSTUP_TOOLCHAIN="$RUST_VERSION"
cargo install cargo-expand --version "$CARGO_EXPAND_VERSION" --locked
cargo install flutter_rust_bridge_codegen --version "$FRB_VERSION" --features "uuid" --locked
(cd flutter && flutter pub get)
flutter_rust_bridge_codegen \
  --rust-input ./src/flutter_ffi.rs \
  --dart-output ./flutter/lib/generated_bridge.dart \
  --c-output ./flutter/macos/Runner/bridge_generated.h
cp ./flutter/macos/Runner/bridge_generated.h ./flutter/ios/Runner/bridge_generated.h

echo "==> 4/5 liblibrustdesk.a ($RUST_TARGET)"
cargo build --locked --features flutter,hwcodec --release --target "$RUST_TARGET" --lib

echo "==> 5/5 flutter / CocoaPods"
(cd flutter && flutter pub get)
(cd flutter/ios && pod install)

if [ "$ARCHIVE" = 1 ]; then
  (cd flutter && flutter build ipa --release --no-codesign)
  echo "Archive: $TARGET/flutter/build/ios/archive/Runner.xcarchive"
fi

cat <<MSG

Done. Next, in Xcode:
  open "$TARGET/flutter/ios/Runner.xcworkspace"
  Runner target -> Signing & Capabilities: pick your Team (bundle id: com.msheptun.alphalink,
  change it if it is taken). Then Product -> Run (device) or Product -> Archive.

Notes:
  * "Access WiFi Information" needs a paid Apple Developer account; with a free Apple ID remove
    that capability (Runner.entitlements) before signing.
  * iOS can only control other devices (the app has no screen-sharing host on iOS).
MSG
