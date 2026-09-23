# ChatGPT Delivery XL Bridge

Generic Windows edge bridge for large inbound Telegram files.

- Logs in as the existing bot through MTProto using API ID/API Hash + bot token.
- Ignores normal files <=18 MB (Apps Script cloud path handles them).
- Downloads larger files to disk, never full-file RAM.
- Splits into 6 MB parts.
- POSTs parts to the V9.0.1 Apps Script Web App.
- HMAC-SHA256 authentication using the bot token; SHA-256 per part.
- Stores secrets locally with Windows DPAPI.
- Adds itself to the user's Startup folder after first configuration.
- No credentials are committed to GitHub.
