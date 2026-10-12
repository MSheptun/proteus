#!/usr/bin/env bash
# Builds the AlphaKeys release APK (debug-signed, for testing).
# usage: build.sh <workdir>     (needs JDK 21+, ANDROID_HOME with platform 37, NDK 28.0.13004108)
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
work="${1:?usage: build.sh <workdir>}"
"$here/prepare.sh" "$work"
cd "$work"
if [ -n "${MAVEN_CENTRAL_MIRROR:-}" ]; then # optional, e.g. when Maven Central rate-limits you
  sed -i "s#mavenCentral()#maven { url = uri(\"$MAVEN_CENTRAL_MIRROR\") }#" build.gradle.kts
fi
./gradlew --no-daemon assembleRelease
ls -la app/build/outputs/apk/release/*.apk
