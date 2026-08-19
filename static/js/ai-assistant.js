/**
 * ==========================================================================
 * ACCESSPATH - AI ASSISTANT DISABILITY ADVISOR ENGINE (INTEGRATED VERSION)
 * Connects directly to the Flask backend Gemini AI agent to provide real-time,
 * automated assistance. Handles security halt approvals and speech output.
 * ==========================================================================
 */

class AiAssistantEngine {
  constructor() {
    this.chatHistory = [];
  }

  async askQuestionAsync(userText, appendBubbleCallback, removeTypingCallback, appendSecurityCallback) {
    if (!userText || !userText.trim()) return;

    try {
      const formData = new FormData();
      formData.append('message', userText);
      formData.append('allow_ai_extraction', 'false');

      const res = await fetch('/chat', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();

      removeTypingCallback();

      if (data.error) {
        appendBubbleCallback('ai', `<span style="color: #ff3366;">Error: ${data.error}</span>`);
      } else if (data.status === 'PENDING_APPROVAL') {
        appendSecurityCallback(data);
      } else {
        let content = data.response;
        // Parse markdown if marked is loaded
        if (window.marked && window.marked.parse) {
          content = window.marked.parse(content);
        } else {
          content = content.replace(/\n/g, '<br>');
        }

        // Add Graphs if present
        if (data.graphs || data.graph) {
          const urls = data.graphs || [data.graph];
          urls.forEach((url, idx) => {
            if (url) {
              const alt = (data.graph_alts && data.graph_alts[idx]) ? data.graph_alts[idx] : `AI generated graph ${idx+1}`;
              content += `<br><img src="${url}?t=${new Date().getTime()}&i=${idx}" alt="${alt}" style="max-width: 100%; border: 2px solid var(--border-color); border-radius: 4px; margin-top: 10px;">`;
            }
          });
        }

        // Add AI Image if present
        if (data.ai_image) {
          content += `<br><img src="${data.ai_image}?t=${new Date().getTime()}" alt="AI generated image" style="max-width: 100%; border: 2px solid var(--border-color); border-radius: 4px; margin-top: 10px;">`;
        }

        appendBubbleCallback('ai', content);

        if (window.jawsEngine) {
          // Speak plain text without HTML tags
          const tempDiv = document.createElement('div');
          tempDiv.innerHTML = content;
          const plainSpeech = tempDiv.textContent || tempDiv.innerText || '';
          window.jawsEngine.speak(plainSpeech);
        }
      }
    } catch (e) {
      removeTypingCallback();
      appendBubbleCallback('ai', `<span style="color: #ff3366;">Connection Error: AI Advisor is offline.</span>`);
    }
  }

  async approveCommand(toolCallId, command, appendBubbleCallback, removeTypingCallback, appendSecurityCallback) {
    try {
      const res = await fetch('/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ choice: 'approve', tool_call_id: toolCallId, command: command })
      });
      const data = await res.json();

      removeTypingCallback();

      if (data.status === 'PENDING_APPROVAL') {
        appendSecurityCallback(data);
      } else {
        let content = data.response || data.error || "";
        if (window.marked && window.marked.parse) {
          content = window.marked.parse(content);
        } else {
          content = content.replace(/\n/g, '<br>');
        }
        appendBubbleCallback('ai', content);

        if (window.jawsEngine) {
          const tempDiv = document.createElement('div');
          tempDiv.innerHTML = content;
          const plainSpeech = tempDiv.textContent || tempDiv.innerText || '';
          window.jawsEngine.speak(plainSpeech);
        }
      }
    } catch (e) {
      removeTypingCallback();
      appendBubbleCallback('ai', `<span style="color: #ff3366;">Approval failed: Connection error.</span>`);
    }
  }

  async rejectCommand(toolCallId, appendBubbleCallback, removeTypingCallback, appendSecurityCallback) {
    try {
      const res = await fetch('/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ choice: 'reject', tool_call_id: toolCallId })
      });
      const data = await res.json();

      removeTypingCallback();

      if (data.status === 'PENDING_APPROVAL') {
        appendSecurityCallback(data);
      } else {
        let content = data.response || data.error || "";
        if (window.marked && window.marked.parse) {
          content = window.marked.parse(content);
        } else {
          content = content.replace(/\n/g, '<br>');
        }
        appendBubbleCallback('ai', content);

        if (window.jawsEngine) {
          const tempDiv = document.createElement('div');
          tempDiv.innerHTML = content;
          const plainSpeech = tempDiv.textContent || tempDiv.innerText || '';
          window.jawsEngine.speak(plainSpeech);
        }
      }
    } catch (e) {
      removeTypingCallback();
      appendBubbleCallback('ai', `<span style="color: #ff3366;">Rejection failed: Connection error.</span>`);
    }
  }
}

window.aiAssistantEngine = new AiAssistantEngine();
