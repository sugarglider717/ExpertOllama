from flask import Blueprint, render_template, request, redirect, url_for, flash
from ciobrain.admin.documents.documents_manager import DocumentsManager
from ciobrain.admin.documents.rag_manager import RAGManager

documents_bp = Blueprint('documents', __name__)
documents_manager = DocumentsManager()
rag_manager = RAGManager()

@documents_bp.route('/documents')
def home():
    """Document management page"""
    directories = documents_manager.get_directories()
    return render_template('admin_documents.html', directories = directories)

@documents_bp.route('documents/upload', methods=['POST'])
def upload_document():
    """document upload operation"""
    file = request.files.get('file')
    if file:
        try:
            documents_manager.upload_document(file)
            flash("File uploaded successfully!", "success")
        except ValueError as e:
            flash(str(e), "error")
    else:
        flash("No file selected!", "error")
    return redirect(url_for('admin.documents.home'))


@documents_bp.route('documents/process_handbook', methods=['POST'])
def process_handbook():
    vector_db = rag_manager.process_handbook('Handbook-CIO.pdf')
    if vector_db:
        return redirect(url_for('admin.documents.home'))
    else:
        return print("error")

