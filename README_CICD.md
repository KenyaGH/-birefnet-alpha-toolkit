# CI/CD Pipeline Guide - Alpha Mask Toolkit

Complete guide for setting up and using the automated CI/CD pipeline for the Alpha Mask Toolkit.

## 🔄 Pipeline Overview

### **3 Automated Workflows:**

1. **CI (Continuous Integration)** - `ci.yml`
   - Tests code on every push/PR
   - Validates Docker builds
   - Code quality checks

2. **CD (Continuous Deployment)** - `cd.yml`
   - Deploys to Docker Hub when CI passes
   - Automatic deployment on main branch

3. **Release (Versioning)** - `release.yml`
   - Creates versioned releases
   - Publishes tagged Docker images

## 🚀 Quick Setup

### 1. **GitHub Repository Setup**
```bash
# Add CI/CD files to your repo
git add .github/workflows/
git commit -m "Add CI/CD pipeline"
git push origin main
```

### 2. **Configure GitHub Secrets**
Go to: **Repository Settings → Secrets and Variables → Actions**

Add these secrets:
- `DOCKER_USERNAME` - Your Docker Hub username
- `DOCKER_PASSWORD` - Your Docker Hub access token

### 3. **First Run**
```bash
# Push any code change to trigger CI
echo "# My Alpha Mask Toolkit" > README.md
git add README.md
git commit -m "Initial commit"
git push origin main
```

## 📋 Detailed Workflow Guide

### **CI Pipeline (ci.yml)**

**Triggers:** Push to main/develop, Pull Requests

**What it does:**
```
Code Push → Quality Checks → Script Tests → Docker Build → Security Scan → Report
```

**Jobs:**
1. **Code Quality** (10 min)
   - Python linting with flake8
   - Code formatting check with black
   - Import sorting with isort

2. **Script Testing** (15 min)
   - Python syntax validation
   - Import testing
   - Basic functionality checks

3. **Docker Testing** (45 min)
   - Build Docker image
   - Test container startup
   - Verify AI model loading
   - Test entrypoint script

4. **Security Scanning** (10 min)
   - Vulnerability scanning with Trivy
   - Dependency security check

5. **Report Generation**
   - CI status summary
   - Next steps guidance

**View Results:** Check the "Actions" tab in your GitHub repository

### **CD Pipeline (cd.yml)**

**Triggers:** After successful CI on main branch

**What it does:**
```
CI Success → Build Production Image → Push to Docker Hub → Create Release
```

**Jobs:**
1. **Check CI Status**
   - Only runs if CI passed
   - Validates deployment readiness

2. **Deploy**
   - Build optimized Docker image
   - Push to Docker Hub with tags:
     - `latest` (main branch)
     - `main-{sha}` (commit specific)
     - `{branch}` (branch specific)

3. **Release** (manual deployments only)
   - Create GitHub release
   - Generate changelog
   - Tag management

**Docker Hub Images:**
- `your-username/alpha-mask-toolkit:latest`
- `your-username/alpha-mask-toolkit:main-abc1234`

### **Release Pipeline (release.yml)**

**Triggers:** Git tags matching `v*.*.*` pattern

**What it does:**
```
Create Tag → Build Versioned Image → Push to Docker Hub → Create GitHub Release
```

**Usage:**
```bash
# Create and push a version tag
git tag v1.0.0
git push --tags

# GitHub automatically:
# ✅ Builds docker image with version tags
# ✅ Pushes to Docker Hub
# ✅ Creates GitHub release with changelog
```

**Generated Tags:**
- `your-username/alpha-mask-toolkit:v1.0.0`
- `your-username/alpha-mask-toolkit:1.0`
- `your-username/alpha-mask-toolkit:1`
- `your-username/alpha-mask-toolkit:latest`

## 🎯 Usage Examples

### **For Developers:**

#### Daily Development
```bash
# Make changes
git add .
git commit -m "Improve alpha mask quality"
git push origin develop

# CI automatically runs:
# ✅ Tests your changes
# ✅ Reports any issues
# ❌ Blocks merge if tests fail
```

#### Create Pull Request
```bash
# Create PR to main
gh pr create --title "Add new features" --body "Description"

# CI runs on PR:
# ✅ Validates changes
# ✅ Shows test results in PR
# ✅ Allows safe merging
```

#### Release New Version
```bash
# When ready for release
git checkout main
git pull origin main
git tag v1.2.0
git push --tags

# Release pipeline:
# ✅ Builds v1.2.0 image
# ✅ Publishes to Docker Hub
# ✅ Creates GitHub release
# ✅ Generates changelog
```

### **For Users:**

#### Use Latest Development
```bash
docker pull your-username/alpha-mask-toolkit:latest
```

#### Use Specific Version
```bash
docker pull your-username/alpha-mask-toolkit:v1.0.0
```

#### Check Available Versions
- Visit: https://hub.docker.com/r/your-username/alpha-mask-toolkit/tags

## 🔧 Configuration

### **Environment Variables**
```yaml
env:
  REGISTRY: docker.io
  IMAGE_NAME: alpha-mask-toolkit
```

### **Timeout Settings**
- Code quality: 10 minutes
- Script testing: 15 minutes
- Docker build: 45 minutes
- Full release: 60 minutes

### **Platform Support**
- Primary: `linux/amd64`
- Extensible to: `linux/arm64` (add to platforms list)

## 🐛 Troubleshooting

### **Common Issues:**

#### "Docker Hub login failed"
```bash
# Check secrets are set correctly:
# Repository Settings → Secrets → Actions
# Add: DOCKER_USERNAME, DOCKER_PASSWORD
```

#### "CI failing on code quality"
```bash
# Fix locally before pushing:
black .                    # Format code
isort .                   # Sort imports
flake8 .                  # Check linting
```

#### "Docker build timeout"
```bash
# Increase timeout in workflow:
timeout-minutes: 60       # Increase from 45
```

#### "Tag format rejected"
```bash
# Use semantic versioning:
git tag v1.0.0            # ✅ Correct
git tag 1.0.0             # ❌ Wrong (missing 'v')
git tag v1.0              # ❌ Wrong (needs patch version)
```

### **Debug CI Locally:**

#### Test Docker Build
```bash
docker build -t alpha-mask-toolkit .
docker run --rm alpha-mask-toolkit python -c "import torch; print('OK')"
```

#### Test Code Quality
```bash
pip install black flake8 isort
black --check .
flake8 .
isort --check-only .
```

## 📊 Monitoring

### **GitHub Actions**
- **View Status:** Repository → Actions tab
- **Check Logs:** Click on workflow runs
- **Monitor Performance:** Check run times

### **Docker Hub**
- **View Images:** https://hub.docker.com/r/your-username/alpha-mask-toolkit
- **Check Downloads:** Monitor pull statistics
- **Manage Tags:** Delete old versions if needed

### **Release Management**
- **View Releases:** Repository → Releases tab
- **Track Downloads:** Monitor asset downloads
- **User Feedback:** Check issues for version-specific problems

## 🔄 Workflow Customization

### **Add New Tests:**
```yaml
# In ci.yml, add to test-scripts job:
- name: Custom Test
  run: |
    python test_custom_functionality.py
```

### **Change Deployment Triggers:**
```yaml
# In cd.yml, modify triggers:
on:
  push:
    branches: [ main, staging ]  # Add staging
```

### **Add Slack Notifications:**
```yaml
# Add to any job:
- name: Slack Notification
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### **Multi-Platform Builds:**
```yaml
# In docker build steps:
platforms: linux/amd64,linux/arm64
```

## 📚 Best Practices

### **Branching Strategy:**
- `main` - Production releases only
- `develop` - Integration branch
- `feature/*` - Feature branches

### **Commit Messages:**
```bash
# Semantic commit messages:
git commit -m "feat: add batch processing support"
git commit -m "fix: resolve CUDA memory leak"
git commit -m "docs: update Docker guide"
git commit -m "BREAKING CHANGE: require Python 3.10+"
```

### **Version Numbering:**
- `v1.0.0` - Major release (breaking changes)
- `v1.1.0` - Minor release (new features)
- `v1.0.1` - Patch release (bug fixes)

### **Docker Tag Strategy:**
- `latest` - Latest stable release
- `v1.0.0` - Specific version
- `main-abc123` - Development builds

## 🚀 Advanced Features

### **Scheduled Builds:**
```yaml
# Add to ci.yml:
on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly Monday 2 AM
```

### **Matrix Testing:**
```yaml
strategy:
  matrix:
    python-version: [3.10, 3.11]
    cuda-version: [11.8, 12.1]
```

### **Conditional Deployments:**
```yaml
# Only deploy on specific conditions:
if: startsWith(github.ref, 'refs/tags/v') && !contains(github.ref, 'beta')
```

---

## 📞 Support

- **Issues:** Create GitHub issues for CI/CD problems
- **Discussions:** Use GitHub Discussions for questions
- **Documentation:** Keep this README updated with changes

**Pipeline Status:** [![CI](https://github.com/your-username/alpha-mask-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/alpha-mask-toolkit/actions/workflows/ci.yml)