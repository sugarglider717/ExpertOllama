"""
ciobrain/customer/__init__.py

Defines the customer Blueprint and routes
"""

import logging
from flask import Blueprint, request, Response, render_template, stream_with_context
from ciobrain.customer.customer_dashboard import CustomerDashboard


def create_customer_blueprint(mediator):
    customer_bp = Blueprint('customer', __name__, url_prefix='/customer')
    customer_dashboard = CustomerDashboard(mediator=mediator)

    @customer_bp.route('/')
    def home():
        """customer dashboard page"""
        return render_template('customer_home.html')

    @customer_bp.route('/prompt', methods=['POST'])
    def submit_prompt():
        """Handles user prompts."""
        try:
            # Get the prompt and RAG toggle value from the POST request body
            prompt = request.json.get('prompt', '').strip()
            use_rag = request.json.get('use_rag', False)

            if not prompt:
                logging.warning("Received empty prompt")
                return Response("Invalid prompt", status=400)

            logging.info(f"Received prompt: {prompt}, Use RAG: {use_rag}")

            # Get the response generator from the customer dashboard
            response_generator = customer_dashboard.process_prompt(prompt, use_rag=use_rag)

            # Logging before sending the response
            logging.info("Streaming response back to client...")

            # Return as plain text with the generator yielding properly encoded bytes
            return Response(
                response_generator,
                content_type="text/plain",
            )
        except Exception as e:
            logging.exception("Error in /prompt route")
            return Response("Internal server error", status=500)

    return customer_bp
