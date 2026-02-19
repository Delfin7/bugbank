"""
Transfers routes - money transfers with multi-step wizard
"""

from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Account, Transaction, SavedRecipient
import time
import random
import string

transfers_bp = Blueprint('transfers', __name__)


def generate_reference():
    """Generate transaction reference number"""
    return 'TRX' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


@transfers_bp.route('/transfers/new')
@login_required
def new_transfer():
    """New transfer - Step 1: Enter details"""
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    # Clear any previous transfer session data
    session.pop('transfer_data', None)
    
    return render_template('transfers/new.html', accounts=accounts)


@transfers_bp.route('/transfers/confirm', methods=['GET', 'POST'])
@login_required
def confirm_transfer():
    """Transfer - Step 2: Confirmation"""
    if request.method == 'POST':
        # Store transfer data in session
        transfer_data = {
            'from_account_id': request.form.get('from_account'),
            'recipient_name': request.form.get('recipient_name'),
            'recipient_account': request.form.get('recipient_account', '').replace(' ', ''),
            'amount': request.form.get('amount'),
            'title': request.form.get('title'),
            'save_recipient': request.form.get('save_recipient') == 'on'
        }
        
        # Validate
        errors = []
        
        if not transfer_data['from_account_id']:
            errors.append('Wybierz konto źródłowe')
        
        if not transfer_data['recipient_name']:
            errors.append('Podaj nazwę odbiorcy')
        
        if not transfer_data['recipient_account'] or len(transfer_data['recipient_account']) < 26:
            errors.append('Podaj poprawny numer konta odbiorcy')
        
        try:
            amount = float(transfer_data['amount'].replace(',', '.'))
            if amount <= 0:
                errors.append('Kwota musi być większa od zera')
            transfer_data['amount'] = amount
        except (ValueError, AttributeError):
            errors.append('Podaj poprawną kwotę')
        
        if not transfer_data['title']:
            errors.append('Podaj tytuł przelewu')
        
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Check account balance
        account = Account.query.filter_by(
            id=transfer_data['from_account_id'],
            user_id=current_user.id
        ).first()
        
        if not account:
            return jsonify({'success': False, 'errors': ['Konto nie znalezione']}), 400
        
        if account.balance < transfer_data['amount']:
            return jsonify({'success': False, 'errors': ['Niewystarczające środki na koncie']}), 400
        
        # Store in session
        session['transfer_data'] = transfer_data
        session['transfer_data']['from_account_name'] = account.account_name
        session['transfer_data']['from_account_number'] = account.formatted_account_number
        session['transfer_data']['currency'] = account.currency
        
        return jsonify({'success': True, 'redirect': url_for('transfers.confirm_transfer')})
    
    # GET - show confirmation page
    transfer_data = session.get('transfer_data')
    
    if not transfer_data:
        return redirect(url_for('transfers.new_transfer'))
    
    return render_template('transfers/confirm.html', transfer=transfer_data)


@transfers_bp.route('/transfers/execute', methods=['POST'])
@login_required
def execute_transfer():
    """Execute the transfer after SMS confirmation"""
    transfer_data = session.get('transfer_data')
    
    if not transfer_data:
        return jsonify({'success': False, 'error': 'Sesja wygasła'}), 400
    
    # Verify SMS code (mock - always 123456)
    sms_code = request.form.get('sms_code', '')
    
    if sms_code != '123456':
        return jsonify({'success': False, 'error': 'Nieprawidłowy kod SMS'}), 400
    
    # Simulate processing delay
    time.sleep(random.uniform(1.0, 2.0))
    
    # Execute transfer
    account = Account.query.get(transfer_data['from_account_id'])
    
    if not account or account.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Błąd autoryzacji'}), 403
    
    if account.balance < transfer_data['amount']:
        return jsonify({'success': False, 'error': 'Niewystarczające środki'}), 400
    
    # Create transaction
    transaction = Transaction(
        from_account_id=account.id,
        to_account_number=transfer_data['recipient_account'],
        to_recipient_name=transfer_data['recipient_name'],
        amount=transfer_data['amount'],
        currency=account.currency,
        title=transfer_data['title'],
        transaction_type='transfer',
        status='completed',
        reference_number=generate_reference()
    )
    
    # Update balance
    account.balance -= transfer_data['amount']
    
    # Save recipient if requested
    if transfer_data.get('save_recipient'):
        existing = SavedRecipient.query.filter_by(
            user_id=current_user.id,
            account_number=transfer_data['recipient_account']
        ).first()
        
        if not existing:
            recipient = SavedRecipient(
                user_id=current_user.id,
                name=transfer_data['recipient_name'],
                account_number=transfer_data['recipient_account']
            )
            db.session.add(recipient)
    
    db.session.add(transaction)
    db.session.commit()
    
    # Store result for display
    session['transfer_result'] = {
        'success': True,
        'reference': transaction.reference_number,
        'amount': transfer_data['amount'],
        'currency': account.currency,
        'recipient': transfer_data['recipient_name']
    }
    
    # Clear transfer data
    session.pop('transfer_data', None)
    
    return jsonify({
        'success': True,
        'redirect': url_for('transfers.transfer_result')
    })


@transfers_bp.route('/transfers/result')
@login_required
def transfer_result():
    """Transfer result page - Step 3"""
    result = session.get('transfer_result')
    
    if not result:
        return redirect(url_for('transfers.new_transfer'))
    
    # Clear result after displaying
    session.pop('transfer_result', None)
    
    return render_template('transfers/result.html', result=result)


@transfers_bp.route('/transfers/cancel', methods=['POST'])
@login_required
def cancel_transfer():
    """Cancel pending transfer (requires reason - prompt alert testing)"""
    reason = request.form.get('reason', '').strip()
    
    if not reason:
        return jsonify({'success': False, 'error': 'Podaj powód anulowania'}), 400
    
    session.pop('transfer_data', None)
    
    return jsonify({'success': True, 'redirect': url_for('dashboard.index')})


@transfers_bp.route('/api/recipients/search')
@login_required
def search_recipients():
    """API: Search saved recipients (for autocomplete)"""
    query = request.args.get('q', '').strip()
    
    # Simulate delay for autocomplete testing
    time.sleep(random.uniform(0.3, 0.8))
    
    if len(query) < 2:
        return jsonify({'recipients': []})
    
    recipients = SavedRecipient.query.filter(
        SavedRecipient.user_id == current_user.id,
        SavedRecipient.name.ilike(f'%{query}%')
    ).limit(5).all()
    
    return jsonify({
        'recipients': [
            {
                'id': r.id,
                'name': r.name,
                'account_number': r.account_number,
                'is_trusted': r.is_trusted
            }
            for r in recipients
        ]
    })


@transfers_bp.route('/api/validate-iban')
@login_required
def validate_iban():
    """API: Validate IBAN format"""
    iban = request.args.get('iban', '').replace(' ', '').upper()
    
    # Basic IBAN validation for Poland
    if not iban:
        return jsonify({'valid': False, 'error': 'Podaj numer konta'})
    
    if not iban.startswith('PL') and not iban[0:2].isdigit():
        # Allow both with and without PL prefix
        if len(iban) == 26 and iban.isdigit():
            return jsonify({'valid': True, 'formatted': 'PL' + iban})
    
    if iban.startswith('PL') and len(iban) == 28:
        return jsonify({'valid': True, 'formatted': iban})
    
    if len(iban) == 26 and iban.isdigit():
        return jsonify({'valid': True, 'formatted': 'PL' + iban})
    
    return jsonify({'valid': False, 'error': 'Nieprawidłowy format numeru konta'})
