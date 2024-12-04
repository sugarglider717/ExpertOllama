import os
import shutil
import logging
import pdfplumber
from flask import current_app
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate

logging.basicConfig(level=logging.INFO)

class RAGManager:

    def process_handbook(self, handbook_filename):
        handbook_path = os.path.join(current_app.config['KNOWLEDGE'], handbook_filename)
        vector_store_path = current_app.config['VECTOR_STORE']

        if not os.path.exists(handbook_path):
            logging.error(f"Handbook not found at {handbook_path}")
            return None

        logging.info(f"Processing handbook: {handbook_path}")
        document_chunks = self.split_document(handbook_path)

        # Check if chunks were extracted
        if not document_chunks:
            logging.error("No chunks extracted from the document.")
            return None

        vector_db = self.load_or_create_vector_db(document_chunks)
        return vector_db

    def split_document(self, doc_path):
        if not os.path.exists(doc_path):
            logging.error(f"Document not found at {doc_path}")
            return []

        documents = self.extract_text(doc_path)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
        document_chunks = text_splitter.split_documents(documents)
        logging.info(f"Document split into {len(document_chunks)} chunks.")
        return document_chunks

    def extract_text(self, pdf_path):
        documents = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:  # Add extracted text if available
                    documents.append(Document(page_content=text))
        logging.info(f"Extracted {len(documents)} pages from the PDF.")
        return documents


    def load_or_create_vector_db(self, doc_chunks):
        vector_db_path = current_app.config['VECTOR_STORE']
        embedding = OllamaEmbeddings(model="nomic-embed-text")

        # Check if vector store already exists
        if os.path.exists(vector_db_path) and os.listdir(vector_db_path):
            logging.info("Vector database directory found, checking contents...")

            # Validate content and attempt to load
            vector_db = self.test_vector_db_loading()
            if vector_db:
                logging.info("Vector database loaded successfully.")
                return vector_db

        # If validation fails, create a new vector database
        logging.info("Creating new vector database.")
        return self._create_new_vector_db(doc_chunks, vector_db_path, embedding)

    def _create_new_vector_db(self, doc_chunks, vector_db_path, embedding):
        """Helper function to create and persist a new vector database"""
        try:
            logging.info("Creating new vector database.")

            if not os.path.exists(vector_db_path):
                os.makedirs(vector_db_path)

            vector_db = Chroma.from_documents(
                documents=doc_chunks,
                embedding=embedding,
                collection_name="handbook_vector_store",
                persist_directory=vector_db_path,
            )

            # Embedding complete message
            logging.info("Vector database created and persisted successfully.")
            return vector_db

        except Exception as e:
            logging.error(f"Error during vector database creation: {str(e)}")
            return None       

    def _clean_directory(self, dir_path):
        """Helper function to delete all files and subdirectories inside a given directory"""
        logging.info(f"Cleaning up directory: {dir_path}")
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove file or symbolic link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove directory
            except Exception as e:
                logging.error(f"Failed to delete {file_path}. Reason: {e}")
            
    def create_retriever(self, vector_db, llm):
        """Create a multi-query retriever."""
        QUERY_PROMPT = PromptTemplate(
            input_variables=["question"],
            template="""You are an AI language model assistant. Your task is to generate five
            different versions of the given user question to retrieve relevant documents from
            a vector database. By generating multiple perspectives on the user question, your
            goal is to help the user overcome some of the limitations of the distance-based
            similarity search. Provide these alternative questions separated by newlines.
            Original question: {question}""",
        )

        logging.info("Creating multi-query retriever...")
        retriever = MultiQueryRetriever.from_llm(
            vector_db.as_retriever(), llm, prompt=QUERY_PROMPT
        )
        logging.info("Retriever created.")
        return retriever

    def create_chain(self, retriever, llm):
        """Create the chain with preserved syntax and detailed progress updates."""
        # RAG prompt template
        template = """Answer the question based ONLY on the following context:
        {context}
        Question: {question}
        """

        prompt = ChatPromptTemplate.from_template(template)

        def chain_generator(question):
            # Adding progress updates
            yield "Retrieving relevant documents...\n"

            try:
                # Use the new `.invoke()` method to get relevant documents
                retrieved_docs = retriever.invoke(question)

                # Handle if no documents were found
                if not retrieved_docs or len(retrieved_docs) == 0:
                    yield "No relevant documents found for the given query.\n"
                    return

                # Convert the retrieved documents into a single string context
                context = "\n\n".join([doc.page_content for doc in retrieved_docs])
                logging.info(f"Retrieved {len(retrieved_docs)} documents.")
                yield f"Retrieved {len(retrieved_docs)} documents successfully.\n"

                # Create a dictionary with context and question to pass through the chain
                input_dict = {"context": context, "question": question}

                # Create the chain by connecting all the Runnables
                chain = (
                    RunnablePassthrough()  # Accept the input dictionary
                    | prompt                # Use the prompt to format the response
                    | llm                   # Pass to the LLM to generate the output
                    | StrOutputParser()     # Parse the output into a readable string
                )

                # Invoke the chain with the correct dictionary format
                response = chain.invoke(input_dict)
                yield response

                logging.info("Response generation completed.")

            except Exception as e:
                logging.error(f"Error during chain generation: {str(e)}")
                yield f"Error during response generation: {str(e)}\n"

        return chain_generator
    
    def test_vector_db_loading(self):
        """Test if the vector database can be loaded successfully."""
        vector_db_path = current_app.config['VECTOR_STORE']
        if os.path.exists(vector_db_path):
            try:
                embedding = OllamaEmbeddings(model="nomic-embed-text")
                vector_db = Chroma(
                    embedding_function=embedding,
                    collection_name="handbook_vector_store",
                    persist_directory=vector_db_path,
                )
                logging.info("Vector database loaded successfully.")
                return vector_db
            except Exception as e:
                logging.error(f"Error loading vector database: {str(e)}")
        else:
            logging.error(f"Vector database path not found at {vector_db_path}")
        return None

    def debug_vector_store_content(self):
        """Debugging method to inspect the content stored in the vector store."""
        with current_app.app_context():  # Ensure we have the correct context
            vector_db_path = current_app.config['VECTOR_STORE']
            embedding = OllamaEmbeddings(model="nomic-embed-text")

            if os.path.exists(vector_db_path):
                vector_db = Chroma(
                    embedding_function=embedding,
                    collection_name="handbook_vector_store",
                    persist_directory=vector_db_path,
                )
                logging.info("Debugging: Inspecting vector store content...")

                # Use similarity search to retrieve documents for inspection
                try:
                    sample_docs = vector_db.similarity_search(query="Sample", k=5)  # Retrieve 5 documents as a sample
                    if not sample_docs:
                        logging.info("No documents found in the vector store.")
                    else:
                        logging.info(f"Total documents retrieved: {len(sample_docs)}")
                        for idx, doc in enumerate(sample_docs):
                            logging.info(f"Document {idx + 1}: {doc.page_content[:200]}")  # Log first 200 characters of each document

                except Exception as e:
                    logging.error(f"Error retrieving documents for debugging: {str(e)}")

            else:
                logging.error(f"Vector database path not found at {vector_db_path}")

