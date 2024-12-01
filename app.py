import datetime
import os
import asyncio
import discord
from discord.ext import commands, tasks
from discord import Embed, ButtonStyle
from discord.ui import View, Button
from functions import login, get_combined_stats, reload_server
from session_handler import load_session
from logger_config import logger

# Load environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Load or create a session
session = load_session()

# Global variable to keep track of the status message
status_message = None

@bot.event
async def on_ready():
    global status_message
    logger.info(f'Logged in as {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    # Fetch the last message sent by the bot
    async for message in channel.history(limit=50):
        if message.author == bot.user:
            status_message = message
            break
    # Start the background task
    post_status.start()

@tasks.loop(minutes=30)
async def post_status():
    global status_message
    channel = bot.get_channel(CHANNEL_ID)
    try:
        # Ensure session is valid
        try:
            stats = get_combined_stats(session)
        except Exception:
            logger.info('Session expired, logging in again.')
            login(session)
            stats = get_combined_stats(session)
        # Create an embed message
        embed = Embed(title='Server Status')
        for server in stats:
            embed.add_field(
                name=f"{server['name']}",
                value=(
                    f"Open Connections: {server['open_connections']}\n"
                    f"Total Streams: {server['total_streams']}\n"
                    f"Running Streams: {server['total_running_streams']}\n"
                    f"Down Streams: {server['down_streams']}\n"
                    f"Uptime: {server['uptime']}"
                ),
                inline=False
            )
        # Add a "last updated" field with the current time
        embed.set_footer(text='Last Updated: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Create buttons for each server
        view = View()
        for server in stats:
            button = Button(
                label=f"Reload {server['name']}",
                style=ButtonStyle.primary,
                custom_id=f"reload_{server['id']}"
            )
            view.add_item(button)
        # Add a refresh status button
        refresh_button = Button(
            label="Refresh Status",
            style=ButtonStyle.secondary,
            custom_id="refresh_status"
        )
        view.add_item(refresh_button)
        # Edit the existing message or send a new one
        if status_message is None:
            status_message = await channel.send(embed=embed, view=view)
        else:
            await status_message.edit(embed=embed, view=view)
    except Exception as e:
        logger.error(f'Error posting status: {e}')

@bot.event
async def on_interaction(interaction):
    custom_id = interaction.data.get('custom_id')
    if custom_id:
        if custom_id.startswith('reload_'):
            server_id = custom_id.split('_')[1]
            await interaction.response.send_message('Reloading...', ephemeral=True)
            try:
                result = reload_server(session, server_id)
                await post_status()
                await interaction.followup.send(f'Server {server_id} reloaded successfully.', ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f'Error reloading server {server_id}: {e}', ephemeral=True)
        elif custom_id == 'refresh_status':
            await interaction.response.send_message('Refreshing status...', ephemeral=True)
            try:
                await post_status()
                await interaction.followup.send('Status refreshed.', ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f'Error refreshing status: {e}', ephemeral=True)

# Run the bot
bot.run(DISCORD_TOKEN)