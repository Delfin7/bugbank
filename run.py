#!/usr/bin/env python
"""
BugBank - Training Application for Selenium Testers
Run this file to start the application.
"""

import argparse
from app import create_app, db
from app.seed_data import seed_database


def main():
    parser = argparse.ArgumentParser(description='BugBank Application')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--reset-db', action='store_true', help='Reset database with fresh data')
    args = parser.parse_args()
    
    app = create_app()
    
    with app.app_context():
        if args.reset_db:
            print("🔄 Resetting database...")
            db.drop_all()
        
        db.create_all()
        seed_database()
        print("✅ Database ready!")
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🏦 BugBank - Aplikacja Treningowa dla Testerów         ║
    ║                                                           ║
    ║   Aplikacja działa na: http://{args.host}:{args.port:<5}               ║
    ║                                                           ║
    ║   Użytkownicy testowi:                                    ║
    ║   • standard_user / password123  - normalne logowanie     ║
    ║   • 2fa_user / password123       - wymaga 2FA             ║
    ║   • locked_user / password123    - zablokowane konto      ║
    ║   • expired_user / password123   - wygasłe hasło          ║
    ║   • empty_user / password123     - brak danych            ║
    ║   • rich_user / password123      - dużo danych            ║
    ║                                                           ║
    ║   Naciśnij Ctrl+C aby zatrzymać serwer                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host=args.host, port=args.port, debug=True)


if __name__ == '__main__':
    main()
