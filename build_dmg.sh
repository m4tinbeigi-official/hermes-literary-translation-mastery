#!/bin/bash
set -e

echo "🔨 Building HermesBookTranslator.app with PyInstaller..."
cd "$(dirname "$0")"

rm -rf build dist

pyinstaller --noconfirm --onedir --windowed --name "HermesBookTranslator" app.py

echo "📦 Creating DMG file..."
DMG_NAME="HermesBookTranslator-macOS.dmg"
VOLUME_NAME="Hermes Book Translator"
TEMP_DMG_DIR="dist/dmg_temp"

rm -rf "$TEMP_DMG_DIR" "$DMG_NAME" "dist/$DMG_NAME"
mkdir -p "$TEMP_DMG_DIR"

cp -R "dist/HermesBookTranslator.app" "$TEMP_DMG_DIR/"
ln -s /Applications "$TEMP_DMG_DIR/Applications"

hdiutil create -volname "$VOLUME_NAME" -srcfolder "$TEMP_DMG_DIR" -ov -format UDZO "dist/$DMG_NAME"
rm -rf "$TEMP_DMG_DIR"

echo "✅ DMG Created successfully at: dist/$DMG_NAME"
