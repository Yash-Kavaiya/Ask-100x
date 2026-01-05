# Ready to Deploy!

Your Discord bot is fully configured for Google Cloud Run deployment. Follow these steps to deploy.

## What Was Changed

### Modified Files
- `.github/workflows/deploy-cloudrun.yml` - Updated to Workload Identity Federation
- `bot.py` - Added structured logging for Cloud Logging
- `README.md` - Updated deployment documentation

### New Files
- `CLOUD_RUN_SETUP.md` - Comprehensive setup guide
- `DEPLOYMENT_QUICKSTART.md` - 5-minute quick start
- `DEPLOYMENT_CHECKLIST.md` - Interactive deployment checklist
- `CHANGES_SUMMARY.md` - Summary of all changes
- `deploy-summary.txt` - Quick reference
- `setup-gcp.sh` - Automated GCP setup script
- `DEPLOY_NOW.md` - This file

## Before You Deploy

### 1. Install gcloud CLI (if not already installed)

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install

**Mac:**
```bash
brew install google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
```

### 2. Have Your Information Ready

- [ ] GCP Project ID (or create new project)
- [ ] GitHub username/organization
- [ ] GitHub repository name
- [ ] Discord bot token (from Discord Developer Portal)

## Deployment Steps

### Step 1: Commit Your Changes

```bash
# Navigate to your repository
cd "c:\Users\yashk\Downloads\Ask-100x"

# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Add Cloud Run deployment with Workload Identity Federation

- Update GitHub Actions workflow to use Workload Identity Federation
- Remove dependency on service account keys for better security
- Add structured JSON logging for Google Cloud Logging
- Create comprehensive deployment documentation
- Add automated setup script for GCP configuration
- Update README with deployment guides

Features:
- Secure authentication via Workload Identity Federation
- Automatic deployment on push to main
- Zero-downtime deployments with traffic routing
- Comprehensive logging and monitoring
- Deployment guides and interactive checklist"

# Push to GitHub
git push origin main
```

### Step 2: Set Up Google Cloud

```bash
# If on Windows, use Git Bash or WSL
# If on Mac/Linux, run directly

# Make script executable
chmod +x setup-gcp.sh

# Run setup script
./setup-gcp.sh
```

**Follow the prompts:**
1. Enter your GCP Project ID
2. Enter your GitHub username/org
3. Enter your repository name: `Ask-100x`
4. Confirm setup

**Save the output!** You'll need these 4 secrets for GitHub.

### Step 3: Add GitHub Secrets

1. Go to: https://github.com/Yash-Kavaiya/Ask-100x/settings/secrets/actions
2. Click **"New repository secret"**
3. Add each of these 4 secrets (from setup script output):

```
Name: GCP_PROJECT_ID
Value: [from setup script]

Name: WIF_PROVIDER
Value: [from setup script - starts with "projects/"]

Name: WIF_SERVICE_ACCOUNT
Value: [from setup script - ends with ".iam.gserviceaccount.com"]

Name: DISCORD_TOKEN
Value: [Your Discord bot token from Discord Developer Portal]
```

### Step 4: Trigger Deployment

If you already pushed in Step 1, deployment is already running!

Check deployment status:
https://github.com/Yash-Kavaiya/Ask-100x/actions

### Step 5: Monitor Deployment

Watch the GitHub Actions workflow:
1. Go to **Actions** tab in your repository
2. Click on the running workflow
3. Watch each step complete

Expected steps:
- ✓ Checkout code
- ✓ Authenticate to Google Cloud
- ✓ Set up Cloud SDK
- ✓ Configure Docker for Artifact Registry
- ✓ Build Docker image
- ✓ Push Docker image to Artifact Registry
- ✓ Deploy to Cloud Run
- ✓ Route traffic to new revision
- ✓ Show deployment info
- ✓ View logs

### Step 6: Verify Deployment

Once deployment completes (5-10 minutes):

```bash
# Check service status
gcloud run services describe discord-bot-ask-100x \
  --platform managed \
  --region us-central1

# View real-time logs
gcloud run services logs tail discord-bot-ask-100x \
  --platform managed \
  --region us-central1
```

Look for:
```
Bot is ready! Logged in as YourBotName
Connected to X guild(s)
Slash commands synced!
```

### Step 7: Test in Discord

In your Discord server, try these commands:

```
/help
/ask Hello, are you working on Cloud Run?
/info
/stats
/limit
```

Bot should respond within 1-2 seconds!

## Verification Checklist

- [ ] Code committed and pushed to GitHub
- [ ] Setup script completed successfully
- [ ] 4 secrets added to GitHub repository
- [ ] GitHub Actions workflow completed successfully
- [ ] All workflow steps show green checkmarks
- [ ] Cloud Run service is in "Ready" status
- [ ] Logs show "Bot is ready!"
- [ ] Bot shows online in Discord (green status)
- [ ] All slash commands work correctly
- [ ] No errors in Cloud Run logs

## Troubleshooting

### "Permission denied" on setup-gcp.sh

**Windows PowerShell:**
```bash
# Use Git Bash instead, or WSL
bash setup-gcp.sh
```

**Mac/Linux:**
```bash
chmod +x setup-gcp.sh
./setup-gcp.sh
```

### GitHub Actions fails at "Authenticate to Google Cloud"

**Solution:**
1. Verify `WIF_PROVIDER` secret is correct
2. Verify `WIF_SERVICE_ACCOUNT` secret is correct
3. Re-run setup script if needed
4. Check secret names are EXACT (case-sensitive)

### Bot not responding in Discord

**Check logs:**
```bash
gcloud run services logs tail discord-bot-ask-100x --region us-central1
```

**Common issues:**
- Discord token incorrect → Re-add `DISCORD_TOKEN` secret
- Bot missing permissions → Check Discord Developer Portal
- Service not ready → Wait 1-2 minutes after deployment

### "gcloud: command not found"

**Install gcloud CLI:**
- Windows: https://cloud.google.com/sdk/docs/install
- Mac: `brew install google-cloud-sdk`
- Linux: `curl https://sdk.cloud.google.com | bash`

## What Happens After Push?

1. **GitHub Actions triggers** (~30 seconds)
2. **Authentication via Workload Identity Federation** (~10 seconds)
3. **Docker build** (~2-3 minutes)
4. **Push to Artifact Registry** (~1 minute)
5. **Deploy to Cloud Run** (~2-3 minutes)
6. **Traffic routing** (~30 seconds)
7. **Bot starts** (~30 seconds)

**Total time: ~7-10 minutes**

## Monitoring Commands

```bash
# View service details
gcloud run services describe discord-bot-ask-100x \
  --region us-central1

# View real-time logs
gcloud run services logs tail discord-bot-ask-100x \
  --region us-central1

# View errors only
gcloud logging read "resource.type=cloud_run_revision AND severity=ERROR" \
  --limit=20

# View service URL
gcloud run services describe discord-bot-ask-100x \
  --region us-central1 \
  --format='value(status.url)'

# List all revisions
gcloud run revisions list \
  --service=discord-bot-ask-100x \
  --region=us-central1
```

## Cost Monitoring

Current configuration costs ~$17-22/month.

**View costs:**
https://console.cloud.google.com/billing

**Set up budget alerts:**
https://console.cloud.google.com/billing/budgets

## Update Bot Later

To deploy updates:

```bash
# Make your changes to bot.py or other files
git add .
git commit -m "Update bot features"
git push origin main
```

Deployment happens automatically!

## Support

- **Quick Start**: [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md)
- **Full Guide**: [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md)
- **Checklist**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Changes**: [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)

## Resources

- **GitHub Actions**: https://github.com/Yash-Kavaiya/Ask-100x/actions
- **Cloud Console**: https://console.cloud.google.com/run
- **Logging**: https://console.cloud.google.com/logs

---

## Ready? Let's Deploy!

```bash
# 1. Commit changes
git add .
git commit -m "Add Cloud Run deployment with Workload Identity Federation"
git push origin main

# 2. Run setup script
chmod +x setup-gcp.sh
./setup-gcp.sh

# 3. Add 4 secrets to GitHub
# (Go to repository settings → secrets)

# 4. Watch deployment
# (Go to repository actions tab)

# 5. Verify
gcloud run services logs tail discord-bot-ask-100x --region us-central1

# 6. Test in Discord
# /help, /ask, /stats
```

**Good luck! Your bot will be live in ~10 minutes!**
