# Deployment Checklist

Use this checklist to ensure a successful deployment to Google Cloud Run.

## Pre-Deployment Setup

### Google Cloud Setup
- [ ] Install [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [ ] Create or select a GCP project
- [ ] Enable billing on the GCP project
- [ ] Note your GCP Project ID: `_________________`

### GitHub Setup
- [ ] Repository is pushed to GitHub
- [ ] You have admin access to the repository
- [ ] Repository name: `_________________`
- [ ] GitHub username/org: `_________________`

### Discord Bot
- [ ] Discord bot created in [Discord Developer Portal](https://discord.com/developers/applications)
- [ ] Bot token obtained
- [ ] Required intents enabled:
  - [ ] Message Content Intent
  - [ ] Server Members Intent
- [ ] Bot invited to your Discord server with correct permissions

## Step 1: Run Setup Script

- [ ] Make script executable: `chmod +x setup-gcp.sh`
- [ ] Run setup script: `./setup-gcp.sh`
- [ ] Script completed successfully
- [ ] Save the output with your secrets (keep it secure!)

### Script Output (Copy these values):
```
GCP_PROJECT_ID: _________________________________
WIF_PROVIDER: ___________________________________
WIF_SERVICE_ACCOUNT: ____________________________
```

## Step 2: Configure GitHub Secrets

Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`

Add these 4 secrets:

- [ ] **GCP_PROJECT_ID**
  - Value: `_________________________________`

- [ ] **WIF_PROVIDER**
  - Value: `_________________________________`
  - Should start with: `projects/`

- [ ] **WIF_SERVICE_ACCOUNT**
  - Value: `_________________________________`
  - Should end with: `@YOUR_PROJECT.iam.gserviceaccount.com`

- [ ] **DISCORD_TOKEN**
  - Value: `[Your Discord bot token from Discord Developer Portal]`

## Step 3: Verify Configuration

- [ ] All 4 secrets are added to GitHub
- [ ] Secret names are exactly as shown (case-sensitive)
- [ ] No extra spaces in secret values

## Step 4: Deploy

- [ ] All changes committed to Git
- [ ] Code pushed to `main` branch

```bash
git add .
git commit -m "Deploy Discord bot to Cloud Run"
git push origin main
```

- [ ] GitHub Actions workflow triggered
- [ ] Go to repository's **Actions** tab

## Step 5: Monitor Deployment

### GitHub Actions
- [ ] Workflow "Deploy to Cloud Run" is running
- [ ] "Checkout code" step completed ✓
- [ ] "Authenticate to Google Cloud" step completed ✓
- [ ] "Build Docker image" step completed ✓
- [ ] "Push Docker image to Artifact Registry" step completed ✓
- [ ] "Deploy to Cloud Run" step completed ✓
- [ ] "Route traffic to new revision" step completed ✓
- [ ] All steps show green checkmarks ✓

### Cloud Run
```bash
gcloud run services describe discord-bot-ask-100x \
  --platform managed \
  --region us-central1
```

- [ ] Service exists
- [ ] Status shows "Ready"
- [ ] Latest revision is serving traffic

## Step 6: Verify Bot is Working

### View Logs
```bash
gcloud run services logs tail discord-bot-ask-100x \
  --platform managed \
  --region us-central1
```

- [ ] Logs showing "Bot is ready! Logged in as..."
- [ ] No error messages in logs
- [ ] Bot shows "Connected to X guild(s)"

### Test in Discord
- [ ] Bot shows as online (green status)
- [ ] `/help` command works
- [ ] `/ask <question>` command works
- [ ] `/info` command works
- [ ] `/stats` command works
- [ ] `/limit` command works

## Step 7: Post-Deployment Verification

### Logging
```bash
# Check structured logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=discord-bot-ask-100x" \
  --limit=10 \
  --format=json
```

- [ ] Logs are in JSON format
- [ ] Severity levels are correct (INFO, WARNING, ERROR)
- [ ] User activity is being logged

### Performance
- [ ] Bot responds within 1-2 seconds
- [ ] No timeout errors
- [ ] Rate limiting works correctly

### Cost Monitoring
- [ ] Set up billing alerts in GCP
- [ ] Review initial costs
- [ ] Estimated: $17-22/month

## Troubleshooting

If something goes wrong, check:

### Authentication Issues
- [ ] WIF_PROVIDER secret is correct
- [ ] WIF_SERVICE_ACCOUNT secret is correct
- [ ] Service account has required permissions

### Deployment Issues
- [ ] Artifact Registry repository exists
- [ ] Docker image pushed successfully
- [ ] Cloud Run service created

### Bot Not Responding
- [ ] DISCORD_TOKEN is correct in GitHub secrets
- [ ] Bot has correct Discord permissions
- [ ] Check logs for errors:
```bash
gcloud run services logs tail discord-bot-ask-100x --region us-central1
```

### View Recent Errors
```bash
gcloud logging read "resource.type=cloud_run_revision AND severity=ERROR" \
  --limit=20 \
  --format="table(timestamp,jsonPayload.message)"
```

## Updates and Maintenance

### Deploy Updates
To deploy changes:
```bash
git add .
git commit -m "Update bot features"
git push origin main
```

- [ ] Changes pushed to main
- [ ] GitHub Actions triggered automatically
- [ ] New revision deployed
- [ ] Traffic routed to new revision

### Monitor Costs
- [ ] Weekly cost review
- [ ] Adjust min-instances if needed
- [ ] Review logging costs

### Security
- [ ] Rotate Discord token every 90 days
- [ ] Review IAM permissions quarterly
- [ ] Update dependencies monthly

## Resources

- **Quick Start**: [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md)
- **Detailed Guide**: [CLOUD_RUN_SETUP.md](CLOUD_RUN_SETUP.md)
- **Summary**: [deploy-summary.txt](deploy-summary.txt)

## Support

- GitHub Actions Logs: Repository → Actions tab
- Cloud Run Logs: `gcloud run services logs tail discord-bot-ask-100x --region us-central1`
- Cloud Console: https://console.cloud.google.com/run

---

## Completion

- [ ] All steps completed successfully
- [ ] Bot is running in Cloud Run
- [ ] Bot responds in Discord
- [ ] Logging is working
- [ ] Monitoring is set up

**Deployment Date**: _________________

**Notes**:
```
_________________________________________________
_________________________________________________
_________________________________________________
```

Congratulations! Your Discord bot is now deployed to Google Cloud Run!
