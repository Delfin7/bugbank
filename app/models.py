"""
Database models for BugBank
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(256), default='default_avatar.png')
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_locked = db.Column(db.Boolean, default=False)
    require_2fa = db.Column(db.Boolean, default=False)
    password_expired = db.Column(db.Boolean, default=False)
    failed_login_attempts = db.Column(db.Integer, default=0)
    
    # Preferences
    language = db.Column(db.String(5), default='pl')
    notifications_enabled = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    accounts = db.relationship('Account', backref='owner', lazy='dynamic')
    messages = db.relationship('Message', backref='recipient', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.username}>'


class Account(db.Model):
    """Bank account model"""
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_number = db.Column(db.String(28), unique=True, nullable=False)
    account_name = db.Column(db.String(64), default='Konto główne')
    account_type = db.Column(db.String(20), default='checking')  # checking, savings, business
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='PLN')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cards = db.relationship('Card', backref='account', lazy='dynamic')
    outgoing_transactions = db.relationship(
        'Transaction',
        foreign_keys='Transaction.from_account_id',
        backref='from_account',
        lazy='dynamic'
    )
    incoming_transactions = db.relationship(
        'Transaction',
        foreign_keys='Transaction.to_account_id',
        backref='to_account',
        lazy='dynamic'
    )
    
    @property
    def formatted_balance(self):
        return f"{self.balance:,.2f} {self.currency}"
    
    @property
    def formatted_account_number(self):
        # Format: XX XXXX XXXX XXXX XXXX XXXX XXXX
        num = self.account_number.replace(' ', '')
        return ' '.join([num[i:i+4] for i in range(0, len(num), 4)])
    
    def __repr__(self):
        return f'<Account {self.account_number}>'


class Transaction(db.Model):
    """Transaction model"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    from_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    to_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    to_account_number = db.Column(db.String(28))  # For external transfers
    to_recipient_name = db.Column(db.String(128))
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='PLN')
    title = db.Column(db.String(256))
    description = db.Column(db.Text)
    transaction_type = db.Column(db.String(20))  # transfer, payment, withdrawal, deposit
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed, cancelled
    reference_number = db.Column(db.String(32), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def formatted_amount(self):
        sign = '-' if self.transaction_type in ['transfer', 'payment', 'withdrawal'] else '+'
        return f"{sign}{self.amount:,.2f} {self.currency}"
    
    def __repr__(self):
        return f'<Transaction {self.reference_number}>'


class Card(db.Model):
    """Bank card model"""
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    card_number = db.Column(db.String(19), unique=True, nullable=False)
    card_holder = db.Column(db.String(64), nullable=False)
    expiry_date = db.Column(db.String(5), nullable=False)  # MM/YY
    cvv = db.Column(db.String(3), nullable=False)
    card_type = db.Column(db.String(20), default='debit')  # debit, credit
    card_brand = db.Column(db.String(20), default='visa')  # visa, mastercard
    is_active = db.Column(db.Boolean, default=True)
    is_blocked = db.Column(db.Boolean, default=False)
    daily_limit = db.Column(db.Float, default=5000.0)
    monthly_limit = db.Column(db.Float, default=50000.0)
    contactless_enabled = db.Column(db.Boolean, default=True)
    internet_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def masked_number(self):
        return f"**** **** **** {self.card_number[-4:]}"
    
    @property
    def formatted_number(self):
        num = self.card_number.replace(' ', '')
        return ' '.join([num[i:i+4] for i in range(0, len(num), 4)])
    
    def __repr__(self):
        return f'<Card {self.masked_number}>'


class Message(db.Model):
    """Internal message model"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender = db.Column(db.String(64), default='BugBank')
    subject = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    is_important = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(20), default='info')  # info, alert, promo, security
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.subject[:30]}>'


class SavedRecipient(db.Model):
    """Saved transfer recipient"""
    __tablename__ = 'saved_recipients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    account_number = db.Column(db.String(28), nullable=False)
    is_trusted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SavedRecipient {self.name}>'
