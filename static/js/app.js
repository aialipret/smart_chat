let currentFlowConfig = null;

// Generate flow configuration
async function generateFlow() {
    const input = document.getElementById('flowInput').value;
    if (!input.trim()) {
        showStatus('Please describe your workflow first.', 'error');
        return;
    }
    
    try {
        showLoading('Generating flow configuration...');
        
        const response = await fetch('/api/config/generate-flow', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ input: input })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentFlowConfig = data.flow_config;
            displayFlowConfig(currentFlowConfig);
            document.getElementById('saveFlowBtn').disabled = false;
            showStatus('Flow configuration generated successfully!', 'success');
        } else {
            showStatus('Error generating flow: ' + data.error, 'error');
            displayFlowConfig('Error generating configuration:\n\n' + data.error);
        }
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Save flow configuration
async function saveFlow() {
    if (!currentFlowConfig) {
        showStatus('No flow configuration to save.', 'error');
        return;
    }
    
    try {
        showLoading('Saving flow configuration...');
        
        const response = await fetch('/api/config/save-flow', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ flow_config: currentFlowConfig })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showStatus('Flow configuration saved successfully!', 'success');
        } else {
            showStatus('Error saving flow: ' + data.error, 'error');
        }
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Load existing flow configuration
async function loadFlow() {
    try {
        showLoading('Loading flow configuration...');
        
        const response = await fetch('/api/config/load-flow');
        const data = await response.json();
        
        if (data.success && data.flow_config) {
            currentFlowConfig = data.flow_config;
            displayFlowConfig(currentFlowConfig);
            document.getElementById('saveFlowBtn').disabled = false;
            showStatus('Flow configuration loaded successfully!', 'success');
        } else {
            showStatus('No existing flow configuration found.', 'error');
        }
    } catch (error) {
        showStatus('Error loading flow: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display flow configuration
function displayFlowConfig(config) {
    const configDiv = document.getElementById('generatedConfig');
    if (typeof config === 'string') {
        configDiv.textContent = config;
    } else {
        configDiv.textContent = JSON.stringify(config, null, 2);
    }
}

// Send chat message
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    input.value = '';
    input.style.height = 'auto'; // Reset textarea height
    
    // Disable send button
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    
    try {
        showTyping();
        
        const response = await fetch('/api/chat/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addMessageToChat(data.response, 'assistant');
        } else {
            addMessageToChat('I apologize, but I encountered an error: ' + (data.error || 'Unknown error'), 'assistant');
        }
    } catch (error) {
        addMessageToChat('I apologize, but I encountered a connection error: ' + error.message, 'assistant');
    } finally {
        hideTyping();
        sendBtn.disabled = false;
    }
}

// Add message to chat container
function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Create avatar
    const avatar = document.createElement('div');
    avatar.className = `message-avatar ${sender}-avatar`;
    if (sender === 'user') {
        avatar.innerHTML = '<i class="fas fa-user"></i>';
    } else {
        avatar.innerHTML = '<i class="fas fa-robot"></i>';
    }
    
    // Create message content
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = message;
    
    // Add elements to message
    if (sender === 'user') {
        messageDiv.appendChild(content);
        messageDiv.appendChild(avatar);
    } else {
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle Enter key in chat input
function handleChatKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Auto-resize textarea
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }
});

// Show typing indicator
function showTyping() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'message assistant-message';
    
    // Create avatar
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar assistant-avatar';
    avatar.innerHTML = '<i class="fas fa-robot"></i>';
    
    // Create typing indicator
    const typingContent = document.createElement('div');
    typingContent.className = 'typing-indicator';
    typingContent.innerHTML = `
        <span style="margin-right: 8px;">AI is typing</span>
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(typingContent);
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hide typing indicator
function hideTyping() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Show loading message
function showLoading(message) {
    showStatus(message, 'loading');
}

// Hide loading message
function hideLoading() {
    const statusDiv = document.getElementById('configStatus');
    if (statusDiv) {
        statusDiv.innerHTML = '';
    }
}

// Show status message
function showStatus(message, type) {
    const statusDiv = document.getElementById('configStatus');
    if (!statusDiv) return;
    
    let icon, className;
    switch (type) {
        case 'success':
            icon = 'fas fa-check-circle';
            className = 'status-success';
            break;
        case 'error':
            icon = 'fas fa-exclamation-circle';
            className = 'status-error';
            break;
        case 'loading':
            icon = 'loading-spinner';
            className = 'status-success';
            break;
        default:
            icon = 'fas fa-info-circle';
            className = 'status-success';
    }
    
    if (type === 'loading') {
        statusDiv.innerHTML = `
            <div class="status-badge ${className}">
                <div class="${icon}"></div>
                ${message}
            </div>
        `;
    } else {
        statusDiv.innerHTML = `
            <div class="status-badge ${className}">
                <i class="${icon}"></i>
                ${message}
            </div>
        `;
    }
}