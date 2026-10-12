document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const cursorGlow = document.getElementById('cursor-glow');

    // 1. Mouse Tracking Glow (Parallax)
    if (cursorGlow) {
        window.addEventListener('mousemove', (e) => {
            gsap.to(cursorGlow, {
                x: e.clientX,
                y: e.clientY,
                duration: 0.8,
                ease: "power2.out"
            });
        });
    }

    // 2. Animate initial message
    const initialMsg = document.querySelector('.initial-message');
    if (initialMsg) {
        gsap.to(initialMsg, {
            opacity: 1,
            y: 0,
            duration: 0.6,
            ease: "back.out(1.2)"
        });
    }

    // 3. Auto-resize Textarea
    chatInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';

        // Enable/disable send button
        if (this.value.trim().length > 0) {
            sendBtn.removeAttribute('disabled');
        } else {
            sendBtn.setAttribute('disabled', 'true');
        }
    });

    // Handle Enter to send (Shift+Enter for newline)
    chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (this.value.trim().length > 0) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    let apiToken = null;

    async function ensureToken() {
        if (apiToken) return apiToken;
        try {
            const params = new URLSearchParams();
            params.append('username', 'dev@cca.com');
            params.append('password', 'CCA_WELCOMES');

            const res = await fetch('http://127.0.0.1:8000/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: params.toString()
            });
            const data = await res.json();
            apiToken = data.access_token;
            return apiToken;
        } catch (e) {
            console.error("Login failed", e);
            return null;
        }
    }

    async function loadChatHistory() {
        const token = await ensureToken();
        if (!token) return;
        try {
            const res = await fetch('http://127.0.0.1:8000/chat/history', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data && data.messages) {
                // Remove the initial static message if history exists
                if (data.messages.length > 0 && initialMsg) {
                    initialMsg.style.display = 'none';
                }
                data.messages.forEach(msg => {
                    const sender = msg.role === 'user' ? 'user' : 'ai';
                    appendMessage(sender, msg.content, false);
                });
            }
        } catch (e) {
            console.error("Failed to load history", e);
        }
    }

    // Load history on startup
    loadChatHistory();

    // 4. Handle sending a message
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text) return;

        appendMessage('user', text);

        // Reset input
        chatInput.value = '';
        chatInput.style.height = 'auto';
        sendBtn.setAttribute('disabled', 'true');

        // Show typing indicator
        showTypingIndicator();

        const token = await ensureToken();
        if (!token) {
            hideTypingIndicator();
            appendMessage('ai', 'Error: Unable to connect to authentication server. Is the backend running?');
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ query: text })
            });

            hideTypingIndicator();

            if (!response.ok) {
                appendMessage('ai', `Error: ${response.statusText}`);
                return;
            }

            // Create a message bubble for the AI stream
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ai-message`;
            msgDiv.innerHTML = `
                <div class="msg-avatar"><i class="fa-solid fa-leaf"></i></div>
                <div class="msg-content markdown-body"></div>
            `;
            chatMessages.appendChild(msgDiv);
            // Trigger GSAP Pop-in animation immediately so it's visible while streaming
            gsap.fromTo(msgDiv,
                { opacity: 0, y: 10 },
                { opacity: 1, y: 0, duration: 0.5, ease: "back.out(1.5)" }
            );

            const contentDiv = msgDiv.querySelector('.msg-content');

            let fullText = "";
            let uiText = "";
            let buffer = "";

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // keep the last incomplete line in the buffer

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const parsed = JSON.parse(line);
                        if (parsed.type === "text") {
                            fullText += parsed.content;
                            contentDiv.innerHTML = uiText + (window.marked ? marked.parse(fullText) : fullText);
                        } else if (parsed.type === "ui" || parsed.type === "source") {
                            uiText += `<div style="color: #888; font-size: 0.85em; font-style: italic; margin-bottom: 8px;">${escapeHTML(parsed.content)}</div>`;
                            contentDiv.innerHTML = uiText + (window.marked ? marked.parse(fullText) : fullText);
                        }
                    } catch (err) {
                        console.error("JSON parse error on line:", line, err);
                    }
                }
                scrollToBottom();
            }

        } catch (e) {
            hideTypingIndicator();
            appendMessage('ai', `Connection Error: ${e.message}`);
        }
    });

    // Append Message with Snapchat/Telegram style bounce animation
    function appendMessage(sender, text, animate = true) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message`;

        let avatarIcon = sender === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-leaf"></i>';

        const contentHtml = sender === 'ai' && window.marked ? marked.parse(text) : escapeHTML(text);

        msgDiv.innerHTML = `
            <div class="msg-avatar">${avatarIcon}</div>
            <div class="msg-content">${contentHtml}</div>
        `;

        chatMessages.appendChild(msgDiv);
        scrollToBottom();

        if (animate) {
            // GSAP Pop-in animation
            gsap.to(msgDiv, {
                opacity: 1,
                y: 0,
                duration: 0.5,
                ease: "back.out(1.5)"
            });
        } else {
            msgDiv.style.opacity = 1;
            msgDiv.style.transform = "translateY(0)";
        }
    }

    function showTypingIndicator() {
        typingIndicator.style.display = 'flex';
        gsap.to(typingIndicator, {
            opacity: 1,
            y: 0,
            duration: 0.3,
            ease: "power2.out"
        });
        scrollToBottom();
    }

    function hideTypingIndicator() {
        gsap.to(typingIndicator, {
            opacity: 0,
            y: 10,
            duration: 0.2,
            onComplete: () => {
                typingIndicator.style.display = 'none';
            }
        });
    }

    function scrollToBottom() {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }

    // Helper to prevent XSS in fake chat
    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g,
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }

    // 5. Check URL parameters for an initial query
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q');
    if (query) {
        chatInput.value = query;
        sendBtn.removeAttribute('disabled');
        // Submit immediately
        setTimeout(() => {
            chatForm.dispatchEvent(new Event('submit'));
        }, 500); // slight delay for visual effect
    }

    // Microphone Functionality
    const micBtn = document.querySelector('.mic-btn');
    if (micBtn && chatInput) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            let isRecording = false;
            let pulseTween;

            micBtn.addEventListener('click', () => {
                if (isRecording) {
                    recognition.stop();
                } else {
                    recognition.start();
                }
            });

            recognition.onstart = () => {
                isRecording = true;
                chatInput.placeholder = "Listening...";
                micBtn.style.color = '#ff5e5e';
                pulseTween = gsap.to(micBtn, { scale: 1.2, duration: 0.5, yoyo: true, repeat: -1 });
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                chatInput.value = transcript;
                sendBtn.removeAttribute('disabled'); // Enable send button if we got text
            };

            recognition.onend = () => {
                isRecording = false;
                micBtn.style.color = '';
                if (pulseTween) pulseTween.kill();
                gsap.to(micBtn, { scale: 1, duration: 0.2 });
                chatInput.placeholder = "Message Healthy Food AI...";
            };

            recognition.onerror = (event) => {
                console.error("Speech recognition error", event.error);
                isRecording = false;
                micBtn.style.color = '';
                if (pulseTween) pulseTween.kill();
                gsap.to(micBtn, { scale: 1, duration: 0.2 });
                chatInput.placeholder = "Message Healthy Food AI...";
            };
        } else {
            micBtn.addEventListener('click', () => {
                alert("Speech Recognition API is not supported in this browser.");
            });
        }
    }
});
