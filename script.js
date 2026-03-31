const chatHistory = document.getElementById('chat-history');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const typingIndicator = document.getElementById('typing-indicator');
const brainCountBtn = document.getElementById('brain-count');
const chatFileInput = document.getElementById('chat-file-input');
const attachmentTray = document.getElementById('attachment-tray');
const allowAiExtractionCheckbox = document.getElementById('allow-ai-extraction');

let stagedFiles = [];
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const resetBtn = document.getElementById('reset-btn');

function appendMessage(role, contentHTML, graphUrls = [], aiImageUrl = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}-msg fade-in`;
    
    let innerHtml = `<div class="msg-content">${contentHTML}`;
    
    // Add Graphs
    if (graphUrls) {
        const urls = Array.isArray(graphUrls) ? graphUrls : [graphUrls];
        urls.forEach((url, idx) => {
            if (url) innerHtml += `<img src="${url}?t=${new Date().getTime()}&i=${idx}" alt="AI Generated Graph">`;
        });
    }

    // Add AI Image
    if (aiImageUrl) {
        innerHtml += `<img src="${aiImageUrl}?t=${new Date().getTime()}" alt="AI Generated Picture" style="border-color: #8B5CF6; border-width: 2px;">`;
    }

    innerHtml += `</div>`;
    
    msgDiv.innerHTML = innerHtml;
    // Insert before typing indicator
    chatHistory.insertBefore(msgDiv, typingIndicator);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function sendMessage(text) {
    if (!text.trim() && stagedFiles.length === 0) return;
    
    let userHtml = text ? marked.parse(text) : "<em>(Sent Attachments)</em>";
    if (stagedFiles.length > 0) {
        userHtml += `<br><small style="color:#93C5FD"><i class="fa-solid fa-paperclip"></i> Attached ${stagedFiles.length} file(s)</small>`;
    }

    appendMessage('user', userHtml);
    chatInput.value = '';
    
    // Build multipart package
    const formData = new FormData();
    formData.append('message', text);
    formData.append('allow_ai_extraction', allowAiExtractionCheckbox && allowAiExtractionCheckbox.checked ? 'true' : 'false');
    stagedFiles.forEach(f => formData.append('files', f));
    
    // Clear the tray
    stagedFiles = [];
    renderAttachmentTray();
    
    chatHistory.appendChild(typingIndicator);
    typingIndicator.style.display = 'flex';
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    try {
        const res = await fetch('/chat', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        
        typingIndicator.style.display = 'none';
        
        if (data.error) {
            appendMessage('assistant', `<span style="color: #ef4444">System Core Error: ${data.error}</span>`);
        } else if (data.status === 'PENDING_APPROVAL') {
            appendSecurityPrompt(data);
        } else {
            appendMessage('assistant', marked.parse(data.response), data.graphs || (data.graph ? [data.graph] : []), data.ai_image);
            updateStatus(); 
        }
    } catch (e) {
        typingIndicator.style.display = 'none';
        appendMessage('assistant', `<span style="color: #ef4444">Network Error: Hub disconnected.</span>`);
    }
}

function appendSecurityPrompt(data) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message assistant-msg fade-in`;
    
    msgDiv.innerHTML = `
        <div class="msg-content">
            <div class="security-halt-card">
                <h4><i class="fa-solid fa-shield-halved"></i> Security Halt: Action Required</h4>
                <div class="reason">${data.reason}</div>
                <div class="command-preview"><code>${data.command}</code></div>
                <div class="security-actions">
                    <button class="glass-btn btn-approve" onclick="approveCommand('${data.tool_call_id}', '${data.command.replace(/'/g, "\\'")}')">
                        <i class="fa-solid fa-check"></i> Approve
                    </button>
                    <button class="glass-btn btn-reject" onclick="rejectCommand('${data.tool_call_id}')">
                        <i class="fa-solid fa-xmark"></i> Reject
                    </button>
                </div>
            </div>
        </div>
    `;
    
    chatHistory.insertBefore(msgDiv, typingIndicator);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function approveCommand(toolCallId, command) {
    // Show typing again
    chatHistory.appendChild(typingIndicator);
    typingIndicator.style.display = 'flex';
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // Remove buttons from the prompt to prevent double clicks
    const actions = document.querySelector('.security-actions');
    if (actions) actions.style.display = 'none';

    try {
        const res = await fetch('/approve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ choice: 'approve', tool_call_id: toolCallId, command: command })
        });
        const data = await res.json();
        
        typingIndicator.style.display = 'none';
        if (data.status === 'PENDING_APPROVAL') {
            appendSecurityPrompt(data);
        } else {
            appendMessage('assistant', marked.parse(data.response), data.graphs || (data.graph ? [data.graph] : []), data.ai_image);
        }
    } catch (e) {
        typingIndicator.style.display = 'none';
        appendMessage('assistant', `<span style="color: #ef4444">Approval failed: Connection error.</span>`);
    }
}

async function rejectCommand(toolCallId) {
    chatHistory.appendChild(typingIndicator);
    typingIndicator.style.display = 'flex';
    
    const actions = document.querySelector('.security-actions');
    if (actions) actions.innerHTML = '<span style="color: #ef4444">Command Rejected.</span>';

    try {
        const res = await fetch('/approve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ choice: 'reject', tool_call_id: toolCallId })
        });
        const data = await res.json();
        typingIndicator.style.display = 'none';
        appendMessage('assistant', marked.parse(data.response));
    } catch (e) {
        typingIndicator.style.display = 'none';
        appendMessage('assistant', `<span style="color: #ef4444">Rejection sync failed.</span>`);
    }
}

sendBtn.addEventListener('click', () => sendMessage(chatInput.value));
// ... (rest of listeners)
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage(chatInput.value);
});

// Queue System Listeners
chatFileInput.addEventListener('change', () => {
    Array.from(chatFileInput.files).forEach(file => {
        stagedFiles.push(file);
    });
    renderAttachmentTray();
    chatFileInput.value = '';
});

function renderAttachmentTray() {
    attachmentTray.innerHTML = '';
    stagedFiles.forEach((file, idx) => {
        const pill = document.createElement('div');
        pill.className = 'attachment-pill fade-in';
        pill.innerHTML = `
            <i class="fa-solid fa-file"></i> ${file.name}
            <div class="remove-pill" onclick="removeStagedFile(${idx})"><i class="fa-solid fa-xmark"></i></div>
        `;
        attachmentTray.appendChild(pill);
    });
}

window.removeStagedFile = function(idx) {
    stagedFiles.splice(idx, 1);
    renderAttachmentTray();
}

async function updateStatus() {
    try {
        const res = await fetch('/status');
        const data = await res.json();
        brainCountBtn.textContent = data.brain_count;
    } catch (e) {
        console.error("Status sync failed:", e);
    }
}

// Custom Upload UI Logic
uploadZone.addEventListener('click', () => fileInput.click());

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.style.borderColor = '#3B82F6';
    uploadZone.style.background = 'rgba(59, 130, 246, 0.1)';
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.style.borderColor = 'rgba(255, 255, 255, 0.2)';
    uploadZone.style.background = 'transparent';
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.style.borderColor = 'rgba(255, 255, 255, 0.2)';
    uploadZone.style.background = 'transparent';
    if (e.dataTransfer.files.length) handleUpload(Array.from(e.dataTransfer.files));
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length) handleUpload(Array.from(fileInput.files));
});

async function handleUpload(files) {
    if (!files.length) return;

    const label = files.length === 1
        ? `<em>(Securely Uploaded System File: ${files[0].name})</em>`
        : `<em>(Securely Uploaded ${files.length} files: ${files.map(file => file.name).join(', ')})</em>`;
    appendMessage('user', label);
    
    chatHistory.appendChild(typingIndicator);
    typingIndicator.style.display = 'flex';
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    const formData = new FormData();
    formData.append('allow_ai_extraction', allowAiExtractionCheckbox && allowAiExtractionCheckbox.checked ? 'true' : 'false');
    files.forEach(file => formData.append('files', file));
    
    try {
        const res = await fetch('/upload', { method: 'POST', body: formData });
        const data = await res.json();
        
        typingIndicator.style.display = 'none';
        if (data.error) {
            appendMessage('assistant', `<span style="color: #ef4444">Parsing Error: ${data.error}</span>`);
        } else if (data.status === 'PENDING_APPROVAL') {
            appendSecurityPrompt(data);
        } else {
            appendMessage('assistant', marked.parse(data.response), data.graphs || (data.graph ? [data.graph] : []));
        }
    } catch (e) {
        typingIndicator.style.display = 'none';
        appendMessage('assistant', `<span style="color: #ef4444">Upload Interrupted.</span>`);
    }
}

resetBtn.addEventListener('click', async () => {
    await fetch('/reset', { method: 'POST' });
    
    // Clear display except for the first msg
    const messages = chatHistory.querySelectorAll('.message');
    messages.forEach((msg, idx) => {
        if (idx > 0) msg.remove();
    });
    
    appendMessage('assistant', 'Short-term memory wiped. My local RAG brain protocols remain intact.');
});

// Boot check
updateStatus();
