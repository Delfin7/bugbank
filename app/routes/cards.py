"""
Cards routes - card management
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Card, Account
import time
import random

cards_bp = Blueprint('cards', __name__)


@cards_bp.route('/cards')
@login_required
def manage_cards():
    """Card management page"""
    # Get user's accounts
    account_ids = [acc.id for acc in current_user.accounts]
    
    # Get cards for those accounts
    cards = Card.query.filter(Card.account_id.in_(account_ids)).all()
    
    return render_template('cards/manage.html', cards=cards)


@cards_bp.route('/api/cards')
@login_required
def api_list_cards():
    """API: Get all user cards"""
    time.sleep(random.uniform(0.3, 1.0))
    
    account_ids = [acc.id for acc in current_user.accounts]
    cards = Card.query.filter(Card.account_id.in_(account_ids)).all()
    
    return jsonify({
        'cards': [
            {
                'id': card.id,
                'masked_number': card.masked_number,
                'full_number': card.formatted_number,
                'card_holder': card.card_holder,
                'expiry_date': card.expiry_date,
                'card_type': card.card_type,
                'card_brand': card.card_brand,
                'is_active': card.is_active,
                'is_blocked': card.is_blocked,
                'daily_limit': card.daily_limit,
                'contactless_enabled': card.contactless_enabled,
                'internet_enabled': card.internet_enabled,
                'account_name': card.account.account_name
            }
            for card in cards
        ]
    })


@cards_bp.route('/api/cards/<int:card_id>/toggle-block', methods=['POST'])
@login_required
def toggle_card_block(card_id):
    """API: Block/unblock card"""
    # Verify card belongs to user
    account_ids = [acc.id for acc in current_user.accounts]
    card = Card.query.filter(
        Card.id == card_id,
        Card.account_id.in_(account_ids)
    ).first()
    
    if not card:
        return jsonify({'error': 'Karta nie znaleziona'}), 404
    
    card.is_blocked = not card.is_blocked
    db.session.commit()
    
    status = 'zablokowana' if card.is_blocked else 'odblokowana'
    
    return jsonify({
        'success': True,
        'is_blocked': card.is_blocked,
        'message': f'Karta została {status}'
    })


@cards_bp.route('/api/cards/<int:card_id>/toggle-contactless', methods=['POST'])
@login_required
def toggle_contactless(card_id):
    """API: Enable/disable contactless payments"""
    account_ids = [acc.id for acc in current_user.accounts]
    card = Card.query.filter(
        Card.id == card_id,
        Card.account_id.in_(account_ids)
    ).first()
    
    if not card:
        return jsonify({'error': 'Karta nie znaleziona'}), 404
    
    card.contactless_enabled = not card.contactless_enabled
    db.session.commit()
    
    status = 'włączone' if card.contactless_enabled else 'wyłączone'
    
    return jsonify({
        'success': True,
        'contactless_enabled': card.contactless_enabled,
        'message': f'Płatności zbliżeniowe {status}'
    })


@cards_bp.route('/api/cards/<int:card_id>/toggle-internet', methods=['POST'])
@login_required
def toggle_internet(card_id):
    """API: Enable/disable internet payments"""
    account_ids = [acc.id for acc in current_user.accounts]
    card = Card.query.filter(
        Card.id == card_id,
        Card.account_id.in_(account_ids)
    ).first()
    
    if not card:
        return jsonify({'error': 'Karta nie znaleziona'}), 404
    
    card.internet_enabled = not card.internet_enabled
    db.session.commit()
    
    status = 'włączone' if card.internet_enabled else 'wyłączone'
    
    return jsonify({
        'success': True,
        'internet_enabled': card.internet_enabled,
        'message': f'Płatności internetowe {status}'
    })


@cards_bp.route('/api/cards/<int:card_id>/set-limit', methods=['POST'])
@login_required
def set_card_limit(card_id):
    """API: Set daily limit (for slider testing)"""
    account_ids = [acc.id for acc in current_user.accounts]
    card = Card.query.filter(
        Card.id == card_id,
        Card.account_id.in_(account_ids)
    ).first()
    
    if not card:
        return jsonify({'error': 'Karta nie znaleziona'}), 404
    
    try:
        new_limit = float(request.json.get('limit', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Nieprawidłowa wartość limitu'}), 400
    
    if new_limit < 0 or new_limit > 50000:
        return jsonify({'error': 'Limit musi być między 0 a 50000 PLN'}), 400
    
    card.daily_limit = new_limit
    db.session.commit()
    
    return jsonify({
        'success': True,
        'daily_limit': card.daily_limit,
        'message': f'Limit dzienny ustawiony na {new_limit:,.0f} PLN'
    })


@cards_bp.route('/api/cards/<int:card_id>/reveal', methods=['POST'])
@login_required
def reveal_card_number(card_id):
    """API: Reveal full card number (with delay for animation testing)"""
    # Simulate security delay
    time.sleep(random.uniform(0.5, 1.5))
    
    account_ids = [acc.id for acc in current_user.accounts]
    card = Card.query.filter(
        Card.id == card_id,
        Card.account_id.in_(account_ids)
    ).first()
    
    if not card:
        return jsonify({'error': 'Karta nie znaleziona'}), 404
    
    return jsonify({
        'success': True,
        'card_number': card.formatted_number,
        'cvv': card.cvv,
        'expiry': card.expiry_date
    })
