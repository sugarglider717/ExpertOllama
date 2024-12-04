import os
from langchain_ollama.chat_models import ChatOllama
from ciobrain.admin.documents.rag_manager import RAGManager  # Assuming RAGManager is in rag_manager.py
from flask import current_app
import logging
import time

class Mediator:
    """Mediator class to facilitate interaction with Ollama using RAG"""

    def __init__(self, model_name="CIO_Brain"):
        # Initialize language model (LLM)
        self.llm = ChatOllama(model=model_name)

        # Initialize RAGManager
        self.rag_manager = RAGManager()

        # Placeholder for vector_db, retriever, and chain
        self.vector_db = None
        self.retriever = None
        self.chain = None

    def initialize_resources(self):
        """Initialize the vector database and related resources if necessary"""
        vector_store_path = current_app.config['VECTOR_STORE']

        if not os.path.exists(vector_store_path) or len(os.listdir(vector_store_path)) == 0:
            logging.info("Vector store not found or is empty. Initializing from handbook...")
            handbook_filename = "Handbook-CIO.pdf"
            self.rag_manager.process_handbook(handbook_filename)
        else:
            logging.info("Vector store exists and is valid. Skipping handbook processing.")

        # Load vector_db for use in retriever and chain creation
        self.vector_db = self.rag_manager.test_vector_db_loading()

        if self.vector_db is None:
            logging.error("Failed to load the vector database.")
            return

        # Create retriever and chain
        logging.info("Creating retriever and chain...")
        self.retriever = self.rag_manager.create_retriever(self.vector_db, self.llm)
        self.chain = self.rag_manager.create_chain(self.retriever, self.llm)
        logging.info("Vector database, retriever, and chain initialized successfully.")

    def stream(self, conversation, use_rag=False):
        """Streams the response from the chain or LLM directly, based on use_rag flag."""
        if use_rag:
            # Ensure RAG resources are initialized
            if not self.vector_db or not self.chain:
                self.initialize_resources(current_app.config['VECTOR_STORE'], "Handbook-CIO.pdf")

            if not self.chain:
                logging.error("Chain is not initialized. Ensure vector DB is loaded correctly.")
                yield "Error: Chain is not initialized.\n".encode('utf-8')
                return

            # Generate response using the RAG chain
            logging.info("Using RAG to generate the response...")
            chain_generator = self.chain(conversation)
            for chunk in chain_generator:
                logging.info(f"Generated chunk (RAG): {chunk}")
                yield str(chunk).encode('utf-8')
        else:
            # Generate response using the LLM directly via streaming
            logging.info("Using LLM directly to generate the response...")

            # Use the stream method to simulate response generation
            llm_generator = self.llm.stream(conversation, stream=True)
            for chunk in llm_generator:
                if hasattr(chunk, 'content'):
                    logging.info(f"Generated chunk (LLM): {chunk.content}")
                    yield chunk.content.encode('utf-8')
                else:
                    logging.warning(f"Unexpected chunk format: {chunk}")
