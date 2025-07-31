#!/bin/bash

# Copilot Chat Backup Script
# Usage: ./backup_chat.sh "conversation_topic" "chat_content"

DATE=$(date +"%Y-%m-%d %H:%M:%S")
TOPIC="$1"
CONTENT="$2"

if [ -z "$TOPIC" ] || [ -z "$CONTENT" ]; then
    echo "Usage: $0 'topic' 'chat_content'"
    echo "Example: $0 'Bug Fix Discussion' 'User: I have an error... Copilot: The issue is...'"
    exit 1
fi

# Append to chat archive
cat << EOF >> copilot_chat_archive.md

### Session: [$DATE] - $TOPIC
**Content**:
\`\`\`
$CONTENT
\`\`\`

**Status**: Backed up automatically
---

EOF

# Commit and push to GitHub
git add copilot_chat_archive.md
git commit -m "Auto-backup: Copilot chat - $TOPIC"
git push origin main

echo "✅ Chat backed up and synced to GitHub!"
echo "📱 Accessible on all devices at: https://github.com/Sandy29krish/Sandy_sniper-bot/blob/main/copilot_chat_archive.md"
