# Ask-100x Discord Bot

A Discord bot built with Python async that allows users to ask questions with a daily rate limit. Users can send up to 10 messages per day.

## Features

- ✅ **Async/await** - Built with modern Python async
- 💬 **Chat functionality** - `/ask` command for questions
- 📊 **Statistics tracking** - Track user message counts and stats
- 📜 **Chat history** - View your recent interactions
- ⏱️ **Rate limiting** - 10 messages per user per day
- 📁 **Data persistence** - User data saved to JSON files
- 🎨 **Rich embeds** - Beautiful Discord embed responses

## Commands

| Command | Description |
|---------|-------------|
| `/ask <question>` | Ask a question to the bot |
| `/info` | Get information about the bot |
| `/stats` | View your usage statistics |
| `/history [count]` | View your recent chat history (default: 5) |
| `/limit` | Check your daily message limit |
| `/help` | Show all available commands |

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- A Discord Bot Token ([How to get one](#getting-a-discord-bot-token))

### 2. Installation

Clone the repository:
```bash
git clone <your-repo-url>
cd Ask-100x
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Or using a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit the `.env` file and add your Discord bot token:
```env
DISCORD_TOKEN=your_discord_bot_token_here
DAILY_MESSAGE_LIMIT=10
```

### 4. Run the Bot

```bash
python bot.py
```

You should see:
```
Bot is ready! Logged in as YourBotName (ID: ...)
Connected to X guild(s)
Slash commands synced!
```

## Getting a Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot"
5. Under the TOKEN section, click "Reset Token" and copy it
6. **IMPORTANT**: Enable these Privileged Gateway Intents:
   - Message Content Intent
   - Server Members Intent
7. Go to OAuth2 → URL Generator
8. Select scopes: `bot` and `applications.commands`
9. Select bot permissions:
   - Send Messages
   - Embed Links
   - Read Message History
   - Use Slash Commands
10. Copy the generated URL and open it in your browser to invite the bot

## Project Structure

```
Ask-100x/
├── bot.py              # Main bot file
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
├── .env.example       # Environment template
├── .gitignore         # Git ignore file
├── README.md          # This file
└── data/              # Created automatically
    ├── user_data.json    # User statistics
    └── chat_history.json # Chat history
```

## Rate Limiting

- Each user can send **10 messages per day** (configurable)
- Limit resets at midnight (00:00)
- Users are notified when they reach their limit
- Use `/limit` to check remaining messages

## Data Storage

User data is stored locally in JSON files:

- `data/user_data.json` - Stores user message counts and statistics
- `data/chat_history.json` - Stores recent chat interactions (last 50 per user)

## Customization

### Change Daily Limit

Edit the `.env` file:
```env
DAILY_MESSAGE_LIMIT=20  # Change to desired limit
```

### Integrate with AI APIs

To make the bot respond intelligently, you can integrate with:
- **OpenAI API** - For ChatGPT responses
- **Anthropic API** - For Claude responses
- **Google Gemini** - For Gemini responses

Example integration point in `bot.py` (line ~150):
```python
# Replace this simple response with AI API call
response = f"Thank you for your question: '{question}'\n\n"
response += "This is a simple response..."
```

## Troubleshooting

### Bot doesn't respond to commands
- Make sure slash commands are synced (wait a few minutes after first run)
- Check that the bot has proper permissions in your server
- Verify the bot is online (green status)

### Rate limit not working
- Check that the `data/` directory exists and is writable
- Verify the `.env` file has correct settings

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

## Development

### Adding New Commands

Add a new slash command:
```python
@bot.tree.command(name="mycommand", description="My command description")
async def my_command(interaction: discord.Interaction):
    await interaction.response.send_message("Hello!")
```

### Testing

Run the bot in development mode and test commands in your Discord server.

## Deployment to Google Cloud Run

This bot can be deployed to Google Cloud Run for 24/7 availability with automatic scaling and logging.

### Quick Deploy

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

#### Prerequisites
- Google Cloud Platform account
- GitHub repository
- Discord bot token

#### Setup GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret | Description |
|--------|-------------|
| `GCP_PROJECT_ID` | Your GCP Project ID |
| `GCP_SA_KEY` | Service Account JSON Key |
| `DISCORD_TOKEN` | Your Discord bot token |

#### Auto-Deploy

Push to `main` or `master` branch to automatically deploy:

```bash
git add .
git commit -m "Deploy to Cloud Run"
git push origin main
```

The GitHub Actions workflow will:
1. Build Docker image
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Configure logging and monitoring

#### View Logs

```bash
# View logs in real-time
gcloud run services logs tail discord-bot-ask-100x \
  --platform managed \
  --region us-central1
```

#### Features
- ✅ Automatic deployment via GitHub Actions
- ✅ Comprehensive logging with Google Cloud Logging
- ✅ Always-on (min-instances=1)
- ✅ Health checks and auto-restart
- ✅ Environment variable management

For complete deployment guide, see [DEPLOYMENT.md](DEPLOYMENT.md).

## License

MIT License - Feel free to use and modify!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the [Discord.py documentation](https://discordpy.readthedocs.io/)
