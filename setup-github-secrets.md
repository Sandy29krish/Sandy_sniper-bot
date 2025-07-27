# GitHub Secrets Setup Guide

This guide will help you set up GitHub repository secrets to securely store your trading bot credentials.

## 🔐 Required GitHub Secrets

### Navigate to Your Repository Settings
1. Go to your GitHub repository: `https://github.com/Sandy29krish/Sandy_sniper-bot`
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret** for each secret below

### 🏦 Kite/Zerodha API Secrets (REQUIRED)

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `KITE_API_KEY` | Your Kite Connect API Key | `abcdef123456` |
| `KITE_API_SECRET` | Your Kite Connect API Secret | `xyz789secret` |
| `KITE_USER_ID` | Your Zerodha User ID | `AB1234` |
| `KITE_PASSWORD` | Your Zerodha Login Password | `MySecurePassword123` |
| `KITE_TOTP_SECRET` | Your TOTP Secret (from authenticator app setup) | `JBSWY3DPEHPK3PXP` |

### 💰 Trading Configuration (OPTIONAL - has defaults)

| Secret Name | Default Value | Description |
|-------------|---------------|-------------|
| `CAPITAL` | `170000` | Total trading capital |
| `SWING_BOT_CAPITAL` | `170000` | Capital allocated for swing trading |
| `SLEEP_INTERVAL` | `60` | Sleep interval between bot runs (seconds) |

### 📱 Telegram Notifications (OPTIONAL)

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | Message @BotFather on Telegram |
| `TELEGRAM_CHAT_ID` | Your chat ID | Message @userinfobot on Telegram |
| `TELEGRAM_ID` | Your Telegram user ID | Same as chat ID for personal use |

### 🔧 System Monitoring (OPTIONAL - has defaults)

| Secret Name | Default Value | Description |
|-------------|---------------|-------------|
| `HEALTH_CHECK_INTERVAL` | `60` | Health check interval (seconds) |
| `HEALTH_CPU_THRESHOLD` | `90.0` | CPU usage alert threshold (%) |
| `HEALTH_MEM_THRESHOLD` | `90.0` | Memory usage alert threshold (%) |
| `TRADE_LOG_FILE` | `trade_log.json` | Trade log file name |

## 🚀 How to Add Secrets

### Method 1: GitHub Web Interface
1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Enter the **Name** (e.g., `KITE_API_KEY`)
4. Enter the **Secret** value
5. Click **Add secret**
6. Repeat for all required secrets

### Method 2: GitHub CLI (if you have it installed)
```bash
# Set required Kite secrets
gh secret set KITE_API_KEY --body "your_api_key_here"
gh secret set KITE_API_SECRET --body "your_api_secret_here"
gh secret set KITE_USER_ID --body "your_user_id_here"
gh secret set KITE_PASSWORD --body "your_password_here"
gh secret set KITE_TOTP_SECRET --body "your_totp_secret_here"

# Set optional Telegram secrets
gh secret set TELEGRAM_BOT_TOKEN --body "your_bot_token_here"
gh secret set TELEGRAM_CHAT_ID --body "your_chat_id_here"
gh secret set TELEGRAM_ID --body "your_telegram_id_here"

# Set optional trading configuration
gh secret set CAPITAL --body "500000"
gh secret set SWING_BOT_CAPITAL --body "300000"
```

## 🔒 Security Best Practices

1. **Never commit secrets to code** - Always use GitHub secrets
2. **Use environment-specific secrets** - Different secrets for dev/prod
3. **Rotate secrets regularly** - Change API keys periodically
4. **Limit secret access** - Only give access to necessary workflows
5. **Monitor secret usage** - Check GitHub Actions logs for any issues

## 📋 Verification Checklist

- [ ] All required Kite API secrets are set
- [ ] TOTP secret is correctly formatted (base32)
- [ ] Telegram secrets are set (if notifications needed)
- [ ] Trading capital amounts are correct
- [ ] GitHub Actions workflow can access all secrets
- [ ] Test workflow runs successfully

## 🚨 Troubleshooting

### Common Issues:

1. **Invalid TOTP Secret**: Ensure it's the base32 secret, not the QR code
2. **API Key Issues**: Verify the API key is active and has trading permissions
3. **Password Changes**: Update the password secret if you change your Zerodha password
4. **Secret Not Found**: Check secret name spelling matches exactly

### Testing Your Setup:
1. Push code to trigger the GitHub Action
2. Check the workflow logs for any authentication errors
3. Verify the bot can generate tokens successfully

## 📞 Support

If you encounter issues:
1. Check GitHub Actions workflow logs
2. Verify all secret names match exactly
3. Ensure API credentials are valid and active
4. Test TOTP generation manually

---

**Important**: After setting up secrets, the `.env` file will be automatically generated during GitHub Actions execution, keeping your credentials secure and never exposing them in your repository.