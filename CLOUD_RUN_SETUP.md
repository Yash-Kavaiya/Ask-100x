# Google Cloud Run Deployment Setup Guide

This guide will help you deploy your Discord bot to Google Cloud Run using GitHub Actions with **Workload Identity Federation** (no service account keys needed).

## Prerequisites

- Google Cloud Platform account
- GitHub repository
- Discord bot token
- gcloud CLI installed (for initial setup)

## Step 1: Set Up Google Cloud Project

### 1.1 Create or Select a Project

```bash
# Set your project ID (replace with your actual project ID)
export PROJECT_ID="your-project-id"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  iamcredentials.googleapis.com \
  logging.googleapis.com
```

### 1.2 Create Artifact Registry Repository

```bash
# Create a Docker repository in Artifact Registry
gcloud artifacts repositories create discord-bot-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Discord bot container images"
```

## Step 2: Configure Workload Identity Federation

This allows GitHub Actions to authenticate without service account keys.

### 2.1 Create Service Account

```bash
# Create a service account for GitHub Actions
gcloud iam service-accounts create github-actions-bot \
  --display-name="GitHub Actions Bot Deployer"

# Get the service account email
export SA_EMAIL="github-actions-bot@${PROJECT_ID}.iam.gserviceaccount.com"
```

### 2.2 Grant Required Permissions

```bash
# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

# Grant Artifact Registry Writer role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer"

# Grant Service Account User role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# Grant Logging Writer role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/logging.logWriter"
```

### 2.3 Create Workload Identity Pool

```bash
# Create Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Get the Workload Identity Pool ID
export WORKLOAD_IDENTITY_POOL_ID=$(gcloud iam workload-identity-pools describe "github-pool" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --format="value(name)")

echo "Workload Identity Pool ID: ${WORKLOAD_IDENTITY_POOL_ID}"
```

### 2.4 Create Workload Identity Provider

Replace `YOUR_GITHUB_ORG` and `YOUR_REPO_NAME` with your actual GitHub organization/username and repository name.

```bash
# Set your GitHub details
export GITHUB_ORG="YOUR_GITHUB_ORG"
export GITHUB_REPO="YOUR_REPO_NAME"

# Create OIDC provider for GitHub
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Get the Workload Identity Provider name
export WIF_PROVIDER=$(gcloud iam workload-identity-pools providers describe "github-provider" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)")

echo "Workload Identity Provider: ${WIF_PROVIDER}"
```

### 2.5 Allow GitHub to Impersonate Service Account

```bash
# Allow GitHub Actions from your repository to impersonate the service account
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_ID}/attribute.repository/${GITHUB_ORG}/${GITHUB_REPO}"
```

## Step 3: Configure GitHub Repository Secrets

Go to your GitHub repository: **Settings → Secrets and variables → Actions → New repository secret**

Add the following secrets:

### 3.1 GCP_PROJECT_ID
```
Value: your-project-id
```

### 3.2 WIF_PROVIDER
```
Value: [The output from step 2.4]
Format: projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider
```

To get this value again:
```bash
echo $WIF_PROVIDER
```

### 3.3 WIF_SERVICE_ACCOUNT
```
Value: github-actions-bot@your-project-id.iam.gserviceaccount.com
```

To get this value:
```bash
echo $SA_EMAIL
```

### 3.4 DISCORD_TOKEN
```
Value: [Your Discord bot token from Discord Developer Portal]
```

**WARNING**: Never commit this token to your repository!

## Step 4: Verify Setup

### 4.1 Check Your Secrets

You should have these 4 secrets in GitHub:
- `GCP_PROJECT_ID`
- `WIF_PROVIDER`
- `WIF_SERVICE_ACCOUNT`
- `DISCORD_TOKEN`

### 4.2 Print Configuration Summary

Run this script to verify your setup:

```bash
echo "=== Configuration Summary ==="
echo "Project ID: ${PROJECT_ID}"
echo "Service Account: ${SA_EMAIL}"
echo "Workload Identity Provider: ${WIF_PROVIDER}"
echo "GitHub Repo: ${GITHUB_ORG}/${GITHUB_REPO}"
echo ""
echo "Add these to GitHub Secrets:"
echo "GCP_PROJECT_ID: ${PROJECT_ID}"
echo "WIF_PROVIDER: ${WIF_PROVIDER}"
echo "WIF_SERVICE_ACCOUNT: ${SA_EMAIL}"
echo "DISCORD_TOKEN: [Your Discord token]"
```

## Step 5: Deploy

### 5.1 Push to GitHub

```bash
git add .
git commit -m "Set up Cloud Run deployment"
git push origin main
```

The GitHub Actions workflow will automatically:
1. Build your Docker image
2. Push to Artifact Registry
3. Deploy to Cloud Run
4. Configure logging

### 5.2 Monitor Deployment

Watch the deployment in GitHub:
- Go to **Actions** tab
- Click on the running workflow
- View the deployment logs

### 5.3 View Cloud Run Logs

```bash
# View real-time logs
gcloud run services logs tail discord-bot-ask-100x \
  --platform managed \
  --region us-central1 \
  --project $PROJECT_ID

# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=discord-bot-ask-100x" \
  --limit=50 \
  --format="table(timestamp,severity,jsonPayload.message)" \
  --project=$PROJECT_ID
```

## Step 6: Verify Bot is Running

### 6.1 Check Cloud Run Service

```bash
# Get service details
gcloud run services describe discord-bot-ask-100x \
  --platform managed \
  --region us-central1 \
  --project $PROJECT_ID

# Check service status
gcloud run services list --platform managed --region us-central1
```

### 6.2 Test Discord Bot

In your Discord server, test the bot:
```
/help
/ask What is the meaning of life?
/stats
```

## Logging Features

Your bot now has comprehensive logging:

### Structured JSON Logs
All logs are in JSON format for easy filtering in Cloud Logging:
```json
{
  "severity": "INFO",
  "message": "User john asked: What is AI?",
  "component": "discord_bot",
  "timestamp": "2025-01-05 10:30:00"
}
```

### Log Queries

```bash
# Filter by severity
gcloud logging read "resource.type=cloud_run_revision AND severity=ERROR" \
  --limit=20 \
  --project=$PROJECT_ID

# Filter by user activity
gcloud logging read "resource.type=cloud_run_revision AND jsonPayload.message=~'User.*asked'" \
  --limit=20 \
  --project=$PROJECT_ID

# View logs in Cloud Console
echo "https://console.cloud.google.com/logs/query?project=${PROJECT_ID}"
```

## Troubleshooting

### Issue: Authentication Failed in GitHub Actions

**Solution**: Verify Workload Identity Federation setup:
```bash
# Check if service account exists
gcloud iam service-accounts describe $SA_EMAIL

# Check IAM bindings
gcloud iam service-accounts get-iam-policy $SA_EMAIL
```

### Issue: Bot Not Responding

**Solution**: Check logs:
```bash
gcloud run services logs tail discord-bot-ask-100x \
  --platform managed \
  --region us-central1
```

### Issue: Container Startup Failed

**Solution**: Check if Discord token is set correctly:
```bash
gcloud run services describe discord-bot-ask-100x \
  --platform managed \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

### Issue: Image Push Failed

**Solution**: Verify Artifact Registry permissions:
```bash
gcloud artifacts repositories get-iam-policy discord-bot-repo \
  --location=us-central1
```

## Cost Optimization

Your current configuration:
- **Min instances**: 1 (always running)
- **Max instances**: 1
- **Memory**: 512Mi
- **CPU**: 1

Estimated cost: ~$15-20/month for 24/7 availability

To reduce costs:
```bash
# Reduce to min-instances=0 (cold starts)
gcloud run services update discord-bot-ask-100x \
  --region us-central1 \
  --min-instances=0
```

## Security Best Practices

1. **Never commit secrets** - Use GitHub Secrets only
2. **Use Workload Identity Federation** - No service account keys
3. **Rotate Discord token** - If compromised, regenerate immediately
4. **Review IAM permissions** - Grant minimum required permissions
5. **Enable Cloud Armor** - For DDoS protection (optional)

## Updating the Bot

To deploy updates:
```bash
# Make your changes
git add .
git commit -m "Update bot features"
git push origin main
```

GitHub Actions will automatically rebuild and deploy.

## Cleanup

To delete all resources:

```bash
# Delete Cloud Run service
gcloud run services delete discord-bot-ask-100x \
  --region us-central1 \
  --quiet

# Delete Artifact Registry repository
gcloud artifacts repositories delete discord-bot-repo \
  --location=us-central1 \
  --quiet

# Delete service account
gcloud iam service-accounts delete $SA_EMAIL --quiet

# Delete Workload Identity Pool
gcloud iam workload-identity-pools delete github-pool \
  --location=global \
  --quiet
```

## Support

For issues:
- Check GitHub Actions logs
- View Cloud Run logs
- Review [Cloud Run documentation](https://cloud.google.com/run/docs)

## Next Steps

- Set up Cloud Monitoring alerts
- Configure error reporting
- Add Cloud SQL for persistent storage
- Implement Cloud Scheduler for periodic tasks
- Set up multi-region deployment
