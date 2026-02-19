"""
Seed data for BugBank - creates test users and sample data
"""

import random
import string
from datetime import datetime, timedelta
from app import db
from app.models import User, Account, Transaction, Card, Message, SavedRecipient


def generate_account_number():
    """Generate Polish IBAN-like account number"""
    return 'PL' + ''.join(random.choices(string.digits, k=26))


def generate_card_number():
    """Generate card number"""
    return ''.join(random.choices(string.digits, k=16))


def generate_reference():
    """Generate transaction reference number"""
    return 'TRX' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


def seed_database():
    """Seed database with test data"""
    
    # Check if data already exists
    if User.query.first() is not None:
        print("📦 Database already seeded, skipping...")
        return
    
    print("🌱 Seeding database...")
    
    # ===================
    # CREATE USERS
    # ===================
    
    users_data = [
        {
            'username': 'standard_user',
            'email': 'standard@bugbank.pl',
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'phone': '+48 123 456 789',
            'is_locked': False,
            'require_2fa': False,
            'password_expired': False
        },
        {
            'username': '2fa_user',
            'email': '2fa@bugbank.pl',
            'first_name': 'Anna',
            'last_name': 'Nowak',
            'phone': '+48 987 654 321',
            'is_locked': False,
            'require_2fa': True,
            'password_expired': False
        },
        {
            'username': 'locked_user',
            'email': 'locked@bugbank.pl',
            'first_name': 'Piotr',
            'last_name': 'Zablokowany',
            'phone': '+48 111 222 333',
            'is_locked': True,
            'require_2fa': False,
            'password_expired': False
        },
        {
            'username': 'expired_user',
            'email': 'expired@bugbank.pl',
            'first_name': 'Maria',
            'last_name': 'Wygasła',
            'phone': '+48 444 555 666',
            'is_locked': False,
            'require_2fa': False,
            'password_expired': True
        },
        {
            'username': 'empty_user',
            'email': 'empty@bugbank.pl',
            'first_name': 'Tomasz',
            'last_name': 'Pusty',
            'phone': '+48 777 888 999',
            'is_locked': False,
            'require_2fa': False,
            'password_expired': False
        },
        {
            'username': 'rich_user',
            'email': 'rich@bugbank.pl',
            'first_name': 'Bogdan',
            'last_name': 'Bogaty',
            'phone': '+48 000 111 222',
            'is_locked': False,
            'require_2fa': False,
            'password_expired': False
        }
    ]
    
    users = {}
    for user_data in users_data:
        user = User(**user_data)
        user.set_password('password123')
        db.session.add(user)
        users[user_data['username']] = user
    
    db.session.commit()
    
    # ===================
    # CREATE ACCOUNTS
    # ===================
    
    # Standard user - 2 accounts
    acc1 = Account(
        user_id=users['standard_user'].id,
        account_number=generate_account_number(),
        account_name='Konto osobiste',
        account_type='checking',
        balance=15420.50,
        currency='PLN'
    )
    acc2 = Account(
        user_id=users['standard_user'].id,
        account_number=generate_account_number(),
        account_name='Konto oszczędnościowe',
        account_type='savings',
        balance=50000.00,
        currency='PLN'
    )
    db.session.add_all([acc1, acc2])
    
    # 2FA user - 1 account
    acc3 = Account(
        user_id=users['2fa_user'].id,
        account_number=generate_account_number(),
        account_name='Konto główne',
        account_type='checking',
        balance=8750.00,
        currency='PLN'
    )
    db.session.add(acc3)
    
    # Expired user - 1 account
    acc4 = Account(
        user_id=users['expired_user'].id,
        account_number=generate_account_number(),
        account_name='Konto osobiste',
        account_type='checking',
        balance=3200.00,
        currency='PLN'
    )
    db.session.add(acc4)
    
    # Rich user - multiple accounts for pagination testing
    rich_accounts = []
    account_types = ['checking', 'savings', 'business']
    currencies = ['PLN', 'EUR', 'USD', 'GBP']
    
    for i in range(12):
        acc = Account(
            user_id=users['rich_user'].id,
            account_number=generate_account_number(),
            account_name=f'Konto {i+1}',
            account_type=random.choice(account_types),
            balance=round(random.uniform(1000, 500000), 2),
            currency=random.choice(currencies)
        )
        rich_accounts.append(acc)
        db.session.add(acc)
    
    db.session.commit()
    
    # ===================
    # CREATE CARDS
    # ===================
    
    # Standard user cards
    card1 = Card(
        account_id=acc1.id,
        card_number=generate_card_number(),
        card_holder='JAN KOWALSKI',
        expiry_date='12/27',
        cvv='123',
        card_type='debit',
        card_brand='visa',
        daily_limit=5000.0
    )
    card2 = Card(
        account_id=acc1.id,
        card_number=generate_card_number(),
        card_holder='JAN KOWALSKI',
        expiry_date='06/26',
        cvv='456',
        card_type='credit',
        card_brand='mastercard',
        daily_limit=10000.0
    )
    db.session.add_all([card1, card2])
    
    # 2FA user card
    card3 = Card(
        account_id=acc3.id,
        card_number=generate_card_number(),
        card_holder='ANNA NOWAK',
        expiry_date='03/28',
        cvv='789',
        card_type='debit',
        card_brand='visa'
    )
    db.session.add(card3)
    
    # Rich user cards
    for acc in rich_accounts[:5]:
        card = Card(
            account_id=acc.id,
            card_number=generate_card_number(),
            card_holder='BOGDAN BOGATY',
            expiry_date=f'{random.randint(1,12):02d}/{random.randint(25,30)}',
            cvv=str(random.randint(100, 999)),
            card_type=random.choice(['debit', 'credit']),
            card_brand=random.choice(['visa', 'mastercard']),
            daily_limit=random.choice([5000, 10000, 20000, 50000])
        )
        db.session.add(card)
    
    db.session.commit()
    
    # ===================
    # CREATE TRANSACTIONS
    # ===================
    
    transaction_titles = [
        'Przelew własny',
        'Zakupy online - Amazon',
        'Płatność kartą - Żabka',
        'Wypłata z bankomatu',
        'Przelew za czynsz',
        'Zwrot za zakupy',
        'Wynagrodzenie',
        'Płatność za telefon',
        'Netflix - subskrypcja',
        'Spotify - subskrypcja',
        'Allegro - zakupy',
        'Przelew do znajomego',
        'Opłata za prąd',
        'Opłata za gaz',
        'Ubezpieczenie samochodu'
    ]
    
    transaction_types = ['transfer', 'payment', 'withdrawal', 'deposit']
    statuses = ['completed', 'completed', 'completed', 'pending']  # Mostly completed
    
    # Transactions for standard user
    for i in range(25):
        days_ago = random.randint(0, 90)
        trans = Transaction(
            from_account_id=acc1.id,
            to_account_number=generate_account_number(),
            to_recipient_name=f'Odbiorca {i+1}',
            amount=round(random.uniform(10, 2000), 2),
            currency='PLN',
            title=random.choice(transaction_titles),
            transaction_type=random.choice(transaction_types),
            status=random.choice(statuses),
            reference_number=generate_reference(),
            created_at=datetime.utcnow() - timedelta(days=days_ago)
        )
        db.session.add(trans)
    
    # Transactions for rich user (many for pagination)
    for i in range(150):
        days_ago = random.randint(0, 365)
        source_acc = random.choice(rich_accounts)
        trans = Transaction(
            from_account_id=source_acc.id,
            to_account_number=generate_account_number(),
            to_recipient_name=f'Kontrahent {i+1}',
            amount=round(random.uniform(100, 50000), 2),
            currency=source_acc.currency,
            title=random.choice(transaction_titles),
            transaction_type=random.choice(transaction_types),
            status=random.choice(statuses),
            reference_number=generate_reference(),
            created_at=datetime.utcnow() - timedelta(days=days_ago)
        )
        db.session.add(trans)
    
    db.session.commit()
    
    # ===================
    # CREATE MESSAGES
    # ===================
    
    messages_data = [
        {
            'subject': 'Witamy w BugBank!',
            'content': '''Szanowny Kliencie,

Witamy w BugBank! Cieszymy się, że do nas dołączyłeś.

Twoje konto zostało pomyślnie aktywowane. Możesz teraz korzystać ze wszystkich funkcji naszego systemu bankowości internetowej.

Pozdrawiamy,
Zespół BugBank''',
            'category': 'info',
            'is_important': True
        },
        {
            'subject': 'Nowa wersja aplikacji mobilnej',
            'content': '''Informujemy o dostępności nowej wersji aplikacji mobilnej BugBank.

Nowości:
- Szybsze logowanie biometryczne
- Nowy wygląd dashboardu
- Powiadomienia push o transakcjach

Zaktualizuj aplikację już dziś!''',
            'category': 'info',
            'is_important': False
        },
        {
            'subject': '⚠️ Próba logowania z nowego urządzenia',
            'content': '''Wykryliśmy próbę logowania na Twoje konto z nowego urządzenia.

Data: wczoraj, 15:32
Lokalizacja: Warszawa, Polska
Urządzenie: Chrome na Windows

Jeśli to nie byłeś Ty, natychmiast zmień hasło i skontaktuj się z nami.''',
            'category': 'security',
            'is_important': True
        },
        {
            'subject': 'Promocja: Cashback 5% na zakupy online',
            'content': '''Specjalna oferta dla Ciebie!

Przez najbliższe 30 dni otrzymasz 5% cashback na wszystkie zakupy online płacone kartą BugBank.

Maksymalny cashback: 500 PLN
Oferta ważna do końca miesiąca.

Szczegóły w regulaminie promocji.''',
            'category': 'promo',
            'is_important': False
        },
        {
            'subject': 'Potwierdzenie zmiany limitu karty',
            'content': '''Informujemy, że limit dzienny Twojej karty został zmieniony.

Nowy limit: 5000 PLN
Data zmiany: dzisiaj

Jeśli nie dokonywałeś tej zmiany, skontaktuj się z nami.''',
            'category': 'alert',
            'is_important': False
        }
    ]
    
    # Add messages to standard, 2fa, and rich users
    for user_key in ['standard_user', '2fa_user', 'rich_user']:
        for i, msg_data in enumerate(messages_data):
            msg = Message(
                user_id=users[user_key].id,
                sender='BugBank',
                subject=msg_data['subject'],
                content=msg_data['content'],
                category=msg_data['category'],
                is_important=msg_data['is_important'],
                is_read=(i > 1),  # First 2 unread
                created_at=datetime.utcnow() - timedelta(days=i*3)
            )
            db.session.add(msg)
    
    # Extra messages for rich user (pagination testing)
    for i in range(50):
        msg = Message(
            user_id=users['rich_user'].id,
            sender='BugBank System',
            subject=f'Powiadomienie systemowe #{i+1}',
            content=f'To jest automatyczne powiadomienie numer {i+1}. Lorem ipsum dolor sit amet.',
            category=random.choice(['info', 'alert', 'promo']),
            is_read=random.choice([True, False]),
            created_at=datetime.utcnow() - timedelta(days=i)
        )
        db.session.add(msg)
    
    db.session.commit()
    
    # ===================
    # CREATE SAVED RECIPIENTS
    # ===================
    
    recipients_data = [
        {'name': 'Adam Mickiewicz', 'is_trusted': True},
        {'name': 'Firma XYZ Sp. z o.o.', 'is_trusted': True},
        {'name': 'Zakład Energetyczny', 'is_trusted': True},
        {'name': 'Telekomunikacja SA', 'is_trusted': False},
        {'name': 'Jan Nowak', 'is_trusted': False},
    ]
    
    for user_key in ['standard_user', '2fa_user', 'rich_user']:
        for rec_data in recipients_data:
            recipient = SavedRecipient(
                user_id=users[user_key].id,
                name=rec_data['name'],
                account_number=generate_account_number(),
                is_trusted=rec_data['is_trusted']
            )
            db.session.add(recipient)
    
    db.session.commit()
    
    print("✅ Database seeded successfully!")
    print(f"   - {len(users_data)} users created")
    print(f"   - Multiple accounts, cards, transactions, and messages created")
