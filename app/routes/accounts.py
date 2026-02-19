"""
Accounts routes - bank accounts management
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Account, Transaction
import time
import random

accounts_bp = Blueprint('accounts', __name__)


@accounts_bp.route('/accounts')
@login_required
def list_accounts():
    """List all user accounts"""
    return render_template('accounts/list.html')


@accounts_bp.route('/accounts/<int:account_id>')
@login_required
def account_detail(account_id):
    """Single account details"""
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
    return render_template('accounts/detail.html', account=account)


@accounts_bp.route('/api/accounts')
@login_required
def api_list_accounts():
    """API: Get all accounts with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    sort_by = request.args.get('sort_by', 'account_name')
    sort_order = request.args.get('sort_order', 'asc')
    filter_type = request.args.get('type', None)
    filter_currency = request.args.get('currency', None)
    
    # Simulate delay
    time.sleep(random.uniform(0.5, 1.5))
    
    query = Account.query.filter_by(user_id=current_user.id, is_active=True)
    
    # Apply filters
    if filter_type:
        query = query.filter_by(account_type=filter_type)
    if filter_currency:
        query = query.filter_by(currency=filter_currency)
    
    # Apply sorting
    if sort_order == 'desc':
        query = query.order_by(getattr(Account, sort_by).desc())
    else:
        query = query.order_by(getattr(Account, sort_by).asc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'accounts': [
            {
                'id': acc.id,
                'account_number': acc.formatted_account_number,
                'account_name': acc.account_name,
                'account_type': acc.account_type,
                'balance': acc.balance,
                'formatted_balance': acc.formatted_balance,
                'currency': acc.currency
            }
            for acc in pagination.items
        ],
        'pagination': {
            'page': pagination.page,
            'pages': pagination.pages,
            'total': pagination.total,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    })


@accounts_bp.route('/api/accounts/<int:account_id>')
@login_required
def api_account_detail(account_id):
    """API: Get single account details"""
    time.sleep(random.uniform(0.3, 1.0))
    
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    
    if not account:
        return jsonify({'error': 'Konto nie znalezione'}), 404
    
    return jsonify({
        'id': account.id,
        'account_number': account.formatted_account_number,
        'account_name': account.account_name,
        'account_type': account.account_type,
        'balance': account.balance,
        'formatted_balance': account.formatted_balance,
        'currency': account.currency,
        'created_at': account.created_at.strftime('%d.%m.%Y')
    })


@accounts_bp.route('/api/accounts/<int:account_id>/rename', methods=['POST'])
@login_required
def api_rename_account(account_id):
    """API: Rename account (for double-click edit testing)"""
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    
    if not account:
        return jsonify({'error': 'Konto nie znalezione'}), 404
    
    new_name = request.json.get('name', '').strip()
    
    if not new_name:
        return jsonify({'error': 'Nazwa nie może być pusta'}), 400
    
    if len(new_name) > 64:
        return jsonify({'error': 'Nazwa jest za długa (max 64 znaki)'}), 400
    
    account.account_name = new_name
    db.session.commit()
    
    return jsonify({
        'success': True,
        'name': account.account_name
    })


@accounts_bp.route('/api/accounts/<int:account_id>/transactions')
@login_required
def api_account_transactions(account_id):
    """API: Get account transactions with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    time.sleep(random.uniform(0.5, 1.5))
    
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    
    if not account:
        return jsonify({'error': 'Konto nie znalezione'}), 404
    
    pagination = Transaction.query.filter_by(
        from_account_id=account_id
    ).order_by(Transaction.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'transactions': [
            {
                'id': t.id,
                'reference': t.reference_number,
                'title': t.title,
                'recipient': t.to_recipient_name,
                'amount': t.amount,
                'formatted_amount': t.formatted_amount,
                'type': t.transaction_type,
                'status': t.status,
                'date': t.created_at.strftime('%d.%m.%Y %H:%M')
            }
            for t in pagination.items
        ],
        'pagination': {
            'page': pagination.page,
            'pages': pagination.pages,
            'total': pagination.total,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    })
