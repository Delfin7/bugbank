"""
Dashboard routes - main user panel
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models import Account, Transaction, Message
import random
import time

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard page"""
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    unread_messages = Message.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return render_template(
        'dashboard/index.html',
        accounts=accounts,
        unread_messages=unread_messages
    )


@dashboard_bp.route('/api/dashboard/balance')
@login_required
def get_balance():
    """AJAX endpoint for balance - with intentional delay"""
    # Simulate slow loading (challenge for explicit waits)
    delay = random.uniform(1.0, 3.0)
    time.sleep(delay)
    
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    total_pln = sum(acc.balance for acc in accounts if acc.currency == 'PLN')
    
    return jsonify({
        'total_balance': f"{total_pln:,.2f} PLN",
        'accounts_count': len(accounts),
        'accounts': [
            {
                'id': acc.id,
                'name': acc.account_name,
                'balance': acc.formatted_balance,
                'type': acc.account_type
            }
            for acc in accounts
        ]
    })


@dashboard_bp.route('/api/dashboard/recent-transactions')
@login_required
def get_recent_transactions():
    """AJAX endpoint for recent transactions - with delay"""
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)
    
    # Get user's accounts
    account_ids = [acc.id for acc in current_user.accounts]
    
    # Get recent transactions
    transactions = Transaction.query.filter(
        Transaction.from_account_id.in_(account_ids)
    ).order_by(Transaction.created_at.desc()).limit(5).all()
    
    return jsonify({
        'transactions': [
            {
                'id': t.id,
                'title': t.title,
                'amount': t.formatted_amount,
                'date': t.created_at.strftime('%d.%m.%Y'),
                'status': t.status,
                'type': t.transaction_type
            }
            for t in transactions
        ]
    })


@dashboard_bp.route('/api/dashboard/notifications')
@login_required
def get_notifications():
    """AJAX endpoint for notifications badge"""
    unread = Message.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return jsonify({
        'unread_count': unread
    })
