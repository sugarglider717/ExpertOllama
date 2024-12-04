document.addEventListener("DOMContentLoaded", () => {
    const scrollContainer = document.getElementById("scroll-container");
    const input = document.getElementById("prompt");
    const ragToggle = document.getElementById("rag-toggle");

    // Function to add a message to the terminal
    const addMessageToTerminal = (role, content) => {
        const message = document.createElement("div");
        message.className = role; // 'user' or 'assistant'
        message.textContent = content;
        scrollContainer.appendChild(message);

        // Scroll to the bottom
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
        return message;
    };

    // Handle user input on Enter key
    input.addEventListener("keypress", async (event) => {
        if (event.key === "Enter") {
            event.preventDefault(); // Prevent newline in the textarea
            const prompt = input.value.trim();
            if (!prompt) return; // Do nothing if input is empty

            // Add user prompt to the terminal
            addMessageToTerminal("user", prompt);
            input.value = ""; // Clear the input box

            // Add a loading indicator to show the assistant is "thinking"
            const loadingMessage = addMessageToTerminal("assistant", "Assistant is typing...");

            try {
                // Send the prompt as a POST request
                console.log("Sending prompt to server...");
                const response = await fetch("/customer/prompt", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt, use_rag: ragToggle.checked }),
                });

                if (!response.ok) {
                    throw new Error("Server error");
                }

                // Stream the server response
                const reader = response.body.getReader();
                const decoder = new TextDecoder("utf-8");
                
                // Replace the loading indicator with an empty response area
                const assistantMessage = addMessageToTerminal("assistant", "");
                loadingMessage.remove();

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value, { stream: true });
                    console.log(`Received chunk from server: ${chunk}`);
                    
                    // Append the new chunk to the assistant message
                    assistantMessage.textContent += chunk;

                    // Keep scrolling to the bottom
                    scrollContainer.scrollTop = scrollContainer.scrollHeight;
                }
            } catch (error) {
                console.error("Error while streaming response:", error);
                loadingMessage.remove();
                addMessageToTerminal("error", "Error connecting to the server. Please try again.");
            }
        }
    });
});

