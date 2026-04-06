from app import create_app, db
from app.models import User, Complaint, SocialWorkImage
from werkzeug.security import generate_password_hash
import os

app = create_app()

with app.app_context():
    db.create_all()

    existing = User.query.filter_by(username='admin').first()
    if not existing:
        # SECURITY FIX: read password from environment variable
        # On Render, set ADMIN_PASSWORD in the environment dashboard
        # Locally, add ADMIN_PASSWORD=yourpassword to your .env file
        admin_password = os.environ.get('ADMIN_PASSWORD')
        if not admin_password:
            raise RuntimeError(
                "\n\n❌ ADMIN_PASSWORD is not set!\n"
                "Add ADMIN_PASSWORD=your_strong_password to your .env file, then run this script.\n"
            )

        admin = User(
            username='admin',
            password=generate_password_hash(admin_password),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created successfully.')
    else:
        print('ℹ️  Admin user already exists — skipped.')

    print('✅ Database and tables ready!')