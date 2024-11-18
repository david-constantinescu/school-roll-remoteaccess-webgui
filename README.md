# School Roll Remote Access Web GUI

This project provides a server with a user-friendly web interface to manage and edit school grades from the **[School Roll](https://github.com/david-constantinescu/school-roll)**, with a simple HTML, CSS, and JavaScript frontend. It allows users (teachers or administrators) to remotely access and update the school roll data.

## Features
- **Web Interface**: Easily manage and edit student grades through a responsive, browser-based interface.
- **Server-Side Backend**: Powered by Flask for easy deployment and scalability.
- **Integration**: Connects directly with the [School Roll](https://github.com/david-constantinescu/school-roll) system to modify grade data.

## Installation

1. Download the latest release by navigating to the **Releases** tab and downloading the linked ZIP file.
2. Extract the contents of the ZIP file to a directory of your choice.
3. Install Flask using `pip`:
   ```bash
   pip install flask

4.	After installation, you can run the server by navigating to the project folder and executing:

     ```bash
    python server.py

## Alternative instalation method

Alternatively, download a precompiled binary from the releases tab. Windows binaries are available and plans for a macOS on ARM binary are on the way.

## Usage

Once the server is running, open your browser and go to http://localhost:1509 or https://127.0.0.1:1509 to access the web interface. You’ll be able to securely manage and update grades from the school roll.
