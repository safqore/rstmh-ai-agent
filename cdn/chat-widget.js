(function() {
  const style = document.createElement('style');
  style.innerHTML = `
  #safqore-chat-wrapper {
      position: relative;
      font-family: Arial, sans-serif;
      font-size: 16px;
      line-height: 1.4;
    }

    /* Chat window - default hidden state */
    #safqore-chat-wrapper .chat-window {
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 426px;
      min-width: 350px;
      max-height: 700px;
      min-height: 400px;
      background: #fff;
      border: none;
      border-radius: 10px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
      display: none;
      flex-direction: column;
      z-index: 9999;
      overflow: hidden;
      font-size: 0.9rem;
      color: #3f4748;
      font-family: "Arial", sans-serif;
      transform: translateY(100%);
      transition: transform 0.3s ease, opacity 0.3s ease;
      opacity: 0;
    }

    /* Open state */
    #safqore-chat-wrapper .chat-window.open {
      display: flex;
      transform: translateY(0);
      opacity: 1;
    }

    /* Chat bubble */
    #safqore-chat-wrapper .chat-bubble {
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: #881c34;
      color: #fff;
      padding: 12px 16px;
      border-radius: 20px;
      cursor: pointer;
      font-family: "Arial", sans-serif;
      font-size: 1rem;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
      display: flex;
      align-items: center;
      z-index: 9999;
      animation: pulse-button 4s infinite;
      transition: background 0.3s ease, opacity 0.3s ease;
    }


    #safqore-chat-wrapper .chat-bubble:hover {
      background: #881c34;
      transform: scale(1.05);
    }

    /* Mobile responsiveness */
    @media (max-width: 600px) {
      #safqore-chat-wrapper .chat-window {
        width: 100%;
        height: 100%;
        right: 0;
        bottom: 0;
        border-radius: 0;
        max-height: none;
      }
    }

    @keyframes pulse-button {
      0% {
        box-shadow: 0 0 0 0 rgba(74, 94, 229, 0.7);
      }
      50% {
        box-shadow: 0 0 15px 10px rgba(74, 94, 229, 0.3);
      }
      100% {
        box-shadow: 0 0 0 0 rgba(74, 94, 229, 0.7);
      }
    }

    #safqore-chat-wrapper .chat-bubble .icon {
      margin-right: 8px;
    }

    /* Header with gradient background */
    #safqore-chat-wrapper .chat-header {
      background: #006778;
      color: #fff;
      font-family: "Arial", sans-serif;
      font-size: 1.1rem;
      padding: 16px;
      position: relative;
    }


    #safqore-chat-wrapper .chat-header .header-text h2 {
      margin: 0 0 4px 0;
      font-size: 1.1rem;
      font-weight: normal;
    }

    #safqore-chat-wrapper .chat-header .header-text p {
      margin: 0;
      font-size: 0.85rem;
    }

    #safqore-chat-wrapper .close-btn {
      position: absolute;
      top: 8px;
      right: 8px;
      background: transparent;
      border: none;
      color: #fff;
      font-size: 1.4rem;
      cursor: pointer;
    }

    #safqore-chat-wrapper .chat-body {
      font-family: "Arial", sans-serif;
      color: #3f4748;
      flex: 1;
      padding: 10px;
      overflow-y: auto;
      background: #fff;
      line-height: 1.5;
    }


    #safqore-chat-wrapper .chat-message {
      margin-bottom: 12px;
      line-height: 1.4;
    }

    #safqore-chat-wrapper .chat-message span {
      display: inline-block;
      padding: 10px 12px;
      border-radius: 12px;
      background: #f0f0f0;
      color: #333;
      font-size: 0.9rem;
    }

    #safqore-chat-wrapper .chat-message.user {
      text-align: right; /* Align the user message to the right */
      padding-right: 12px; /* Space between the message bubble and the right edge */
      margin-left: auto; /* Add space to the left of the user message */
      max-width: 85%; /* Prevent the bubble from stretching across the full width */
    }

    #safqore-chat-wrapper .chat-message.user span {
      display: inline-block;
      background: #006778; /* User message background color */
      color: #fff; /* User message text color */
      padding: 10px 12px;
      border-radius: 12px 12px 0 12px; /* Top-left, top-right, bottom-right, bottom-left */
      word-wrap: break-word; /* Ensure text wraps nicely */
      line-height: 1.5;
    }

    #safqore-chat-wrapper .chat-message.bot {
      text-align: left;
      margin-right: auto;
      margin-left: 10px;
      max-width: 85%;
      background: #f9f9f9;
      padding: 12px;
      border-radius: 12px 12px 12px 0; /* Top-left, top-right, bottom-right, bottom-left */
      border: 1px solid #e0e0e0;
      box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
    }

    /* Bot Response Styling */
    #safqore-chat-wrapper .formatted-response h3 {
      font-size: 1rem;
      color: #4A5EE5;
      margin: 5px 0; /* Reduced margin */
      font-weight: bold;
    }

    #safqore-chat-wrapper .formatted-response h4 {
      font-size: 0.9rem;
      color: #333;
      margin: 4px 0; /* Reduced margin */
    }

    #safqore-chat-wrapper .formatted-response ul {
      list-style-type: disc;
      margin: 5px 0; /* Reduced margin around list */
      padding-left: 20px; /* Maintain indentation */
    }

    #safqore-chat-wrapper .formatted-response ol {
      list-style-type: decimal;
      margin: 5px 0; /* Reduced margin */
      padding-left: 20px;
    }

    #safqore-chat-wrapper .formatted-response li {
      margin-bottom: 3px; /* Reduce space between list items */
      line-height: 1.5; /* Slightly tighter line spacing */
    }

    #safqore-chat-wrapper .formatted-response strong {
      font-weight: bold;
      color: #333;
    }

    #safqore-chat-wrapper .formatted-response br {
      margin-bottom: 2px; /* Minimized extra space from line breaks */
    }

    #safqore-chat-wrapper .chat-footer {
      padding: 10px;
      background: #fff;
      border-top: 1px solid #eee;
      display: flex;
      flex-direction: column;
      gap: 6px;
      position: relative;
    }
    
    /* Links and Highlights */
    #safqore-chat-wrapper a {
      color: #00adcd;
      text-decoration: none;
    }

    #safqore-chat-wrapper a:hover {
      text-decoration: underline;
    }

    /* Input row without attach button */
    #safqore-chat-wrapper .input-row {
      display: flex;
      align-items: center;
      background: #f9f9f9;
      border-radius: 20px;
      padding: 4px;
      border: 1px solid #ddd;
    }

    #safqore-chat-wrapper .chat-input {
      flex: 1;
      border: none;
      background: transparent;
      outline: none;
      padding: 8px;
      font-size: 0.9rem;
    }

    #safqore-chat-wrapper .send-btn {
      background: transparent;
      border: none;
      cursor: pointer;
      color: #666;
      font-size: 1.1rem;
      width: 32px;
      height: 32px;
      text-align: center;
      line-height: 32px;
      padding: 0;
      border-radius: 50%;
      transition: background 0.2s ease;
    }

    #safqore-chat-wrapper .send-btn:hover {
      background: #eee;
    }

    #safqore-chat-wrapper .powered-by {
      font-size: 0.75rem;
      color: #aaa;
      text-align: center;
    }

    #safqore-chat-wrapper .powered-by a {
      color: #aaa; /* Link color */
      text-decoration: underline; /* Add underline on hover */
    }

    #safqore-chat-wrapper .powered-by a:hover {
      text-decoration: underline; /* Add underline on hover */
      font-weight: bold;
      color: #aaa; /* Slightly darker teal on hover */
    }


    .typing-indicator {
      display: flex;
      align-items: center;
      gap: 5px;
      font-size: 0.85rem;
      color: #aaa;
      margin-top: 5px;
    }

    .typing-indicator .dot {
      width: 6px;
      height: 6px;
      background-color: #aaa;
      border-radius: 50%;
      animation: blink 1.4s infinite;
    }
  `;
  document.head.appendChild(style);

  const wrapper = document.createElement('div');
  wrapper.id = 'safqore-chat-wrapper';
  wrapper.innerHTML = `
    <div class="chat-bubble" id="chat-bubble">
      <span class="icon">💬</span>Grant Application Questions? Let’s Chat!
    </div>
    <div class="chat-window" id="chat-window">
      <div class="chat-header">
        <div class="header-text">
          <h2>RSTMH Grants - AI Agent Assistant ✨</h2>
        </div>
        <button id="close-chat" class="close-btn">&times;</button>
      </div>
      <div class="chat-body"></div>
      <div class="chat-footer">
        <div class="typing-indicator" id="typing-indicator" style="display: none;">
          <div>Agent is typing</div>
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        <div class="input-row">
          <input type="text" placeholder="Send a message..." class="chat-input"/>
          <button class="send-btn" title="Send">➤</button>
        </div>
        <div class="powered-by">Powered By <a href="https://www.safqore.com" target="_blank">Safqore AI</a></div>
      </div>
    </div>
  `;
  document.body.appendChild(wrapper);

  function formatLLMResponse(text) {
    return text
      .replace(/(\s*<br>\s*)+/g, '<br>') // Replace multiple <br> tags with a single <br>
      .replace(/^##\s(.+)$/gm, '<h3>$1</h3>') // Convert '## Heading' to <h3>
      .replace(/^###\s(.+)$/gm, '<h4>$1</h4>') // Convert '### Subheading' to <h4>
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') // Convert **bold** text
      .replace(/^- (.+)$/gm, '<li>$1</li>') // Convert bullet points
      .replace(/^(\d+)\.\s(.+)$/gm, '<li>$2</li>') // Convert numbered lists
      .replace(/<\/li>\n<li>/g, '</li><li>') // Fix list item breaks
      .replace(/<li>.*<\/li>/g, '<ul>$&</ul>') // Wrap bullet points in <ul>
      .replace(/<\/ul>\n<ul>/g, '') // Avoid nested <ul> tags
      .replace(/\n/g, '<br>'); // Convert remaining newlines to <br>
  }
  

  const chatBubble = wrapper.querySelector('#chat-bubble');
  const chatWindow = wrapper.querySelector('#chat-window');
  const closeChat = wrapper.querySelector('#close-chat');
  const sendBtn = wrapper.querySelector('.send-btn');
  const chatInput = wrapper.querySelector('.chat-input');
  const chatBody = wrapper.querySelector('.chat-body');
  const typingIndicator = wrapper.querySelector('#typing-indicator');


  chatBubble.addEventListener('click', () => {
    // Hide the chat bubble
    chatBubble.style.opacity = '0';
    chatBubble.style.pointerEvents = 'none';
  
    // Show and animate the chat window
    chatWindow.classList.add('open');
  });
  
  closeChat.addEventListener('click', () => {
    // Hide the chat window with animation
    chatWindow.classList.remove('open');
  
    // Show the chat bubble again after animation
    setTimeout(() => {
      chatBubble.style.opacity = '1';
      chatBubble.style.pointerEvents = 'auto';
    }, 300); // Match the duration of the chat window animation
  });



  async function handleUserMessage(userMsg) {
    const userMsgElem = document.createElement('div');
    userMsgElem.className = 'chat-message user';
    userMsgElem.innerHTML = `<span>${userMsg}</span>`;
    chatBody.appendChild(userMsgElem);
    chatBody.scrollTop = chatBody.scrollHeight;

    typingIndicator.style.display = 'flex';

    const botReply = await window.getLLMResponse(userMsg);

    typingIndicator.style.display = 'none';

    const botMsgElem = document.createElement('div');
    botMsgElem.className = 'chat-message bot';
    botMsgElem.innerHTML = `<div class="formatted-response">${formatLLMResponse(botReply)}</div>`;
    chatBody.appendChild(botMsgElem);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  chatInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      const userMsg = chatInput.value.trim();
      if (!userMsg) return;
      chatInput.value = '';
      handleUserMessage(userMsg);
    }
  });

  sendBtn.addEventListener('click', () => {
    const userMsg = chatInput.value.trim();
    if (!userMsg) return;
    chatInput.value = '';
    handleUserMessage(userMsg);
  });
})();
