# Bluetooth Messenger

A simple Bluetooth-based messaging application for Android and Windows. Messages are stored in RAM only and automatically deleted after 5 minutes.

## � Quick Start

**Run directly with Python:**

```bash
git clone https://github.com/JeevikaS-19/Bluetooth_msgs.git
cd Bluetooth_msgs
pip install kivy pybluez
python main.py
```

**Download pre-built apps:** Coming soon! (See [DISTRIBUTION.md](DISTRIBUTION.md) to build yourself)

## Features

- 🔵 **Bluetooth Communication**: Uses PyBluez for cross-platform Bluetooth support
- 🔐 **Simple Authentication**: PIN-based authentication for secure connections
- 💬 **Real-time Messaging**: Send and receive messages instantly
- 👥 **Multi-peer Support**: Host can connect to multiple clients simultaneously
- ⏰ **Auto-deletion**: Messages are automatically deleted after 5 minutes
- 🖥️ **Simple Terminal UI**: Clean, easy-to-use command-line interface
- 📱 **GUI App Available**: Standalone apps for Android and Windows

## Quick Start (GUI App)

**The easiest way to use Bluetooth Messenger is with the standalone apps!**

1. **Download** the app for your platform from [Releases](https://github.com/JeevikaS-19/Bluetooth_msgs/releases)
2. **Install** and run the app
3. **Select mode**:
   - Tap "Scan for Devices" to find nearby Bluetooth devices
   - Select a device to connect as client (you'll need their PIN)
   - Or tap "Start as Host" to create a chat room and get a PIN
4. **Chat**: Simple message interface with auto-scrolling

**User Flow:**
```
App Opens → Device List → Select Device/Start Host → Enter PIN (client) / Get PIN (host) → Chat!
```

## Installation (For Developers)

### Prerequisites

- Python 3.7 or higher
- Bluetooth adapter (built-in or USB)
- Bluetooth enabled on all devices

### Laptop (Windows/Linux/Mac)

1. Clone the repository:
```bash
git clone https://github.com/JeevikaS-19/Bluetooth_msgs.git
cd Bluetooth_msgs
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note for Windows users**: You may need to install Microsoft Visual C++ 14.0 or greater for PyBluez. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

**Note for Linux users**: Install Bluetooth libraries:
```bash
sudo apt-get install libbluetooth-dev
```

### Android

1. Install a Python environment (recommended: **Pydroid 3** from Play Store)
2. Install the required package in Pydroid 3:
   - Open Pydroid 3
   - Go to Menu → Pip
   - Install `pybluez`
3. Copy the repository files to your Android device
4. Enable Bluetooth and make sure devices are paired

## Usage

### GUI App (Recommended)

Run the GUI version:
```bash
python main.py
```

### Running as Host (Server) - Terminal Version

The host generates an authentication PIN that clients use to connect.

```bash
python host.py
```

The host will:
1. Display a 6-digit PIN
2. Wait for client connections
3. Show connected peers
4. Allow sending messages to all connected clients

**Host Commands:**
- Type a message and press Enter to send to all clients
- `/status` - Show connected peers
- `/messages` - Show recent messages
- `/quit` - Shut down the server

### Running as Client

The client discovers nearby Bluetooth devices and connects to the host.

```bash
python client.py
```

The client will:
1. Search for nearby Bluetooth devices
2. Display a list of found devices
3. Prompt you to select the host
4. Request the authentication PIN
5. Connect and allow messaging

**Client Commands:**
- Type a message and press Enter to send
- `/messages` - Show recent messages
- `/quit` - Disconnect from host

## Simple Terminal UI

### Host View
```
==================================================
BLUETOOTH MESSENGER - HOST MODE
==================================================

Authentication PIN: 123456
Share this PIN with clients to allow connections.

Waiting for connections...
==================================================

✓ peer1 connected (XX:XX:XX:XX:XX:XX)

--- Connected Peers ---
  • peer1
-----------------------

[18:30:45] peer1: Hello!

host> Hi there!
```

### Client View
```
==================================================
BLUETOOTH MESSENGER - CLIENT MODE
==================================================

Found 2 device(s):
  1. MyLaptop (XX:XX:XX:XX:XX:XX)
  2. OtherDevice (YY:YY:YY:YY:YY:YY)

Select device number: 1

Connecting to MyLaptop...
Enter authentication PIN: 123456
✓ Authentication successful!

You can now send messages.
==================================================

[18:30:45] host: Hi there!

me> Hello from client!
```

## How It Works

1. **Host starts** and generates a random 6-digit PIN
2. **Client discovers** nearby Bluetooth devices
3. **Client connects** to the host's Bluetooth service
4. **Authentication** happens using the PIN
5. **Messages are exchanged** in real-time
6. **Messages are stored** in RAM only
7. **Auto-deletion** removes messages after 5 minutes

## Security & Privacy

- 🔒 Messages are **never stored permanently**
- 🧹 All messages are **automatically deleted** after 5 minutes
- 🔐 Simple **PIN authentication** prevents unauthorized access
- 💾 Messages are stored in **RAM only** - no disk writes

## Troubleshooting

### Connection Issues

**Problem**: Can't find devices
- Ensure Bluetooth is enabled on both devices
- Make sure devices are discoverable
- Try pairing devices in your OS Bluetooth settings first

**Problem**: PyBluez installation fails on Windows
- Install Visual C++ Build Tools
- Use Python 3.7-3.9 (better PyBluez compatibility)

**Problem**: Permission denied on Linux
```bash
sudo python host.py  # or client.py
```

### Android Issues

**Using Pydroid 3**:
- Grant Bluetooth permissions to Pydroid 3
- Enable "Nearby devices" permission
- Some Android versions may have restrictions on Bluetooth access

**Alternative: Termux**:
```bash
pkg install python bluetooth
pip install pybluez
```

## Limitations

- PyBluez has varying support across platforms
- Android support requires third-party Python environments
- Bluetooth range is typically 10-100 meters depending on device
- No encryption beyond basic Bluetooth security

## Architecture

```
┌─────────────────┐
│   host.py       │  ← Bluetooth Server
│  - Auth Manager │
│  - Message Mgr  │
│  - Multi-client │
└─────────────────┘
        ↕
   Bluetooth
        ↕
┌─────────────────┐
│  client.py      │  ← Bluetooth Client
│  - Discovery    │
│  - Auth         │
│  - Messaging    │
└─────────────────┘
```

## License

MIT License - feel free to use and modify!

## Contributing

Contributions welcome! Please feel free to submit pull requests or open issues.
