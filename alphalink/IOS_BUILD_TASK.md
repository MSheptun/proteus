# Задача для Арбитра: собрать iOS-версию AlphaLink на Mac mini

Контекст: приложение AlphaLink (форк RustDesk 1.5.0). Владелец: MSheptun. Сборка iOS возможна
только на macOS, поэтому нужна помощь Mac mini. Репозиторий публичный, клонируется без авторизации.

## Что сделать

1. Клонировать в **новый отдельный каталог** (чужие проекты на Mac не трогать):
   ```bash
   git clone --branch claude/awesome-euler-7dejoy https://github.com/MSheptun/proteus.git alphalink-src
   ```
   (если PR #2 уже влит в `master`, ветку `--branch` можно не указывать).
2. Запустить сборку (скрипт сам всё скачает и соберёт, подробности в шапке скрипта и в
   `alphalink/README.md`, раздел «iOS (Xcode)»):
   ```bash
   cd alphalink-src
   alphalink/scripts/build_ios.sh "$PWD/../alphalink-ios" --archive
   ```
3. Результат: `alphalink-ios/flutter/build/ios/archive/Runner.xcarchive` (неподписанный архив).
   Подписанный `.ipa` нужен **только если** на Mac уже есть рабочая подпись Apple для
   `com.msheptun.alphalink`. Новых аккаунтов, сертификатов и профилей не создавать.

## Требования на Mac

Xcode (+ command line tools), Homebrew, rustup, git, python3 и **Flutter 3.24.5** (именно эта версия).
Скрипт сам доустановит nasm, yasm, pkg-config, cargo-expand, flutter_rust_bridge_codegen, Rust 1.75
и соберёт зависимости через vcpkg (кэш `~/.alphalink-vcpkg`). Нужно примерно 15-20 ГБ места;
первый запуск долгий, потому что ffmpeg и др. собираются из исходников.

## Важно

* iOS-часть скрипта ещё **ни разу не запускалась на Mac**: возможны ошибки. При падении пришлите
  владельцу название шага и **последние 40-60 строк лога**, владелец перешлёт их в облачный чат,
  где скрипт будет исправлен.
* Если Mac занят другой тяжёлой задачей, не мешайте ей: соберите позже или поставьте в очередь.
* Не менять и не удалять ничего за пределами нового каталога, `~/.alphalink-vcpkg` и стандартных
  кэшей brew/cargo/flutter. В репозиторий ничего не пушить.

## Отчёт владельцу

Удалось ли; путь к артефакту и его размер; версии (`xcodebuild -version`, `flutter --version`,
`rustc +1.75 --version`); если нет, то на каком шаге упало и хвост лога.
