# C2 (Command and Control) Project

A command and control framework demonstrating secure client-server communications.

## Project Overview

This project implements a secure C2 (Command and Control) framework with the following key components:

- Interactive C2 server for command execution
- Resilient remote agent with auto-reconnect capabilities
- Line-delimited JSON protocol over TCP
- Built-in safe demo commands
- Screenshot functionality
- Modular and security-focused design

## Key Features

- **Secure Communication**: Line-delimited JSON protocol over TCP
- **Resilient Agent**: Auto-reconnects if server unavailable
- **Safe Demo Commands**:
    - echo - Safe message echo
    - screenshot - Screenshot capture (Base64 encoded)
    - rickroll - Educational demo
    - exit - Graceful shutdown
- **Safety-First Design**: Minimal attack surface, controlled execution

## Components

- server.py - C2 server implementation
- agent.py - Remote agent
- take_screenshot.py - Screenshot utility
- get_rick_roll.py - Demo helper
- command_executor.py - Safe subprocess wrapper

## Authors

- Raziel Maymon

## Security Notice

This project is for educational purposes only. Always follow security best practices.
