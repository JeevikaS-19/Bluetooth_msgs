#!/bin/bash
# Build script for Android APK using Buildozer

echo "Building Bluetooth Messenger for Android..."
echo ""

# Install buildozer if not already installed
if ! command -v buildozer &> /dev/null
then
    echo "Buildozer not found. Installing..."
    pip install buildozer
    pip install cython
fi

echo "Starting build process..."
echo "This may take 15-30 minutes on first build..."
echo ""

# Build debug APK
buildozer android debug

echo ""
if [ -f "bin/bluetoothmessenger-1.0-debug.apk" ]; then
    echo "Build successful!"
    echo "APK location: bin/bluetoothmessenger-1.0-debug.apk"
    echo ""
    echo "To install on Android device:"
    echo "  adb install bin/bluetoothmessenger-1.0-debug.apk"
    echo ""
    echo "Or transfer the APK to your phone and install manually"
else
    echo "Build failed. Check the output above for errors."
fi
