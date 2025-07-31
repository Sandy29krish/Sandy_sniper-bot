// Copilot Chat Auto-Backup Browser Script
// Instructions: 
// 1. Open browser console (F12)
// 2. Paste this script
// 3. It will automatically copy chat content to clipboard
// 4. Manually paste into your GitHub repository

function backupCopilotChat() {
    // Try to find Copilot chat content in various possible selectors
    const chatSelectors = [
        '.chat-container',
        '.copilot-chat',
        '[data-testid="chat"]',
        '.conversation',
        '.chat-messages',
        '.vscode-chat-content'
    ];
    
    let chatContent = '';
    let chatElement = null;
    
    // Find the chat container
    for (const selector of chatSelectors) {
        chatElement = document.querySelector(selector);
        if (chatElement) {
            chatContent = chatElement.innerText || chatElement.textContent;
            break;
        }
    }
    
    if (!chatContent) {
        // Fallback: try to get all text content
        chatContent = document.body.innerText;
    }
    
    // Format the content
    const timestamp = new Date().toISOString().split('T')[0];
    const formattedContent = `
### Session: [${timestamp}] - Auto-Backup
**Content**:
\`\`\`
${chatContent}
\`\`\`

**Source**: Browser auto-backup
**URL**: ${window.location.href}
---
`;
    
    // Copy to clipboard
    navigator.clipboard.writeText(formattedContent).then(() => {
        alert('✅ Chat content copied to clipboard!\n\nNext steps:\n1. Go to GitHub repository\n2. Edit copilot_chat_archive.md\n3. Paste the content');
    }).catch(err => {
        console.error('Failed to copy to clipboard:', err);
        // Fallback: show content in console
        console.log('Chat content to backup:', formattedContent);
    });
}

// Create a backup button
function createBackupButton() {
    const button = document.createElement('button');
    button.innerHTML = '💾 Backup Chat';
    button.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 9999;
        background: #0066cc;
        color: white;
        border: none;
        padding: 10px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 12px;
    `;
    button.onclick = backupCopilotChat;
    document.body.appendChild(button);
}

// Auto-create backup button
createBackupButton();

console.log('🤖 Copilot Chat Backup Script Loaded!');
console.log('Click the "💾 Backup Chat" button to backup current conversation');

// You can also call backupCopilotChat() directly from console
