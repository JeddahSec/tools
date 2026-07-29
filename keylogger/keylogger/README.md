# 🔑 Keylogger - Educational Security Tool
![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-cross--platform-lightgrey)
![Status](https://img.shields.io/badge/status-educational-orange)
> ⚠️ **DISCLAIMER**: This tool is created for **EDUCATIONAL PURPOSES ONLY**. Unauthorized use of keyloggers is illegal and unethical. Always obtain explicit written permission before monitoring any system. The developer assumes no liability for misuse of this software.
---
## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Security Considerations](#security-considerations)
- [Legal Warning](#legal-warning)
- [Contributing](#contributing)
- [License](#license)
---
## 📖 Overview
This project implements a keylogger with email reporting capabilities, designed specifically for educational purposes in isolated environments. It demonstrates concepts related to:
- System monitoring and event handling
- Network communication via SMTP
- Threading and asynchronous operations
- Signal handling and graceful shutdown
- Secure coding practices
---
## ✨ Features
- **⌨️ Keystroke Logging**: Captures all keyboard input including special keys
- **📧 Email Reporting**: Sends periodic reports via Gmail SMTP
- **🔧 Configurable**: Easy configuration through environment variables
- **🛡️ Graceful Shutdown**: Handles Ctrl+C and termination signals properly
- **📊 Log Management**: Automatic log size management to prevent memory issues
- **🎨 Colored Output**: User-friendly terminal interface with colored messages
- **📝 Comprehensive Logging**: Detailed logging for debugging and monitoring
- **🔒 Security Focused**: Environment variables for sensitive data
- **🧹 Clean Architecture**: Well-organized, documented, and maintainable code
---
## 📦 Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Gmail account (for email reporting)
- Required Python packages (listed in `requirements.txt`)
---
## 🚀 Installation
### 1. Clone the Repository
```bash
git clone https://github.com/jeddahsec/tools.git
cd tools/keylogger
```

### 2. Create Virtual Environment (Recommended)


# On Linux/macOS

```python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```


### 4. Verify Installation

```bash
python -c "import pynput; import termcolor; print('✓ All dependencies installed')"
```


---

## ⚙️ Configuration

### Email Configuration

Create a `.env` file in the project root directory:

```bash
# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SENDER_EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com
# Keylogger Settings
REPORT_INTERVAL=30
MAX_LOG_SIZE=10000
```

### Gmail Setup

1. Enable 2-Factor Authentication on your Gmail account

2. Generate an App Password:
    - Go to Google Account Settings
    - Security → App passwords
    - Select "Mail" and your device
    - Use the generated 16-character password
3. Use this App Password in your `.env` file

> ⚠️ **Never commit your `.env` file to version control!**

### Alternative: Direct Configuration

You can also modify the `KeyloggerConfig` class in `keylogger.py` directly:

```bash
class KeyloggerConfig:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    SENDER_EMAIL = "your_email@gmail.com"
    RECIPIENT_EMAILS = ["recipient@example.com"]
    EMAIL_PASSWORD = "your_app_password"
    REPORT_INTERVAL = 30
    MAX_LOG_SIZE = 10000
```

---
## 🎯 Usage

### Basic Usage
```
python main.py
```
### With Custom Configuration
```bash
# Set environment variables before running
export SENDER_EMAIL="myemail@gmail.com"
export EMAIL_PASSWORD="myapppassword"
export RECIPIENT_EMAILS="admin@example.com"
python main.py
```
### Running with Elevated Privileges

Some systems may require elevated privileges to capture keyboard events:
```bash
# On Linux/macOS
sudo python main.py
# On Windows (Run as Administrator)
python main.py
```
### Stopping the Keylogger

Press `Ctrl+C` to gracefully stop the keylogger. It will:

1. Stop the keyboard listener
2. Send any remaining logs via email
3. Cancel pending timers
4. Exit cleanly
---
## 📁 Project Structure
```
keylogger/
│
├── keylogger.py          # Core keylogger implementation
├── main.py               # Main entry point and controller
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment configuration
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

### File Descriptions

#### `keylogger.py`

- **KeyloggerConfig**: Configuration management class
- **Keylogger**: Main keylogger implementation with:
    - Keyboard event handling
    - Email reporting via SMTP
    - Log management
    - Graceful shutdown

#### `main.py`

- **KeyloggerController**: Application controller with:
    - Signal handling (SIGINT, SIGTERM)
    - User interface with colored output
    - Error handling and recovery
    - Banner display

---

## 🔒 Security Considerations

### Best Practices Implemented
- ✅ Sensitive data stored in environment variables
- ✅ No hardcoded credentials
- ✅ `.env` file in `.gitignore`
- ✅ Graceful error handling
- ✅ Log size limitations
- ✅ Secure SMTP connection (SSL)

### Recommendations

- 🔐 Use dedicated email accounts for testing
- 🔐 Rotate App Passwords regularly
- 🔐 Monitor email sending limits
- 🔐 Use encryption for stored logs
- 🔐 Implement authentication for production use

---
## ⚖️ Legal Warning

### IMPORTANT LEGAL NOTICE

This software is intended **SOLELY FOR EDUCATIONAL PURPOSES** in controlled, isolated environments where you have:
1. **Explicit Permission**: Written authorization from the system owner
2. **Legal Right**: Authority to monitor the target system
3. **Informed Consent**: All users are aware of monitoring activities
4. **Isolated Environment**: Testing in a sandboxed/isolated setup

### Illegal Uses Include (But Not Limited To):

- ❌ Monitoring without consent
- ❌ Deploying on others' systems
- ❌ Using for malicious purposes
- ❌ Violating privacy laws
- ❌ Corporate espionage
- ❌ Identity theft

### Legal Consequences

Unauthorized use of keyloggers may violate:
- Computer Fraud and Abuse Act (CFAA)
- Electronic Communications Privacy Act (ECPA)
- Various state and international laws
- Privacy regulations (GDPR, CCPA, etc.)

**Penalties can include substantial fines and imprisonment.**

> The developer assumes NO LIABILITY and is NOT RESPONSIBLE for any misuse or damage caused by this program. By using this software, you agree to use it only for legal, educational purposes.

---

## 🆘 Troubleshooting

### Common Issues

#### 1. **ModuleNotFoundError: No module named 'pynput'**
```bash
pip install pynput
```
#### 2. **Permission Denied Error**
```bash
# Linux/macOS
sudo python main.py
# Windows: Run as Administrator
```
#### 3. **SMTP Authentication Error**

- Enable 2-Factor Authentication
- Use App Password instead of regular password
- Check Gmail security settings
    

#### 4. **Firewall Blocking SMTP**
- Ensure port 465 is open
- Check firewall settings
- Try alternative SMTP servers

---

## 📊 Performance
- **Memory Usage**: ~20-30 MB
- **CPU Usage**: < 1% (idle)
- **Network**: Only during email sending (every 30 seconds by default)
- **Log Size**: Automatically managed (default max: 10,000 characters)

---

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Basic keylogging functionality
- Email reporting
- Signal handling
- Configuration via environment variables

---

## 📚 Educational Resources

### Learning Objectives

- Understanding system hooks and event listeners
- Implementing secure SMTP communication
- Working with threads and timers
- Handling OS signals
- Writing clean, documented code

### Related Topics

- System Security
- Ethical Hacking
- Network Programming
- Python Threading
- Event-Driven Programming

---

## 📄 License

This project is licensed under the MIT License.
```text
MIT License
Copyright (c) 2024 JeddahSec
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## ⭐ Support

If you find this project educational and helpful, please:
- Star the repository ⭐
- Share with fellow learners
- Contribute improvements
- Report issues responsibly

---

## 📧 Contact

- **GitHub**: [jeddahsec/tools](https://github.com/jeddahsec/tools)
- **Issues**: [Create an issue](https://github.com/jeddahsec/tools/issues)

---

## 🙏 Acknowledgments

- [pynput](https://github.com/moses-palmer/pynput) - Keyboard monitoring library
- [termcolor](https://github.com/termcolor/termcolor) - Terminal coloring
- Python Software Foundation
- Information Security Community
