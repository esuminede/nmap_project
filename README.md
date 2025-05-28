# Network Scanner Tool

A comprehensive network scanning tool with a graphical user interface that provides network device discovery, port scanning, and operating system detection capabilities.

## Features

- **Device Scanning**: Discover active devices on your local network
- **Port Scanning**: 
  - Custom port range scanning
  - Common port group scanning (Web, FTP, SSH, etc.)
  - Service detection and banner grabbing
- **Operating System Detection**: Identify the operating system of target devices
- **User-Friendly GUI**: Easy-to-use interface with progress tracking
- **Real-time Results**: Live scanning updates and detailed output

## Requirements

- Python 3.x
- Required Python packages:
  - tkinter (usually comes with Python)
  - threading (built-in)
  - json (built-in)

## Installation

1. Clone this repository:
```bash
git clone [repository-url]
cd network-scanner
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python network_scanner_gui.py
```

### Device Scanning
1. Enter the subnet (e.g., 192.168.1)
2. Click "Scan Devices" to discover active devices on the network

### Port Scanning
1. Enter the target IP address
2. Choose scanning type:
   - Custom Port Range: Specify start and end ports
   - Common Port Groups: Select predefined port groups
3. Click "Scan Ports" to begin port scanning

### Operating System Detection
1. Enter the target IP address
2. Click "Detect OS" to identify the operating system

## Security Notice

This tool is intended for educational and legitimate network administration purposes only. Always:
- Obtain proper authorization before scanning networks
- Respect privacy and security policies
- Use responsibly and ethically

## License

[Your chosen license]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 