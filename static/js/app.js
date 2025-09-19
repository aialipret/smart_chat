// Multi-Agent System JavaScript

let currentFlowConfig = null;
let currentAgent = null;
let agents = [];
let availableTools = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadAgents();
    loadAvailableTools();
    setupChatInput();
});

// ===== AGENT MANAGEMENT =====

async function loadAgents() {
    try {
        const response = await fetch('/api/agents');
        const data = await response.json();
        
        if (data.success) {
            agents = data.agents;
            displayAgents();
            populateChatAgentSelect();
        } else {
            showStatus('Error loading agents: ' + data.error, 'error');
        }
    } catch (error) {
        showStatus('Error loading agents: ' + error.message, 'error');
    }
}

function displayAgents() {
    const agentsList = document.getElementById('agentsList');
    if (!agentsList) return;
    
    agentsList.innerHTML = '';
    
    agents.forEach(agent => {
        const agentItem = document.createElement('div');
        agentItem.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-start';
        agentItem.style.cursor = 'pointer';
        agentItem.setAttribute('data-agent-id', agent.id);
        agentItem.onclick = function(event) {
            selectAgent(agent.id, this);
        };
        
        agentItem.innerHTML = `
            <div class="ms-2 me-auto">
                <div class="fw-bold">${agent.name}</div>
                <small class="text-muted">${agent.description || 'No description'}</small>
            </div>
            <span class="badge ${agent.active ? 'bg-success' : 'bg-secondary'} rounded-pill">
                ${agent.active ? 'Active' : 'Inactive'}
            </span>
        `;
        
        agentsList.appendChild(agentItem);
    });
}

function populateChatAgentSelect() {
    const select = document.getElementById('chatAgentSelect');
    if (!select) return;
    
    // Clear existing options except the first one
    select.innerHTML = '<option value="">Choose an agent to chat with...</option>';
    
    agents.forEach(agent => {
        if (agent.active) {
            const option = document.createElement('option');
            option.value = agent.id;
            option.textContent = agent.name;
            select.appendChild(option);
        }
    });
}

async function selectAgent(agentId, clickedElement = null) {
    try {
        const response = await fetch(`/api/agents/${agentId}`);
        const data = await response.json();
        
        if (data.success) {
            currentAgent = data.agent;
            displayAgentDetails(currentAgent);
            
            // Highlight selected agent
            document.querySelectorAll('#agentsList .list-group-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // If clickedElement is provided, highlight it
            if (clickedElement) {
                clickedElement.classList.add('active');
            } else {
                // Find the element by agent ID and highlight it
                const agentElements = document.querySelectorAll('#agentsList .list-group-item');
                agentElements.forEach(item => {
                    if (item.onclick && item.onclick.toString().includes(agentId)) {
                        item.classList.add('active');
                    }
                });
            }
        } else {
            showStatus('Error loading agent: ' + data.error, 'error');
        }
    } catch (error) {
        showStatus('Error loading agent: ' + error.message, 'error');
    }
}

function displayAgentDetails(agent) {
    const detailsDiv = document.getElementById('agentDetails');
    if (!detailsDiv) return;
    
    detailsDiv.innerHTML = `
        <div class="row g-3">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <h5 class="mb-1">${agent.name}</h5>
                        <p class="text-muted mb-0">${agent.description || 'No description'}</p>
                    </div>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-outline-success" onclick="manageAgentFlows('${agent.id}')">
                            <i class="fas fa-project-diagram"></i> Manage Flows
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteAgent('${agent.id}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="mb-0"><i class="fas fa-cog me-2"></i>System Prompt</h6>
                    <button class="btn btn-sm btn-outline-primary" onclick="editSystemPrompt('${agent.id}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                </div>
                <div class="border rounded p-3 bg-light" style="max-height: 200px; overflow-y: auto;">
                    <div id="systemPrompt-${agent.id}">${agent.system_prompt || 'No system prompt defined'}</div>
                </div>
            </div>
            
            <div class="col-md-6">
                <h6><i class="fas fa-tools me-2"></i>Available Tools</h6>
                <div class="border rounded p-3 bg-light" style="max-height: 200px; overflow-y: auto;">
                    ${agent.tools && agent.tools.length > 0 
                        ? agent.tools.map(tool => `<span class="badge bg-primary me-1 mb-1">${tool}</span>`).join('')
                        : '<small class="text-muted">No tools assigned</small>'
                    }
                </div>
            </div>
            
            <div class="col-md-6">
                <h6><i class="fas fa-project-diagram me-2"></i>Assigned Flows</h6>
                <div class="border rounded p-3 bg-light" style="max-height: 200px; overflow-y: auto;" id="agentFlows-${agent.id}">
                    ${agent.flows && agent.flows.length > 0 
                        ? agent.flows.map(flow => `<span class="badge bg-success me-1 mb-1">${flow}</span>`).join('')
                        : '<small class="text-muted">No flows assigned</small>'
                    }
                </div>
            </div>
            
            <div class="col-12">
                <small class="text-muted">
                    Created: ${new Date(agent.created_at).toLocaleString()} | 
                    Updated: ${new Date(agent.updated_at).toLocaleString()}
                </small>
            </div>
        </div>
    `;
}

async function loadAvailableTools() {
    try {
        const response = await fetch('/api/tools');
        const data = await response.json();
        
        if (data.success) {
            availableTools = data.tools;
        }
    } catch (error) {
        console.error('Error loading tools:', error);
    }
}

function showCreateAgentModal() {
    // Populate tools dropdown
    const toolsSelect = document.getElementById('agentTools');
    if (toolsSelect) {
        toolsSelect.innerHTML = '';
        
        availableTools.forEach(tool => {
            const option = document.createElement('option');
            option.value = tool;
            option.textContent = tool;
            toolsSelect.appendChild(option);
        });
    }
    
    // Show modal with proper configuration
    const modalElement = document.getElementById('createAgentModal');
    if (modalElement) {
        const modal = new bootstrap.Modal(modalElement, {
            backdrop: true,
            keyboard: true,
            focus: true
        });
        modal.show();
    }
}

async function createAgent() {
    const name = document.getElementById('agentName').value.trim();
    const description = document.getElementById('agentDescription').value.trim();
    const systemPrompt = document.getElementById('agentSystemPrompt').value.trim();
    const toolsSelect = document.getElementById('agentTools');
    const selectedTools = Array.from(toolsSelect.selectedOptions).map(option => option.value);
    
    if (!name || !systemPrompt) {
        alert('Please fill in all required fields');
        return;
    }
    
    try {
        const response = await fetch('/api/agents', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                description: description,
                system_prompt: systemPrompt,
                tools: selectedTools
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createAgentModal'));
            modal.hide();
            
            // Clear form
            document.getElementById('createAgentForm').reset();
            
            // Reload agents
            await loadAgents();
            
            showStatus('Agent created successfully!', 'success');
        } else {
            alert('Error creating agent: ' + data.error);
        }
    } catch (error) {
        alert('Error creating agent: ' + error.message);
    }
}

async function deleteAgent(agentId) {
    if (!confirm('Are you sure you want to delete this agent?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/agents/${agentId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadAgents();
            
            // Clear details if this agent was selected
            if (currentAgent && currentAgent.id === agentId) {
                document.getElementById('agentDetails').innerHTML = `
                    <div class="text-center text-muted py-5">
                        <i class="fas fa-robot fa-3x mb-3"></i>
                        <h5>Select an agent to view configuration</h5>
                        <p>Choose an agent from the list to see its details, flows, and tools.</p>
                    </div>
                `;
                currentAgent = null;
            }
            
            showStatus('Agent deleted successfully!', 'success');
        } else {
            alert('Error deleting agent: ' + data.error);
        }
    } catch (error) {
        alert('Error deleting agent: ' + error.message);
    }
}

// ===== CHAT FUNCTIONALITY =====

function switchChatAgent() {
    const select = document.getElementById('chatAgentSelect');
    const selectedAgentId = select.value;
    
    if (selectedAgentId) {
        const agent = agents.find(a => a.id === selectedAgentId);
        if (agent) {
            currentAgent = agent;
            document.getElementById('currentAgentName').textContent = agent.name;
            document.getElementById('chatInterface').style.display = 'block';
            document.getElementById('noAgentSelected').style.display = 'none';
            document.getElementById('agentStatus').style.display = 'inline-flex';
            
            // Clear chat and show welcome message
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = '';
            
            addMessageToChat(`Hello! I'm ${agent.name}. ${agent.description || 'How can I help you today?'}`, 'assistant');
        }
    } else {
        document.getElementById('chatInterface').style.display = 'none';
        document.getElementById('noAgentSelected').style.display = 'block';
        document.getElementById('agentStatus').style.display = 'none';
        currentAgent = null;
    }
}

async function sendMessage() {
    if (!currentAgent) {
        alert('Please select an agent first');
        return;
    }
    
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    input.value = '';
    input.style.height = 'auto';
    
    // Disable send button
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    
    try {
        showTyping();
        
        const response = await fetch(`/api/chat/agent/${currentAgent.id}`, {
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

function handleChatKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function setupChatInput() {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }
}

function showTyping() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'message assistant-message';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar assistant-avatar';
    avatar.innerHTML = '<i class="fas fa-robot"></i>';
    
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

function hideTyping() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// ===== WORKFLOW BUILDER =====

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

async function loadFlow() {
    try {
        showLoading('Loading available flows...');
        
        const response = await fetch('/api/flows');
        const data = await response.json();
        
        if (data.success && data.flows.length > 0) {
            showFlowSelectionModal(data.flows);
        } else {
            showStatus('No flows found.', 'error');
        }
    } catch (error) {
        showStatus('Error loading flows: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function showFlowSelectionModal(flows) {
    // Remove existing modal if any
    const existingModal = document.getElementById('flowSelectionModal');
    if (existingModal) {
        const existingModalInstance = bootstrap.Modal.getInstance(existingModal);
        if (existingModalInstance) {
            existingModalInstance.dispose();
        }
        existingModal.remove();
    }
    
    // Create modal content
    const modalHTML = `
        <div class="modal fade" id="flowSelectionModal" tabindex="-1" aria-labelledby="flowSelectionModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="flowSelectionModalLabel">
                            <i class="fas fa-folder-open me-2"></i>Select Flow to Load
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row g-3">
                            ${flows.map(flow => `
                                <div class="col-12">
                                    <div class="card h-100 flow-card" style="cursor: pointer;" onclick="selectFlowToLoad('${flow.id}')">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-start">
                                                <div>
                                                    <h6 class="card-title mb-2">${flow.name}</h6>
                                                    <p class="card-text text-muted mb-2">${flow.description || 'No description'}</p>
                                                    <small class="text-muted">
                                                        Created: ${flow.created_at ? new Date(flow.created_at).toLocaleString() : 'Unknown'}
                                                    </small>
                                                </div>
                                                <button class="btn btn-primary btn-sm">
                                                    <i class="fas fa-download"></i> Load
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Show modal
    const modalElement = document.getElementById('flowSelectionModal');
    const modal = new bootstrap.Modal(modalElement, {
        backdrop: true,
        keyboard: true,
        focus: true
    });
    
    // Clean up when modal is hidden
    modalElement.addEventListener('hidden.bs.modal', function () {
        modalElement.remove();
    });
    
    modal.show();
}

async function selectFlowToLoad(flowId) {
    try {
        showLoading('Loading flow configuration...');
        
        const response = await fetch(`/api/flows/${flowId}`);
        const data = await response.json();
        
        if (data.success && data.flow) {
            currentFlowConfig = data.flow;
            displayFlowConfig(currentFlowConfig);
            document.getElementById('saveFlowBtn').disabled = false;
            showStatus('Flow configuration loaded successfully!', 'success');
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('flowSelectionModal'));
            if (modal) {
                modal.hide();
            }
        } else {
            showStatus('Error loading flow: ' + (data.error || 'Flow not found'), 'error');
        }
    } catch (error) {
        showStatus('Error loading flow: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

function displayFlowConfig(config) {
    const configDiv = document.getElementById('generatedConfig');
    if (typeof config === 'string') {
        configDiv.textContent = config;
    } else {
        configDiv.textContent = JSON.stringify(config, null, 2);
    }
}

// ===== UTILITY FUNCTIONS =====

function showLoading(message) {
    showStatus(message, 'loading');
}

function hideLoading() {
    const statusDiv = document.getElementById('configStatus');
    if (statusDiv) {
        statusDiv.innerHTML = '';
    }
}

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

// ===== AGENT EDITING FUNCTIONS =====

function editSystemPrompt(agentId) {
    const agent = agents.find(a => a.id === agentId);
    if (!agent) return;
    
    const promptDiv = document.getElementById(`systemPrompt-${agentId}`);
    const currentPrompt = agent.system_prompt || '';
    
    // Create textarea for editing
    promptDiv.innerHTML = `
        <textarea class="form-control mb-2" id="editPrompt-${agentId}" rows="6">${currentPrompt}</textarea>
        <div class="d-flex gap-2">
            <button class="btn btn-sm btn-success" onclick="saveSystemPrompt('${agentId}')">
                <i class="fas fa-save"></i> Save
            </button>
            <button class="btn btn-sm btn-secondary" onclick="cancelEditPrompt('${agentId}')">
                <i class="fas fa-times"></i> Cancel
            </button>
        </div>
    `;
}

async function saveSystemPrompt(agentId) {
    const textarea = document.getElementById(`editPrompt-${agentId}`);
    const newPrompt = textarea.value.trim();
    
    if (!newPrompt) {
        alert('System prompt cannot be empty');
        return;
    }
    
    try {
        const response = await fetch(`/api/agents/${agentId}/system-prompt`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ system_prompt: newPrompt })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update local agent data
            const agent = agents.find(a => a.id === agentId);
            if (agent) {
                agent.system_prompt = newPrompt;
            }
            
            // Update display
            const promptDiv = document.getElementById(`systemPrompt-${agentId}`);
            promptDiv.innerHTML = newPrompt;
            
            showStatus('System prompt updated successfully!', 'success');
        } else {
            alert('Error updating system prompt: ' + data.error);
        }
    } catch (error) {
        alert('Error updating system prompt: ' + error.message);
    }
}

function cancelEditPrompt(agentId) {
    const agent = agents.find(a => a.id === agentId);
    if (!agent) return;
    
    const promptDiv = document.getElementById(`systemPrompt-${agentId}`);
    promptDiv.innerHTML = agent.system_prompt || 'No system prompt defined';
}

async function manageAgentFlows(agentId) {
    try {
        // Load available flows
        const flowsResponse = await fetch('/api/flows');
        const flowsData = await flowsResponse.json();
        
        if (!flowsData.success) {
            alert('Error loading flows: ' + flowsData.error);
            return;
        }
        
        const agent = agents.find(a => a.id === agentId);
        if (!agent) return;
        
        // Remove existing modal if any
        const existingModal = document.getElementById('manageFlowsModal');
        if (existingModal) {
            const existingModalInstance = bootstrap.Modal.getInstance(existingModal);
            if (existingModalInstance) {
                existingModalInstance.dispose();
            }
            existingModal.remove();
        }
        
        // Create modal content
        const modalHTML = `
            <div class="modal fade" id="manageFlowsModal" tabindex="-1" aria-labelledby="manageFlowsModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="manageFlowsModalLabel">
                                <i class="fas fa-project-diagram me-2"></i>Manage Flows for ${agent.name}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Available Flows</h6>
                                    <div class="border rounded p-3" style="max-height: 300px; overflow-y: auto;">
                                        ${flowsData.flows.map(flow => `
                                            <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded ${agent.flows.includes(flow.id) ? 'bg-light' : ''}">
                                                <div>
                                                    <strong>${flow.name}</strong>
                                                    <br><small class="text-muted">${flow.description || 'No description'}</small>
                                                </div>
                                                <button class="btn btn-sm ${agent.flows.includes(flow.id) ? 'btn-outline-danger' : 'btn-outline-success'}" 
                                                        onclick="toggleFlowAssignment('${agentId}', '${flow.id}', ${agent.flows.includes(flow.id)})">
                                                    <i class="fas ${agent.flows.includes(flow.id) ? 'fa-minus' : 'fa-plus'}"></i>
                                                </button>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <h6>Assigned Flows</h6>
                                    <div class="border rounded p-3" style="max-height: 300px; overflow-y: auto;" id="assignedFlowsList">
                                        ${agent.flows.length > 0 
                                            ? agent.flows.map(flowId => {
                                                const flow = flowsData.flows.find(f => f.id === flowId);
                                                return flow ? `
                                                    <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded bg-success text-white">
                                                        <div>
                                                            <strong>${flow.name}</strong>
                                                            <br><small>${flow.description || 'No description'}</small>
                                                        </div>
                                                        <button class="btn btn-sm btn-light" onclick="toggleFlowAssignment('${agentId}', '${flowId}', true)">
                                                            <i class="fas fa-times text-danger"></i>
                                                        </button>
                                                    </div>
                                                ` : '';
                                            }).join('')
                                            : '<p class="text-muted">No flows assigned</p>'
                                        }
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Show modal with proper initialization
        const modalElement = document.getElementById('manageFlowsModal');
        const modal = new bootstrap.Modal(modalElement, {
            backdrop: true,
            keyboard: true,
            focus: true
        });
        
        // Clean up when modal is hidden
        modalElement.addEventListener('hidden.bs.modal', function () {
            modalElement.remove();
        });
        
        modal.show();
        
        // Store flows data globally for the modal functions
        window.currentFlowsData = flowsData.flows;
        
    } catch (error) {
        console.error('Error loading flows:', error);
        alert('Error loading flows: ' + error.message);
    }
}

async function toggleFlowAssignment(agentId, flowId, isCurrentlyAssigned) {
    try {
        const method = isCurrentlyAssigned ? 'DELETE' : 'POST';
        const response = await fetch(`/api/agents/${agentId}/flows/${flowId}`, {
            method: method
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update local agent data
            const agent = agents.find(a => a.id === agentId);
            if (agent) {
                if (isCurrentlyAssigned) {
                    agent.flows = agent.flows.filter(f => f !== flowId);
                } else {
                    if (!agent.flows.includes(flowId)) {
                        agent.flows.push(flowId);
                    }
                }
            }
            
            // Close current modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('manageFlowsModal'));
            if (modal) {
                modal.hide();
            }
            
            // Wait a bit then reopen with updated data
            setTimeout(() => {
                manageAgentFlows(agentId);
            }, 300);
            
            // Update agent details if currently displayed
            if (currentAgent && currentAgent.id === agentId) {
                displayAgentDetails(agent);
            }
            
            const action = isCurrentlyAssigned ? 'removed' : 'assigned';
            showStatus(`Flow ${action} successfully!`, 'success');
        } else {
            alert('Error updating flow assignment: ' + data.error);
        }
    } catch (error) {
        console.error('Error updating flow assignment:', error);
        alert('Error updating flow assignment: ' + error.message);
    }
}