from app import create_app

app = create_app()

if __name__ == "__main__":
    # SECURITY FIX: debug=False — debug=True in production exposes your entire server
    # For local development, set DEBUG=true in your .env instead
    import os
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)