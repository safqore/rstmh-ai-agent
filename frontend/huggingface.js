(function () {
  window.getLLMResponse = async function (userMessage) {
    try {
      // Send user message to the backend proxy
      const response = await fetch(
        "https://pdf-qa-bot-o1bn.onrender.com/query", // Use the correct endpoint
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            accept: "application/json",
          },
          body: JSON.stringify(userMessage), // Directly send the user message as shown in the sample
        }
      );

      // Parse the response from the backend
      const data = await response.json();

      // Return the reply from the server
      return data.reply; // Ensure the backend returns a "reply" key
    } catch (err) {
      console.error("Error calling backend API:", err);
      return "An error occurred while fetching a response.";
    }
  };
})();
