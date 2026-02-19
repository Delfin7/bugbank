"""
REST API routes - for advanced API testing
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Account, Transaction, Message

api_bp = Blueprint('api', __name__)


@api_bp.route('/health')
def health_check():
    """API health check - no auth required"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'app': 'BugBank'
    })


@api_bp.route('/accounts')
@login_required
def list_accounts():
    """List all user accounts"""
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    return jsonify({
        'accounts': [
            {
                'id': acc.id,
                'account_number': acc.account_number,
                'account_name': acc.account_name,
                'account_type': acc.account_type,
                'balance': acc.balance,
                'currency': acc.currency
            }
            for acc in accounts
        ]
    })


@api_bp.route('/accounts/<int:account_id>')
@login_required
def get_account(account_id):
    """Get single account details"""
    account = Account.query.filter_by(
        id=account_id,
        user_id=current_user.id
    ).first()
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    return jsonify({
        'id': account.id,
        'account_number': account.account_number,
        'account_name': account.account_name,
        'account_type': account.account_type,
        'balance': account.balance,
        'currency': account.currency,
        'created_at': account.created_at.isoformat()
    })


@api_bp.route('/transactions')
@login_required
def list_transactions():
    """List transactions with optional filters"""
    account_id = request.args.get('account_id', type=int)
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Get user's account IDs
    account_ids = [acc.id for acc in current_user.accounts]
    
    query = Transaction.query.filter(Transaction.from_account_id.in_(account_ids))
    
    if account_id:
        if account_id not in account_ids:
            return jsonify({'error': 'Account not found'}), 404
        query = query.filter_by(from_account_id=account_id)
    
    total = query.count()
    transactions = query.order_by(
        Transaction.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return jsonify({
        'transactions': [
            {
                'id': t.id,
                'reference_number': t.reference_number,
                'from_account_id': t.from_account_id,
                'to_account_number': t.to_account_number,
                'to_recipient_name': t.to_recipient_name,
                'amount': t.amount,
                'currency': t.currency,
                'title': t.title,
                'transaction_type': t.transaction_type,
                'status': t.status,
                'created_at': t.created_at.isoformat()
            }
            for t in transactions
        ],
        'pagination': {
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total
        }
    })


@api_bp.route('/transactions/<int:transaction_id>')
@login_required
def get_transaction(transaction_id):
    """Get single transaction details"""
    account_ids = [acc.id for acc in current_user.accounts]
    
    transaction = Transaction.query.filter(
        Transaction.id == transaction_id,
        Transaction.from_account_id.in_(account_ids)
    ).first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    return jsonify({
        'id': transaction.id,
        'reference_number': transaction.reference_number,
        'from_account_id': transaction.from_account_id,
        'to_account_number': transaction.to_account_number,
        'to_recipient_name': transaction.to_recipient_name,
        'amount': transaction.amount,
        'currency': transaction.currency,
        'title': transaction.title,
        'description': transaction.description,
        'transaction_type': transaction.transaction_type,
        'status': transaction.status,
        'created_at': transaction.created_at.isoformat()
    })


@api_bp.route('/messages')
@login_required
def list_messages():
    """List user messages"""
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    query = Message.query.filter_by(user_id=current_user.id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    total = query.count()
    messages = query.order_by(
        Message.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return jsonify({
        'messages': [
            {
                'id': msg.id,
                'sender': msg.sender,
                'subject': msg.subject,
                'is_read': msg.is_read,
                'is_important': msg.is_important,
                'category': msg.category,
                'created_at': msg.created_at.isoformat()
            }
            for msg in messages
        ],
        'pagination': {
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total
        }
    })


@api_bp.route('/messages/<int:message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Mark message as read"""
    from app import db
    
    message = Message.query.filter_by(
        id=message_id,
        user_id=current_user.id
    ).first()
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    message.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})
