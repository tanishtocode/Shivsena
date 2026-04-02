from app import create_app, db
from app.models import User, Complaint, SocialWorkImage
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()

    # Create admin user if not exists
    existing = User.query.filter_by(username='admin').first()
    if not existing:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created — username: admin, password: admin123')

    print('✅ Database and tables created successfully!')