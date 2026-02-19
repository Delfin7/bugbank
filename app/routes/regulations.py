"""
Regulations routes - terms and conditions (opens in new window)
"""

from flask import Blueprint, render_template

regulations_bp = Blueprint('regulations', __name__)


@regulations_bp.route('/regulations')
def terms():
    """Terms and conditions page - opens in new tab"""
    return render_template('regulations/terms.html')


@regulations_bp.route('/regulations/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('regulations/privacy.html')


@regulations_bp.route('/regulations/fees')
def fees():
    """Fee table page"""
    return render_template('regulations/fees.html')
