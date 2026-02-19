"""
Messages routes - internal messaging system
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Message
import time
import random

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/messages')
@login_required
def inbox():
    """Messages inbox page"""
    return render_template('messages/inbox.html')


@messages_bp.route('/messages/<int:message_id>')
@login_required
def message_detail(message_id):
    """Single message detail"""
    message = Message.query.filter_by(
        id=message_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Mark as read
    if not message.is_read:
        message.is_read = True
        db.session.commit()
    
    return render_template('messages/detail.html', message=message)


@messages_bp.route('/api/messages')
@login_required
def api_list_messages():
    """API: Get messages with pagination and infinite scroll support"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category', None)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    # Simulate delay for infinite scroll testing
    time.sleep(random.uniform(0.5, 1.5))
    
    query = Message.query.filter_by(user_id=current_user.id)
    
    if category:
        query = query.filter_by(category=category)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    pagination = query.order_by(Message.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'messages': [
            {
                'id': msg.id,
                'sender': msg.sender,
                'subject': msg.subject,
                'preview': msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
                'is_read': msg.is_read,
                'is_important': msg.is_important,
                'category': msg.category,
                'date': msg.created_at.strftime('%d.%m.%Y'),
                'time': msg.created_at.strftime('%H:%M')
            }
            for msg in pagination.items
        ],
        'pagination': {
            'page': pagination.page,
            'pages': pagination.pages,
            'total': pagination.total,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    })


@messages_bp.route('/api/messages/<int:message_id>')
@login_required
def api_message_detail(message_id):
    """API: Get single message"""
    message = Message.query.filter_by(
        id=message_id,
        user_id=current_user.id
    ).first()
    
    if not message:
        return jsonify({'error': 'Wiadomość nie znaleziona'}), 404
    
    # Mark as read
    if not message.is_read:
        message.is_read = True
        db.session.commit()
    
    return jsonify({
        'id': message.id,
        'sender': message.sender,
        'subject': message.subject,
        'content': message.content,
        'is_read': message.is_read,
        'is_important': message.is_important,
        'category': message.category,
        'date': message.created_at.strftime('%d.%m.%Y %H:%M')
    })


@messages_bp.route('/api/messages/<int:message_id>/read', methods=['POST'])
@login_required
def mark_as_read(message_id):
    """API: Mark message as read"""
    message = Message.query.filter_by(
        id=message_id,
        user_id=current_user.id
    ).first()
    
    if not message:
        return jsonify({'error': 'Wiadomość nie znaleziona'}), 404
    
    message.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})


@messages_bp.route('/api/messages/<int:message_id>/toggle-important', methods=['POST'])
@login_required
def toggle_important(message_id):
    """API: Toggle important flag"""
    message = Message.query.filter_by(
        id=message_id,
        user_id=current_user.id
    ).first()
    
    if not message:
        return jsonify({'error': 'Wiadomość nie znaleziona'}), 404
    
    message.is_important = not message.is_important
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_important': message.is_important
    })


@messages_bp.route('/api/messages/unread-count')
@login_required
def unread_count():
    """API: Get unread messages count"""
    count = Message.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    return jsonify({'count': count})


@messages_bp.route('/api/messages/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """API: Mark all messages as read"""
    Message.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    
    db.session.commit()
    
    return jsonify({'success': True})


@messages_bp.route('/api/messages/<int:message_id>/delete', methods=['DELETE'])
@login_required
def delete_message(message_id):
    """API: Delete message"""
    message = Message.query.filter_by(
        id=message_id,
        user_id=current_user.id
    ).first()
    
    if not message:
        return jsonify({'error': 'Wiadomość nie znaleziona'}), 404
    
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({'success': True})
