# Building and Distributing Bluetooth Messenger

This guide explains how to build the app for different platforms and distribute it via GitHub Releases.

## 🏗️ Building the Apps

### Android APK

**Requirements:**
- Linux or WSL (Windows Subsystem for Linux)
- Python 3.8+
- Java JDK
- Android SDK

**Steps:**

1. **Install Buildozer** (on Linux/WSL):
   ```bash
   pip install buildozer
   pip install cython
   ```

2. **Install dependencies** (Ubuntu/Debian):
   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   ```

3. **Build the APK**:
   ```bash
   chmod +x build_scripts/build_android.sh
   ./build_scripts/build_android.sh
   ```
   
   Or manually:
   ```bash
   buildozer android debug
   ```

4. **Find your APK**:
   - Location: `bin/bluetoothmessenger-1.0-debug.apk`
   - File size: ~20-30 MB

**For Windows users:**
- Use WSL (Windows Subsystem for Linux)
- Install WSL: `wsl --install`
- Then follow Linux steps above

### Windows Executable

**Requirements:**
- Windows PC
- Python 3.8+

**Steps:**

1. **Run the build script**:
   ```batch
   build_scripts\build_windows.bat
   ```

2. **Find your EXE**:
   - Location: `dist\BluetoothMessenger.exe`
   - File size: ~50-80 MB

**Manual build:**
```bash
pip install pyinstaller kivy
pyinstaller build_windows.spec
```

## 📦 Distribution via GitHub Releases

### Step 1: Create a Release

1. **Go to your repository**:
   ```
   https://github.com/JeevikaS-19/Bluetooth_msgs
   ```

2. **Click "Releases"** → **"Create a new release"**

3. **Fill in release info**:
   - **Tag**: `v1.0.0`
   - **Title**: `Bluetooth Messenger v1.0.0`
   - **Description**:
     ```markdown
     # Bluetooth Messenger v1.0.0
     
     Simple Bluetooth messaging app for Android and Windows
     
     ## Features
     - PIN-based authentication
     - Multi-peer chat
     - Messages auto-delete after 5 minutes
     - No permanent storage
     
     ## Downloads
     - **Android**: Download `bluetoothmessenger-1.0.apk` below
     - **Windows**: Download `BluetoothMessenger.exe` below
     
     ## Installation
     
     ### Android
     1. Download the APK
     2. Enable "Install from Unknown Sources" in Settings
     3. Tap the APK to install
     4. Grant Bluetooth permissions
     
     ### Windows
     1. Download the EXE
     2. Run the executable
     3. If Windows SmartScreen appears, click "More info" → "Run anyway"
     ```

4. **Upload files**:
   - Drag and drop:
     - `bin/bluetoothmessenger-1.0-debug.apk` (rename to `bluetoothmessenger-1.0.apk`)
     - `dist/BluetoothMessenger.exe`

5. **Publish release**

### Step 2: Get Download Links

After publishing, you'll get direct download links:

```
Android APK:
https://github.com/JeevikaS-19/Bluetooth_msgs/releases/download/v1.0.0/bluetoothmessenger-1.0.apk

Windows EXE:
https://github.com/JeevikaS-19/Bluetooth_msgs/releases/download/v1.0.0/BluetoothMessenger.exe
```

### Step 3: Add Download Badges (Optional)

Update your README.md with download badges:

```markdown
[![Download Android](https://img.shields.io/badge/Download-Android%20APK-green)](https://github.com/JeevikaS-19/Bluetooth_msgs/releases/latest/download/bluetoothmessenger-1.0.apk)
[![Download Windows](https://img.shields.io/badge/Download-Windows%20EXE-blue)](https://github.com/JeevikaS-19/Bluetooth_msgs/releases/latest/download/BluetoothMessenger.exe)
```

## 📱 User Installation Guide

### Android

1. **Download** the APK from GitHub Releases
2. **Enable installation from unknown sources**:
   - Settings → Security → Install unknown apps → Chrome (or your browser) → Allow
3. **Install**: Tap the downloaded APK file
4. **Grant permissions**: Allow Bluetooth and Location permissions
5. **Run**: Open "Bluetooth Messenger" from app drawer

### Windows

1. **Download** the EXE from GitHub Releases
2. **Run**: Double-click `BluetoothMessenger.exe`
3. **Windows SmartScreen** (if appears):
   - Click "More info"
   - Click "Run anyway"
4. **Grant permissions**: Allow Bluetooth access if prompted

## 🔄 Updating the App

To release a new version:

1. Update version in `buildozer.spec` (line with `version = 1.0`)
2. Rebuild both apps
3. Create a new GitHub release (e.g., `v1.1.0`)
4. Upload new APK and EXE
5. Users download the new version

## ⚠️ Important Notes

### Code Signing

**Android:**
- Debug APKs are unsigned (fine for personal use)
- For public distribution, create a signed release APK:
  ```bash
  buildozer android release
  ```
- Requires creating a keystore

**Windows:**
- EXE is unsigned (will trigger SmartScreen)
- To avoid warnings, purchase a code signing certificate (~$200/year)
- For free distribution, users must click "Run anyway"

### App Store Distribution

**Google Play Store:**
- Requires Google Play Developer account ($25 one-time fee)
- Needs signed release APK
- Review process 1-3 days

**Microsoft Store:**
- Requires Microsoft Developer account ($19/year)
- Needs MSIX package (different from EXE)
- Review process 24-48 hours

**Direct distribution (current method):**
- Free
- No review process
- Users must enable "unknown sources" (Android)
- May trigger security warnings (Windows)

## 🎯 Quick Distribution Checklist

- [ ] Build Android APK
- [ ] Build Windows EXE
- [ ] Test both builds
- [ ] Create GitHub Release
- [ ] Upload both files
- [ ] Update README with download links
- [ ] Share release link with users

## 📊 File Sizes

Expected file sizes:
- **Android APK**: 20-30 MB
- **Windows EXE**: 50-80 MB

Both are standalone - no additional installation needed!
