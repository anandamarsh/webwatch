# WebWatch

A browser extension to track and analyze web browsing activity.

## Features

- Track web page visits
- Store full HTML content of visited pages
- Block distracting websites
- Analyze browsing habits

## Components

- Chrome Extension: Tracks page visits and sends data to the server
- Python Flask API: Receives and stores visit data
- SQLite Database: Stores visit history and blocklist

## Installation

### Server

1. Clone this repository
2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the server:
   ```
   python run.py
   ```

### Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `chrome` directory from this repository
4. Configure the server URL in the extension options

## API Documentation

See [API.md](API.md) for detailed API documentation.

## License

MIT
