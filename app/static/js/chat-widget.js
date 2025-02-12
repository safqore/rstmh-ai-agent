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
      min-height: 400px;
      background: #fff;
      border: none;
      border-radius: 10px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
      display: none;
      flex-direction: column;
      z-index: 9999;
      overflow: hidden;
      font-size: 1.0rem;
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
      background: #006778;
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
      background: #006778;
      transform: scale(1.05);
    }

    /* For larger screens */
    @media (min-width: 600px) {
      #safqore-chat-wrapper .chat-window {
        height: 80vh; /* 80% of the viewport height */
      }
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
        box-shadow: 0 0 0 0 rgba(153, 24, 54, 0.7); /* Darker shade */
      }
      50% {
        box-shadow: 0 0 15px 10px rgba(153, 24, 54, 0.3); /* Lighter shade */
      }
      100% {
        box-shadow: 0 0 0 0 rgba(153, 24, 54, 0.7); /* Darker shade */
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
      top: 5px;
      right: 8px;
      background: transparent;
      border: none;
      color: #fff;
      font-size: 2.4rem;
      cursor: pointer;
    }

    #safqore-chat-wrapper .chat-body {
      font-family: "Arial", sans-serif;
      color: black;
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
      font-size: 1.0rem;
    }

    #safqore-chat-wrapper .chat-message.user {
      text-align: right; /* Align the user message to the right */
      padding-right: 7px; /* Space between the message bubble and the right edge */
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
      margin-left: 5px;
      max-width: 90%;
      background: #f9f9f9;
      padding: 12px;
      border-radius: 12px 12px 12px 0; /* Top-left, top-right, bottom-right, bottom-left */
      border: 1px solid #e0e0e0;
      box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
    }

    #safqore-chat-wrapper .chat-message.bot span {
    display: inline-block;
    background: #f9f9f9; /* Agent response background */
    color: black; /* Agent response text color */
    word-wrap: break-word;
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
      font-size: 1.0rem;
    }

    #safqore-chat-wrapper .send-btn {
      background: transparent;
      border: none;
      cursor: pointer;
      color: #006778;
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
      color: #004d59; /* Darker shade of the primary color for hover */

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

    #safqore-chat-wrapper .typing-indicator {
      display: flex;
      align-items: flex-end; /* Align dots to the bottom of the text */
      gap: 5px;
      font-size: 0.85rem;
      color: #aaa;
    }

    #safqore-chat-wrapper .typing-indicator .dot {
      width: 6px;
      height: 6px;
      background-color: #aaa;
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out;
      margin-bottom: 2px; /* Adjust the dots slightly higher */
    }

    #safqore-chat-wrapper .typing-indicator .dot:nth-child(1) {
      animation-delay: -0.32s;
    }
    #safqore-chat-wrapper .typing-indicator .dot:nth-child(2) {
      animation-delay: -0.16s;
    }
    #safqore-chat-wrapper .typing-indicator .dot:nth-child(3) {
      animation-delay: 0;
    }

    @keyframes bounce {
      0%, 80%, 100% {
        transform: scale(0);
      }
      40% {
        transform: scale(1);
      }
    }

    #safqore-chat-wrapper .message-timestamp-user {
      font-size: 0.75rem; /* Match 'Powered By' font size */
      color: black; 
      margin-top: 4px; /* Add slight spacing above the timestamp */
      text-align: right; /* Align with the message bubble */
    }

    #safqore-chat-wrapper .message-timestamp-bot {
      font-size: 0.75rem; /* Same size as 'Powered By' text */
      color: black; 
      margin-top: -8px;
      margin-left: 12px; /* Align to the left */
      text-align: left;
      padding-bottom: 12px;
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
          <h2>RSTMH Grants - AI Assistant ✨</h2>
        </div>
        <button id="close-chat" class="close-btn">&times;</button>
      </div>
      <div class="chat-body">
        <div class="chat-message bot">
          <span>
            <b>Welcome to the RSTMH Early Career Grants AI Assistant!</b><br><br>
            Thank you for visiting. I’m here to help with all your queries about the RSTMH Early Career Grants Programme, including eligibility, the application process, key dates, and funding details.<br><br>
            How can I assist you today?
          </span>
        </div>
      </div>
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

    // Ensure the input field is focused
    chatInput.focus();
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

  function getLocalTimestamp() {
    const now = new Date();
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const day = days[now.getDay()];
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    return `${day} ${hours}:${minutes}`;
  }  

  async function handleUserMessage(userMsg) {
    const usertimestamp = getLocalTimestamp();

    // Add user message
    const userMsgElem = document.createElement('div');
    userMsgElem.className = 'chat-message user';
    userMsgElem.innerHTML = `<span>${userMsg}</span><div class="message-timestamp-user">Sent - ${usertimestamp}</div>`;
    chatBody.appendChild(userMsgElem);
    chatBody.scrollTop = chatBody.scrollHeight;
  
    typingIndicator.style.display = 'flex';
  
    // Simulate agent response
    const botReply = await window.getLLMResponse(userMsg);
  
    typingIndicator.style.display = 'none';
  
    // Add bot message
    const botMsgContainer = document.createElement('div');
    botMsgContainer.className = 'chat-message bot';
  
    const botMessageContent = document.createElement('div');
    botMessageContent.className = 'formatted-response';
    botMessageContent.innerHTML = formatLLMResponse(botReply);
  
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp-bot';
    timestamp.innerHTML = `RSTMH AI Assistant -  ${new Date().toLocaleString('en-US', {
      weekday: 'short',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    })}`;
  
    botMsgContainer.appendChild(botMessageContent);
    chatBody.appendChild(botMsgContainer);
    chatBody.appendChild(timestamp); // Append timestamp as a sibling element
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

  window.getLLMResponse = async function(userMessage) {
    try {
        let user_id = localStorage.getItem('user_id');
        let session_id = localStorage.getItem('session_id');
        
        // Send user message to the backend dynamically using BASE_URL
        const response = await fetch(`${BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': user_id,
                'X-Session-ID': session_id
            },
            body: JSON.stringify({ user_query: userMessage })
        });

        // Parse the response from the Flask server
        const data = await response.json();
        
        // Update local storage with IDs if they're returned
        if (data.user_id) localStorage.setItem('user_id', data.user_id);
        if (data.session_id) localStorage.setItem('session_id', data.session_id);

        console.log('Server Response:', data);
        
        // Return the reply from the server
        return data.answer;
    } catch (err) {
        console.error('Error calling backend API:', err);
        return "An error occurred while fetching a response.";
    }
};

})();
