# Discord Server Reload Bot

This project is a Discord bot that monitors server statuses and allows users to reload servers or refresh the status using interactive buttons. The bot updates the server status every 30 minutes and posts it in a specified Discord channel.

## Features

- **Automated Status Updates**: Posts server statuses to a Discord channel every 30 minutes.
- **Interactive Controls**:
  - **Reload Servers**: Provides buttons to reload individual servers.
  - **Refresh Status**: Offers a button to manually refresh the server statuses.
- **Clean Channel Management**: Edits the last status message instead of sending new ones to keep the channel uncluttered.

## Prerequisites

- **Python 3.8 or higher**
- **Discord Account**: Access to a Discord server where you can add bots.
- **Service Credentials**: Valid `USERNAME` and `PASSWORD` for the service you are monitoring.
- **Service Link**: The `SERVICE_LINK` URL of the service dashboard or API.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/earlingeling/discord-reload.git
cd discord-reload
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory and add the following variables:

```
DISCORD_TOKEN=your_discord_bot_token
CHANNEL_ID=your_discord_channel_id
USERNAME=your_service_username
PASSWORD=your_service_password
SERVICE_LINK=your_service_link
```

Alternatively, use set the environment variables directly

### 4. Run the Bot

```bash
python app.py
```

## Usage

Once the bot is running, it will automatically post server statuses to the specified Discord channel every 30 minutes. Use the interactive buttons to reload servers or refresh the status manually.

## Contributing

Feel free to submit issues or pull requests if you have any improvements or bug fixes.