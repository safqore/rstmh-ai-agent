(function() {
  window.getLLMResponse = async function(userMessage) {
      try {
          // Send user message to the backend proxy instead of Hugging Face directly
          const response = await fetch('http://localhost:5000/api/chat', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({ message: userMessage })
          });

          // Parse the response from the Flask server
          const data = await response.json();
          
          // Return the reply from the server
          return data.reply;
      } catch (err) {
          console.error('Error calling backend API:', err);
          return "An error occurred while fetching a response.";
      }
  };
})();
