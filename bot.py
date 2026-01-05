import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for Google Cloud Run
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Structured logging format for Cloud Logging
class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'severity': record.levelname,
            'message': record.getMessage(),
            'component': record.name,
            'timestamp': self.formatTime(record, self.datefmt),
        }

        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_obj['user_id'] = record.user_id
        if hasattr(record, 'guild_id'):
            log_obj['guild_id'] = record.guild_id
        if hasattr(record, 'command'):
            log_obj['command'] = record.command

        return json.dumps(log_obj)

# Determine if running in Cloud Run
IS_CLOUD_RUN = os.getenv('K_SERVICE') is not None

if IS_CLOUD_RUN:
    # Use structured JSON logging for Cloud Run
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        handlers=[handler]
    )
else:
    # Use human-readable logging for local development
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger('discord_bot')
logger.info(f"Logging configured. Environment: {'Cloud Run' if IS_CLOUD_RUN else 'Local'}")

# Configuration
TOKEN = os.getenv('DISCORD_TOKEN')
DAILY_MESSAGE_LIMIT = int(os.getenv('DAILY_MESSAGE_LIMIT', 10))

logger.info(f"Bot starting with configuration: DAILY_MESSAGE_LIMIT={DAILY_MESSAGE_LIMIT}")

# Data directory setup
DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)
USER_DATA_FILE = DATA_DIR / 'user_data.json'
HISTORY_FILE = DATA_DIR / 'chat_history.json'

class AskBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )

        self.user_data = {}
        self.chat_history = {}

    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Bot setup hook called")
        await self.load_data()
        logger.info("Syncing slash commands...")
        await self.tree.sync()
        logger.info("Slash commands synced successfully!")

    async def load_data(self):
        """Load user data and chat history from files"""
        try:
            if USER_DATA_FILE.exists():
                with open(USER_DATA_FILE, 'r') as f:
                    self.user_data = json.load(f)
                logger.info(f"Loaded data for {len(self.user_data)} users")

            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, 'r') as f:
                    self.chat_history = json.load(f)
                logger.info(f"Loaded history for {len(self.chat_history)} users")

            logger.info("Data loaded successfully!")
        except Exception as e:
            logger.error(f"Error loading data: {e}", exc_info=True)
            self.user_data = {}
            self.chat_history = {}

    async def save_data(self):
        """Save user data and chat history to files"""
        try:
            with open(USER_DATA_FILE, 'w') as f:
                json.dump(self.user_data, f, indent=2)

            with open(HISTORY_FILE, 'w') as f:
                json.dump(self.chat_history, f, indent=2)

            logger.debug("Data saved successfully")

        except Exception as e:
            logger.error(f"Error saving data: {e}", exc_info=True)

    def check_rate_limit(self, user_id: str) -> tuple[bool, int]:
        """
        Check if user has exceeded daily message limit
        Returns: (can_send: bool, remaining: int)
        """
        today = datetime.now().strftime('%Y-%m-%d')
        user_id_str = str(user_id)

        if user_id_str not in self.user_data:
            self.user_data[user_id_str] = {
                'last_reset': today,
                'message_count': 0,
                'total_messages': 0
            }

        user = self.user_data[user_id_str]

        # Reset count if it's a new day
        if user['last_reset'] != today:
            user['last_reset'] = today
            user['message_count'] = 0

        remaining = DAILY_MESSAGE_LIMIT - user['message_count']
        can_send = user['message_count'] < DAILY_MESSAGE_LIMIT

        return can_send, remaining

    def increment_message_count(self, user_id: str):
        """Increment user's message count"""
        user_id_str = str(user_id)
        if user_id_str in self.user_data:
            self.user_data[user_id_str]['message_count'] += 1
            self.user_data[user_id_str]['total_messages'] += 1

    def add_to_history(self, user_id: str, username: str, question: str, response: str):
        """Add interaction to chat history"""
        user_id_str = str(user_id)
        if user_id_str not in self.chat_history:
            self.chat_history[user_id_str] = []

        self.chat_history[user_id_str].append({
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'question': question,
            'response': response
        })

        # Keep only last 50 interactions per user
        if len(self.chat_history[user_id_str]) > 50:
            self.chat_history[user_id_str] = self.chat_history[user_id_str][-50:]

# Create bot instance
bot = AskBot()

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    logger.info(f'Bot is ready! Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} guild(s)')
    logger.info(f'Bot user: {bot.user.name}#{bot.user.discriminator}')
    logger.info('------')

@bot.tree.command(name="ask", description="Ask a question to the bot")
@app_commands.describe(question="Your question")
async def ask(interaction: discord.Interaction, question: str):
    """Ask command - main chat functionality"""
    user_id = interaction.user.id
    username = interaction.user.name

    logger.info(f"User {username} (ID: {user_id}) asked: {question[:100]}...")

    # Check rate limit
    can_send, remaining = bot.check_rate_limit(user_id)

    if not can_send:
        logger.warning(f"User {username} (ID: {user_id}) exceeded daily limit")
        embed = discord.Embed(
            title="⚠️ Daily Limit Reached",
            description=f"You've reached your daily limit of {DAILY_MESSAGE_LIMIT} messages. Please try again tomorrow!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Defer response as we might take a moment to process
    await interaction.response.defer()

    # Increment count
    bot.increment_message_count(user_id)
    logger.info(f"User {username} has {remaining - 1} messages remaining")

    # Generate a simple response (you can integrate with an AI API here)
    response = f"Thank you for your question: '{question}'\n\n"
    response += "This is a simple response. You can integrate this bot with OpenAI, Anthropic, or other AI APIs for intelligent responses.\n\n"
    response += f"You have {remaining - 1} messages remaining today."

    # Add to history
    bot.add_to_history(user_id, username, question, response)

    # Save data
    await bot.save_data()

    # Create embed response
    embed = discord.Embed(
        title="💬 Response",
        description=response,
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Asked by {username}")

    await interaction.followup.send(embed=embed)
    logger.info(f"Response sent to {username} (ID: {user_id})")

@bot.tree.command(name="info", description="Get information about the bot")
async def info(interaction: discord.Interaction):
    """Info command - displays bot information"""
    logger.info(f"User {interaction.user.name} requested bot info")

    embed = discord.Embed(
        title="ℹ️ Bot Information",
        description="Ask-100x Discord Bot - A simple chat bot with rate limiting",
        color=discord.Color.green()
    )

    embed.add_field(
        name="Features",
        value="• `/ask` - Ask questions\n• `/stats` - View your statistics\n• `/history` - View your chat history\n• `/limit` - Check your daily limit\n• `/info` - Bot information",
        inline=False
    )

    embed.add_field(
        name="Rate Limit",
        value=f"{DAILY_MESSAGE_LIMIT} messages per day",
        inline=True
    )

    embed.add_field(
        name="Servers",
        value=f"{len(bot.guilds)} server(s)",
        inline=True
    )

    embed.set_footer(text=f"Bot by {bot.user.name}")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="stats", description="View your usage statistics")
async def stats(interaction: discord.Interaction):
    """Stats command - displays user statistics"""
    user_id = str(interaction.user.id)
    logger.info(f"User {interaction.user.name} requested stats")

    if user_id not in bot.user_data:
        embed = discord.Embed(
            title="📊 Your Statistics",
            description="You haven't used the bot yet. Use `/ask` to get started!",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    user = bot.user_data[user_id]

    embed = discord.Embed(
        title="📊 Your Statistics",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="Today's Messages",
        value=f"{user['message_count']}/{DAILY_MESSAGE_LIMIT}",
        inline=True
    )

    embed.add_field(
        name="Total Messages",
        value=user['total_messages'],
        inline=True
    )

    embed.add_field(
        name="Last Reset",
        value=user['last_reset'],
        inline=True
    )

    # Calculate remaining
    remaining = DAILY_MESSAGE_LIMIT - user['message_count']
    embed.add_field(
        name="Remaining Today",
        value=remaining,
        inline=True
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="history", description="View your recent chat history")
@app_commands.describe(count="Number of recent messages to show (default: 5)")
async def history(interaction: discord.Interaction, count: int = 5):
    """History command - displays user's chat history"""
    user_id = str(interaction.user.id)

    if user_id not in bot.chat_history or not bot.chat_history[user_id]:
        embed = discord.Embed(
            title="📜 Chat History",
            description="You don't have any chat history yet. Use `/ask` to start chatting!",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Limit count to reasonable range
    count = max(1, min(count, 10))

    history = bot.chat_history[user_id][-count:]

    embed = discord.Embed(
        title=f"📜 Your Recent Chat History (Last {len(history)})",
        color=discord.Color.blue()
    )

    for i, entry in enumerate(reversed(history), 1):
        timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M')
        embed.add_field(
            name=f"{i}. {timestamp}",
            value=f"**Q:** {entry['question'][:100]}{'...' if len(entry['question']) > 100 else ''}",
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="limit", description="Check your daily message limit")
async def limit(interaction: discord.Interaction):
    """Limit command - displays user's rate limit status"""
    user_id = interaction.user.id

    can_send, remaining = bot.check_rate_limit(user_id)

    # Calculate progress bar
    used = DAILY_MESSAGE_LIMIT - remaining
    progress = int((used / DAILY_MESSAGE_LIMIT) * 10)
    progress_bar = "█" * progress + "░" * (10 - progress)

    embed = discord.Embed(
        title="⏱️ Daily Message Limit",
        color=discord.Color.blue() if can_send else discord.Color.red()
    )

    embed.add_field(
        name="Usage",
        value=f"{progress_bar} {used}/{DAILY_MESSAGE_LIMIT}",
        inline=False
    )

    embed.add_field(
        name="Remaining",
        value=f"{remaining} message{'s' if remaining != 1 else ''} left today",
        inline=True
    )

    if not can_send:
        # Calculate time until reset (midnight)
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        midnight = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
        time_until_reset = midnight - now
        hours = int(time_until_reset.total_seconds() // 3600)
        minutes = int((time_until_reset.total_seconds() % 3600) // 60)

        embed.add_field(
            name="Reset In",
            value=f"{hours}h {minutes}m",
            inline=True
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    """Help command - displays all available commands"""
    embed = discord.Embed(
        title="🤖 Bot Commands Help",
        description="Here are all available commands:",
        color=discord.Color.gold()
    )

    commands_list = [
        ("**/ask <question>**", "Ask a question to the bot"),
        ("**/info**", "Get information about the bot"),
        ("**/stats**", "View your usage statistics"),
        ("**/history [count]**", "View your recent chat history (default: 5)"),
        ("**/limit**", "Check your daily message limit"),
        ("**/help**", "Show this help message"),
    ]

    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)

    embed.set_footer(text=f"Daily limit: {DAILY_MESSAGE_LIMIT} messages per user")

    await interaction.response.send_message(embed=embed, ephemeral=True)

# Error handling
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Global error handler for slash commands"""
    if isinstance(error, app_commands.CommandOnCooldown):
        logger.warning(f"Command cooldown for user {interaction.user.name}: {error.retry_after:.2f}s")
        await interaction.response.send_message(
            f"⏱️ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
            ephemeral=True
        )
    elif isinstance(error, app_commands.MissingPermissions):
        logger.warning(f"Permission denied for user {interaction.user.name}")
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.",
            ephemeral=True
        )
    else:
        logger.error(f"Command error: {error}", exc_info=True)
        await interaction.response.send_message(
            "❌ An error occurred while processing your command.",
            ephemeral=True
        )

# Run the bot
if __name__ == "__main__":
    if not TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with your bot token.")
        exit(1)

    try:
        logger.info("Starting Discord bot...")
        bot.run(TOKEN, log_handler=None)  # We're using our own logging
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        exit(1)
