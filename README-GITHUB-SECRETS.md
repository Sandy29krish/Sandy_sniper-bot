# 🔐 Secure Deployment with GitHub Secrets

This document explains how to securely deploy your trading bot using GitHub repository secrets instead of storing sensitive credentials in code.

## 🚨 Why Use GitHub Secrets?

- **Security**: Credentials are encrypted and never exposed in your repository
- **Version Control**: No risk of accidentally committing sensitive data
- **Team Collaboration**: Secure sharing without exposing credentials
- **Environment Management**: Different secrets for different environments
- **Audit Trail**: GitHub tracks secret usage and changes

## 🛠️ Quick Setup Guide

### Step 1: Set Up GitHub Secrets

1. **Navigate to Repository Settings**
   ```
   https://github.com/Sandy29krish/Sandy_sniper-bot/settings/secrets/actions
   ```

2. **Add Required Secrets** (click "New repository secret" for each):

   | Secret Name | Description | Required |
   |-------------|-------------|----------|
   | `KITE_API_KEY` | Your Kite Connect API Key | ✅ Yes |
   | `KITE_API_SECRET` | Your Kite Connect API Secret | ✅ Yes |
   | `KITE_USER_ID` | Your Zerodha User ID | ✅ Yes |
   | `KITE_PASSWORD` | Your Zerodha Login Password | ✅ Yes |
   | `KITE_TOTP_SECRET` | Your TOTP Secret (base32) | ✅ Yes |
   | `TELEGRAM_BOT_TOKEN` | Telegram bot token | ⚪ Optional |
   | `TELEGRAM_CHAT_ID` | Your Telegram chat ID | ⚪ Optional |
   | `TELEGRAM_ID` | Your Telegram user ID | ⚪ Optional |
   | `CAPITAL` | Trading capital amount | ⚪ Optional |
   | `SWING_BOT_CAPITAL` | Swing trading capital | ⚪ Optional |

### Step 2: Deploy Using GitHub Actions

#### Option A: Automatic Deployment (Recommended)
- Push to `main` or `master` branch
- GitHub Actions will automatically run tests and deploy

#### Option B: Manual Deployment
1. Go to **Actions** tab in your repository
2. Select **"Production Deploy"** workflow
3. Click **"Run workflow"**
4. Choose environment and duration
5. Click **"Run workflow"** button

## 🚀 Deployment Workflows

### 1. Continuous Integration (`deploy-bot.yml`)
- **Triggers**: Push to main/master, Pull Requests
- **Purpose**: Testing and validation
- **Duration**: Limited (5 minutes for testing)

### 2. Production Deployment (`production-deploy.yml`)
- **Triggers**: Manual trigger only
- **Purpose**: Production trading
- **Duration**: Configurable (unlimited or specified minutes)
- **Features**: 
  - Environment validation
  - Token generation testing
  - Telegram notifications
  - Log collection

## 🔧 Local Development

### For Local Testing (Not Recommended for Production)

1. **Copy environment template**:
   ```bash
   cp env.template .env
   ```

2. **Fill in your credentials** (for development only)

3. **Run locally**:
   ```bash
   python run-local.py
   ```

⚠️ **Warning**: Never commit `.env` files with real credentials!

## 📊 Monitoring and Logs

### GitHub Actions Logs
- View workflow execution logs in the **Actions** tab
- Download artifacts containing bot logs
- Monitor deployment status and errors

### Telegram Notifications
If configured, you'll receive notifications for:
- ✅ Successful deployments
- ❌ Failed deployments
- 🚨 Runtime errors

### Log Files Available
- `*.log` - Application logs
- `trade_log.json` - Trading activity logs
- Token files (excluded from public logs for security)

## 🔒 Security Best Practices

### ✅ Do's
- Use GitHub secrets for all sensitive data
- Rotate API keys regularly
- Monitor GitHub Actions logs for suspicious activity
- Use different secrets for staging/production
- Enable two-factor authentication on GitHub

### ❌ Don'ts
- Never commit `.env` files with real credentials
- Don't share secrets in chat or email
- Don't use production credentials for testing
- Don't store secrets in code comments
- Don't use weak passwords

## 🛡️ Environment Security

### Production Environment
- Secrets are injected at runtime
- No persistent credential storage
- Encrypted communication
- Audit logging enabled

### Development Environment
- Use separate development API keys
- Local `.env` files (never committed)
- Limited trading capital for testing

## 🚨 Troubleshooting

### Common Issues

1. **"Secret not found" error**
   - Check secret name spelling (case-sensitive)
   - Verify secret is set in repository settings
   - Ensure you have admin access to repository

2. **"Invalid TOTP secret" error**
   - Use the base32 secret from authenticator setup
   - Don't use the QR code or 6-digit codes
   - Ensure no spaces or special characters

3. **"Authentication failed" error**
   - Verify API key is active
   - Check if password was recently changed
   - Ensure API key has trading permissions

4. **Workflow permission errors**
   - Check repository settings → Actions → General
   - Ensure workflows have read/write permissions

### Getting Help

1. **Check workflow logs** in GitHub Actions tab
2. **Review error messages** in the logs
3. **Verify all secrets** are properly set
4. **Test with development credentials** first

## 📈 Production Deployment Checklist

- [ ] All required GitHub secrets are configured
- [ ] TOTP secret is in correct base32 format
- [ ] API credentials are active and have trading permissions
- [ ] Telegram notifications are configured (optional)
- [ ] Trading capital amounts are set correctly
- [ ] Test deployment runs successfully
- [ ] Monitor initial trades for accuracy
- [ ] Set up log monitoring and alerts

## 🔄 Maintenance

### Regular Tasks
- **Weekly**: Check GitHub Actions logs for errors
- **Monthly**: Rotate API credentials
- **Quarterly**: Review and update trading parameters
- **As needed**: Update bot code and redeploy

### Updates and Changes
1. Make code changes in feature branches
2. Test with pull request workflows
3. Merge to main for automatic deployment
4. Monitor production deployment

---

**🎯 Ready to deploy securely?** Follow the setup guide above and start trading with confidence knowing your credentials are protected!