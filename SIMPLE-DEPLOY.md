# Simple Google Cloud Run Deployment (No Service Account)

This guide shows you how to deploy directly to Cloud Run using your personal Google Cloud credentials.

## Quick Deploy (5 Minutes)

### Step 1: Install Google Cloud SDK

If you don't have it installed:

**Linux/macOS:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install

### Step 2: Authenticate and Setup

```bash
# Login to Google Cloud
gcloud auth login

# Set your project (create one if needed)
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 3: Deploy with One Command

From your project directory:

```bash
# Deploy directly to Cloud Run
# Replace YOUR_DISCORD_TOKEN_HERE with your actual Discord token
gcloud run deploy discord-bot-ask-100x \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DISCORD_TOKEN=YOUR_DISCORD_TOKEN_HERE,DAILY_MESSAGE_LIMIT=10,LOG_LEVEL=INFO" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 1 \
  --min-instances 1 \
  --no-cpu-throttling
```

That's it! The command will:
1. Build your Docker image in the cloud
2. Push it to Container Registry
3. Deploy to Cloud Run
4. Start your bot

### Step 4: Verify Deployment

```bash
# Check if service is running
gcloud run services describe discord-bot-ask-100x \
  --platform managed \
  --region us-central1

# View logs
gcloud run services logs tail discord-bot-ask-100x \
  --platform managed \
  --region us-central1
```

## Alternative: Using Cloud Shell (No Installation Required)

You can deploy directly from your browser using Cloud Shell:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the **Cloud Shell** icon (>_) in the top right
3. Clone your repository or upload files
4. Run the deploy command above

### Upload Files to Cloud Shell

```bash
# In Cloud Shell
mkdir discord-bot
cd discord-bot

# Upload your files using the Cloud Shell upload button
# Or clone from GitHub:
git clone https://github.com/YOUR_USERNAME/Ask-100x.git
cd Ask-100x

# Deploy (replace YOUR_DISCORD_TOKEN_HERE with your actual token)
gcloud run deploy discord-bot-ask-100x \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DISCORD_TOKEN=YOUR_DISCORD_TOKEN_HERE,DAILY_MESSAGE_LIMIT=10,LOG_LEVEL=INFO" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 1 \
  --min-instances 1 \
  --no-cpu-throttling
```

## Update Bot (Redeploy)

To update your bot after making changes:

```bash
# Just run the deploy command again
gcloud run deploy discord-bot-ask-100x \
  --source . \
  --platform managed \
  --region us-central1
```

It will rebuild and redeploy automatically.

## View Logs

### Real-time Logs

```bash
gcloud run services logs tail discord-bot-ask-100x \
  --platform managed \
  --region us-central1
```

### Recent Logs

```bash
gcloud run services logs read discord-bot-ask-100x \
  --platform managed \
  --region us-central1 \
  --limit 100
```

### View in Console

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click on **discord-bot-ask-100x**
3. Click **LOGS** tab

## Change Environment Variables

```bash
# Update any environment variable
gcloud run services update discord-bot-ask-100x \
  --platform managed \
  --region us-central1 \
  --set-env-vars "DAILY_MESSAGE_LIMIT=20"

# Or update the Discord token
gcloud run services update discord-bot-ask-100x \
  --platform managed \
  --region us-central1 \
  --set-env-vars "DISCORD_TOKEN=your_new_token"
```

## Stop/Delete Service

```bash
# Delete the service (stops billing)
gcloud run services delete discord-bot-ask-100x \
  --platform managed \
  --region us-central1
```

## Troubleshooting

### "Permission Denied" Error

```bash
# Make sure you're authenticated
gcloud auth login

# Set the correct project
gcloud config set project YOUR_PROJECT_ID
```

### "API Not Enabled" Error

```bash
# Enable the required API
gcloud services enable run.googleapis.com
```

### Check Service Status

```bash
# Get service details
gcloud run services describe discord-bot-ask-100x \
  --platform managed \
  --region us-central1
```

### View All Your Services

```bash
gcloud run services list
```

## Cost

With min-instances=1 (always running):
- **Estimated cost**: $15-25/month
- Includes: CPU, memory, and networking

To reduce costs, you can remove `--min-instances 1` to scale to zero when idle, but the bot won't be instantly available.

## Regions

Available regions (choose the closest to you):

- `us-central1` (Iowa)
- `us-east1` (South Carolina)
- `us-west1` (Oregon)
- `europe-west1` (Belgium)
- `asia-east1` (Taiwan)
- `asia-northeast1` (Tokyo)

Change `--region us-central1` to your preferred region.

## Next Steps

1. Your bot is now running 24/7 on Cloud Run
2. Monitor logs to ensure it's working
3. Test commands in your Discord server
4. Update anytime by running the deploy command again

No GitHub Actions, no service accounts, no complexity! 🚀
