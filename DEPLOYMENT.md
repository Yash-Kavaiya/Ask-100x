# Google Cloud Run Deployment Guide

This guide will help you deploy the Discord bot to Google Cloud Run with automated CI/CD using GitHub Actions.

## Prerequisites

- Google Cloud Platform account
- GitHub repository
- Discord bot token
- `gcloud` CLI installed (for local deployment)

## Setup Steps

### 1. Google Cloud Setup

#### Create a GCP Project

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Create a new project (or use existing)
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID
```

#### Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Build API (optional, for building in cloud)
gcloud services enable cloudbuild.googleapis.com

# Enable Cloud Logging API
gcloud services enable logging.googleapis.com
```

#### Create a Service Account

```bash
# Create service account
gcloud iam service-accounts create github-actions \
    --description="Service account for GitHub Actions" \
    --display-name="GitHub Actions"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create key.json \
    --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com
```

### 2. GitHub Secrets Setup

Add the following secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret Name | Description | Value |
|------------|-------------|-------|
| `GCP_PROJECT_ID` | Your GCP Project ID | `your-project-id` |
| `GCP_SA_KEY` | Service Account JSON Key | Contents of `key.json` |
| `DISCORD_TOKEN` | Discord Bot Token | Your Discord bot token |

#### How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret listed above

### 3. Manual Deployment (Optional)

If you want to deploy manually before setting up CI/CD:

```bash
# Build the Docker image
docker build -t gcr.io/$PROJECT_ID/discord-bot-ask-100x:latest .

# Authenticate Docker with GCR
gcloud auth configure-docker

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/discord-bot-ask-100x:latest

# Deploy to Cloud Run
gcloud run deploy discord-bot-ask-100x \
  --image gcr.io/$PROJECT_ID/discord-bot-ask-100x:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DISCORD_TOKEN=your_token_here,DAILY_MESSAGE_LIMIT=10,LOG_LEVEL=INFO" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 1 \
  --min-instances 1 \
  --no-cpu-throttling
```

### 4. Automated Deployment with GitHub Actions

Once you've set up the GitHub secrets, the bot will automatically deploy when you push to the `main` or `master` branch.

#### Workflow File

The workflow is defined in `.github/workflows/deploy-cloudrun.yml` and includes:

- ✅ Checkout code
- ✅ Authenticate with Google Cloud
- ✅ Build Docker image
- ✅ Push to Container Registry
- ✅ Deploy to Cloud Run
- ✅ Verify deployment

#### Trigger Deployment

```bash
# Commit and push changes
git add .
git commit -m "Deploy bot to Cloud Run"
git push origin main
```

## Monitoring and Logging

### View Logs in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Cloud Run** → Select your service
3. Click **LOGS** tab

### View Logs with gcloud CLI

```bash
# View recent logs
gcloud run services logs read discord-bot-ask-100x \
  --platform managed \
  --region us-central1 \
  --limit 100

# Follow logs in real-time
gcloud run services logs tail discord-bot-ask-100x \
  --platform managed \
  --region us-central1
```

### Log Levels

The bot supports different log levels via the `LOG_LEVEL` environment variable:

- `DEBUG` - Detailed information, typically of interest only when diagnosing problems
- `INFO` - Confirmation that things are working as expected (default)
- `WARNING` - An indication that something unexpected happened
- `ERROR` - A more serious problem

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DISCORD_TOKEN` | Discord bot token | - | Yes |
| `DAILY_MESSAGE_LIMIT` | Max messages per user per day | 10 | No |
| `LOG_LEVEL` | Logging level | INFO | No |

### Update Environment Variables

```bash
gcloud run services update discord-bot-ask-100x \
  --platform managed \
  --region us-central1 \
  --set-env-vars "DAILY_MESSAGE_LIMIT=20,LOG_LEVEL=DEBUG"
```

## Scaling Configuration

The current setup uses:
- **Min instances**: 1 (always running)
- **Max instances**: 1 (single instance)
- **CPU**: 1 vCPU
- **Memory**: 512 Mi
- **CPU throttling**: Disabled
- **Timeout**: 3600 seconds (1 hour)

### Why Always Running?

Discord bots need to maintain a persistent WebSocket connection. Setting `min-instances=1` ensures the bot is always available.

### Adjust Scaling

```bash
# Increase memory
gcloud run services update discord-bot-ask-100x \
  --platform managed \
  --region us-central1 \
  --memory 1Gi

# Increase CPU
gcloud run services update discord-bot-ask-100x \
  --platform managed \
  --region us-central1 \
  --cpu 2
```

## Cost Estimation

With the current configuration (always running, 512 Mi memory, 1 vCPU):

- **Approximate cost**: $15-25/month
- Includes: CPU allocation, memory, and networking

### Cost Optimization

To reduce costs:
1. Use smaller memory allocation (256 Mi minimum)
2. Consider using Compute Engine for long-running bots (may be cheaper)
3. Monitor usage with Google Cloud Billing reports

## Troubleshooting

### Bot Not Responding

```bash
# Check if service is running
gcloud run services describe discord-bot-ask-100x \
  --platform managed \
  --region us-central1

# Check logs for errors
gcloud run services logs tail discord-bot-ask-100x \
  --platform managed \
  --region us-central1
```

### Deployment Failures

1. Check GitHub Actions logs
2. Verify all secrets are set correctly
3. Ensure service account has proper permissions
4. Check GCP quotas and billing

### Connection Issues

```bash
# Verify Discord token is set
gcloud run services describe discord-bot-ask-100x \
  --platform managed \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

## Health Checks

The Docker image includes a health check that verifies the bot process is running. Cloud Run will automatically restart the container if the health check fails.

## Data Persistence

By default, data is stored in `/app/data` within the container. This data is **not persistent** across deployments.

### Options for Persistent Storage

1. **Cloud Storage** - Mount a bucket for file storage
2. **Firestore** - Use a database for structured data
3. **Cloud SQL** - For relational data

To implement persistent storage, modify `bot.py` to use one of these services instead of local JSON files.

## Updating the Bot

1. Make changes to your code
2. Commit and push to GitHub
3. GitHub Actions will automatically rebuild and redeploy
4. Monitor the deployment in GitHub Actions tab

## Rollback

```bash
# List revisions
gcloud run revisions list \
  --service discord-bot-ask-100x \
  --platform managed \
  --region us-central1

# Rollback to a specific revision
gcloud run services update-traffic discord-bot-ask-100x \
  --platform managed \
  --region us-central1 \
  --to-revisions REVISION_NAME=100
```

## Security Best Practices

1. ✅ Never commit `.env` files or secrets
2. ✅ Use GitHub Secrets for sensitive data
3. ✅ Regularly rotate service account keys
4. ✅ Use least-privilege IAM roles
5. ✅ Enable Cloud Armor for DDoS protection
6. ✅ Monitor logs for suspicious activity

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cloud Logging Documentation](https://cloud.google.com/logging/docs)
