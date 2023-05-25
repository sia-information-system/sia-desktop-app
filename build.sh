#!/bin/bash

# Clean workspace
echo "Cleaning workspace."
rm -rf build
rm -rf dist
rm *.spec

# Build command
echo "Starting build process."
# This works on Windows.
# pyinstaller --name SIA --onefile --windowed --add-data "etc;etc" --add-data "assets/images;assets/images" src/main.py
pyinstaller --name SIA --onefile --windowed --icon="assets/images/sia-logo.ico" --add-data "etc;etc" --add-data "assets/images;assets/images" --additional-hooks-dir pyinstaller_hooks src/main.py
