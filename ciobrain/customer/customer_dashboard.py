import logging

class CustomerDashboard:
    """
    Facade class for customer dashboard
    """
    def __init__(self, mediator):
        self.chat_handler = ChatHandler(mediator=mediator)

    def process_prompt(self, prompt, use_rag=False):
        """
        Delegate chat prompt processing to the ChatHandler
        """
        return self.chat_handler.generate_response_stream(prompt, use_rag=use_rag)

class ChatHandler:
    def __init__(self, mediator):
        self.mediator = mediator
        self.chat_history = []

    def generate_response_stream(self, prompt, use_rag=False):
        """
        Generates a streaming response for a given prompt.
        """
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        # Append user prompt to chat history
        self.chat_history.append({"role": "user", "content": prompt})

    def generate_response_stream(self, prompt, use_rag=False):
        """
        Generates a streaming response for a given prompt.
        """
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        # Append user prompt to chat history
        self.chat_history.append({"role": "user", "content": prompt})

        def generate():
            response_buffer = []

            # Prepare the conversation history to be passed to the mediator
            full_history = self.chat_history
            
            # Logging the conversation history for debugging
            logging.info(f"Full history being sent to mediator: {full_history}")

            # Stream the response using the mediator's stream function
            generator = self.mediator.stream(full_history, use_rag=use_rag)
            for chunk in generator:
                # Log each chunk received from the mediator
                logging.info(f"Chunk received from mediator: {chunk}")

                # Decode the byte chunk to string before adding to buffer
                decoded_chunk = chunk.decode('utf-8')
                response_buffer.append(decoded_chunk)

                # Yield each chunk to the client
                yield chunk

            # Once streaming is complete, add the final assistant response to the chat history
            self.chat_history.append({"role": "assistant", "content": "".join(response_buffer)})
            logging.info(f"Final response added to history: {''.join(response_buffer)}")

        return generate()
            
