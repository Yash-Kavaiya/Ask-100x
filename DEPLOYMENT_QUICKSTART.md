# Quick Start: Deploy to Google Cloud Run (5 Minutes)

This is a simplified guide to get your Discord bot deployed quickly. For detailed information, see [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md).

## Prerequisites

- Google Cloud account with billing enabled
- GitHub repository
- Discord bot token (from Discord Developer Portal)
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed

## Step 1: Run Setup Script (2 minutes)

```bash
# Make the script executable
chmod +x setup-gcp.sh

# Run the setup script
./setup-gcp.sh
```

Follow the prompts:
1. Enter your GCP Project ID
2. Enter your GitHub username/organization
3. Enter your repository name (e.g., "Ask-100x")

The script will:
- Enable required Google Cloud APIs
- Create Artifact Registry repository
- Set up Workload Identity Federation
- Configure permissions

At the end, you'll get 4 secrets to add to GitHub.

## Step 2: Add Secrets to GitHub (1 minute)

Go to your GitHub repository:
**Settings → Secrets and variables → Actions → New repository secret**

Add these 4 secrets (values provided by setup script):

1. **GCP_PROJECT_ID**: Your Google Cloud project ID
2. **WIF_PROVIDER**: Workload Identity Provider (long string starting with "projects/...")
3. **WIF_SERVICE_ACCOUNT**: Service account email (github-actions-bot@...)
4. **DISCORD_TOKEN**: Your Discord bot token

## Step 3: Deploy (2 minutes)

```bash
# Push your code to trigger deployment
git add .
git commit -m "Deploy to Cloud Run"
git push origin main
```

GitHub Actions will automatically:
1. Build Docker image
2. Push to Google Artifact Registry
3. Deploy to Cloud Run
4. Start your bot

Monitor the deployment:
- Go to GitHub → Actions tab
- Watch the deployment progress

## Step 4: Verify Bot is Running

### Check GitHub Actions
- Go to your repository's Actions tab
- Look for green checkmarks

### Check Cloud Console
```bash
gcloud run services describe discord-bot-ask-100x \
  --platform managed \
  --region us-central1
```

### Test in Discord
```
/help
/ask Hello, are you working?
/stats
```

## View Logs

```bash
# Real-time logs
gcloud run services logs tail discord-bot-ask-100x \
  --platform managed \
  --region us-central1

# Or view in Cloud Console
gcloud run services describe discord-bot-ask-100x \
  --platform managed \
  --region us-central1 \
  --format='value(status.url)'
```

## Troubleshooting

### "Authentication failed" in GitHub Actions
- Verify all 4 secrets are added correctly to GitHub
- Check secret names are exact (case-sensitive)

### "Permission denied" errors
- Re-run the setup script
- Make sure billing is enabled on your GCP project

### Bot not responding in Discord
- Check logs: `gcloud run services logs tail discord-bot-ask-100x --region us-central1`
- Verify DISCORD_TOKEN is correct in GitHub secrets
- Make sure bot has correct Discord permissions

## Cost

With current configuration (always-on, 512MB, 1 CPU):
- **Estimated cost**: $15-20/month
- **Logging**: ~$2/month for typical usage

To reduce costs (but have cold starts):
```bash
gcloud run services update discord-bot-ask-100x \
  --region us-central1 \
  --min-instances=0
```

## Update Bot

To deploy changes:
```bash
git add .
git commit -m "Update bot"
git push origin main
```

Deployment happens automatically via GitHub Actions.

## Key Features

- **No service account keys**: Uses Workload Identity Federation (secure!)
- **Automatic deployment**: Push to GitHub = automatic deploy
- **Comprehensive logging**: JSON structured logs in Cloud Logging
- **Always-on**: min-instances=1 keeps bot running 24/7
- **Auto-scaling**: Handles traffic spikes automatically

## Next Steps

- View detailed setup: [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md)
- Set up monitoring alerts
- Configure error notifications
- Add database for persistent storage

## Support

- GitHub Actions logs: Repository → Actions tab
- Cloud Run logs: `gcloud run services logs tail discord-bot-ask-100x --region us-central1`
- Cloud Console: https://console.cloud.google.com/run
