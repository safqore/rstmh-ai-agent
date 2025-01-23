(function() {
    window.getLLMResponse = async function(userMessage) {
        try {
            let user_id = localStorage.getItem('user_id');
            let session_id = localStorage.getItem('session_id');
            
            // Send user message to the backend proxy instead of Hugging Face directly
            const response = await fetch('https://rsmth-test-bot.onrender.com/query', {
            // const response = await fetch('http://127.0.0.1:5005/query', {
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
  
  