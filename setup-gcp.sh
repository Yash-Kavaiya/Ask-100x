#!/bin/bash

# Google Cloud Run Setup Script for Discord Bot
# This script sets up Workload Identity Federation for GitHub Actions

set -e

echo "=== Google Cloud Run Setup for Discord Bot ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed. Please install it from https://cloud.google.com/sdk/docs/install"
    exit 1
fi

print_success "gcloud CLI found"

# Get project ID
read -p "Enter your GCP Project ID: " PROJECT_ID
if [ -z "$PROJECT_ID" ]; then
    print_error "Project ID cannot be empty"
    exit 1
fi

# Get GitHub details
read -p "Enter your GitHub username or organization: " GITHUB_ORG
if [ -z "$GITHUB_ORG" ]; then
    print_error "GitHub username/org cannot be empty"
    exit 1
fi

read -p "Enter your GitHub repository name: " GITHUB_REPO
if [ -z "$GITHUB_REPO" ]; then
    print_error "Repository name cannot be empty"
    exit 1
fi

echo ""
print_info "Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  GitHub: $GITHUB_ORG/$GITHUB_REPO"
echo ""

read -p "Continue with this configuration? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Setup cancelled"
    exit 1
fi

# Set project
print_info "Setting GCP project..."
gcloud config set project $PROJECT_ID
print_success "Project set to $PROJECT_ID"

# Enable required APIs
print_info "Enabling required APIs (this may take a few minutes)..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  iamcredentials.googleapis.com \
  logging.googleapis.com \
  --quiet

print_success "APIs enabled"

# Create Artifact Registry repository
print_info "Creating Artifact Registry repository..."
if gcloud artifacts repositories describe discord-bot-repo --location=us-central1 &> /dev/null; then
    print_info "Repository already exists, skipping..."
else
    gcloud artifacts repositories create discord-bot-repo \
      --repository-format=docker \
      --location=us-central1 \
      --description="Discord bot container images" \
      --quiet
    print_success "Artifact Registry repository created"
fi

# Create service account
print_info "Creating service account..."
SA_EMAIL="github-actions-bot@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe $SA_EMAIL &> /dev/null; then
    print_info "Service account already exists, skipping..."
else
    gcloud iam service-accounts create github-actions-bot \
      --display-name="GitHub Actions Bot Deployer" \
      --quiet
    print_success "Service account created: $SA_EMAIL"
fi

# Grant permissions
print_info "Granting IAM permissions..."

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin" \
  --quiet > /dev/null

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.writer" \
  --quiet > /dev/null

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser" \
  --quiet > /dev/null

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/logging.logWriter" \
  --quiet > /dev/null

print_success "IAM permissions granted"

# Create Workload Identity Pool
print_info "Creating Workload Identity Pool..."
if gcloud iam workload-identity-pools describe github-pool --location=global --project=$PROJECT_ID &> /dev/null; then
    print_info "Workload Identity Pool already exists, skipping..."
else
    gcloud iam workload-identity-pools create "github-pool" \
      --project="${PROJECT_ID}" \
      --location="global" \
      --display-name="GitHub Actions Pool" \
      --quiet
    print_success "Workload Identity Pool created"
fi

WORKLOAD_IDENTITY_POOL_ID=$(gcloud iam workload-identity-pools describe "github-pool" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --format="value(name)")

# Create Workload Identity Provider
print_info "Creating Workload Identity Provider..."
if gcloud iam workload-identity-pools providers describe github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --project=$PROJECT_ID &> /dev/null; then
    print_info "Provider already exists, skipping..."
else
    gcloud iam workload-identity-pools providers create-oidc "github-provider" \
      --project="${PROJECT_ID}" \
      --location="global" \
      --workload-identity-pool="github-pool" \
      --display-name="GitHub Provider" \
      --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
      --issuer-uri="https://token.actions.githubusercontent.com" \
      --quiet
    print_success "Workload Identity Provider created"
fi

WIF_PROVIDER=$(gcloud iam workload-identity-pools providers describe "github-provider" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --format="value(name)")

# Allow GitHub to impersonate service account
print_info "Configuring GitHub repository access..."
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_ID}/attribute.repository/${GITHUB_ORG}/${GITHUB_REPO}" \
  --quiet > /dev/null

print_success "GitHub repository access configured"

echo ""
echo "=========================================="
print_success "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Add these secrets to your GitHub repository:"
echo "Go to: https://github.com/${GITHUB_ORG}/${GITHUB_REPO}/settings/secrets/actions"
echo ""
echo "Secret Name: GCP_PROJECT_ID"
echo "Value: ${PROJECT_ID}"
echo ""
echo "Secret Name: WIF_PROVIDER"
echo "Value: ${WIF_PROVIDER}"
echo ""
echo "Secret Name: WIF_SERVICE_ACCOUNT"
echo "Value: ${SA_EMAIL}"
echo ""
echo "Secret Name: DISCORD_TOKEN"
echo "Value: [Your Discord bot token]"
echo ""
echo "=========================================="
print_info "Next steps:"
echo "1. Add the above secrets to GitHub"
echo "2. Push your code to trigger deployment"
echo "3. Monitor deployment in GitHub Actions"
echo "=========================================="
