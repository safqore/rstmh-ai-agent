(function() {
  window.getLLMResponse = async function(userMessage) {
      try {
          // Send user message to the backend proxy instead of Hugging Face directly
          const response = await fetch('https://rsmth-test-bot.onrender.com/query', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({ user_query: userMessage })
          });

          // Parse the response from the Flask server
          const data = await response.json();
          
          // Return the reply from the server
          return data.answer;
      } catch (err) {
          console.error('Error calling backend API:', err);
          return "An error occurred while fetching a response.";
      }
  };
})();
