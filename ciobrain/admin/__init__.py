"""
ciobrain/admin/__init__.py

Defines admin Blueprint and registers subsections 
"""

from flask import Blueprint, render_template
from ciobrain.admin.documents import documents_bp

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
admin_bp.register_blueprint(documents_bp)

@admin_bp.route('/')
def home():
    """Admin dashboard homepage"""
    return render_template('admin_home.html')
