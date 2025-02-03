from flask import current_app as app
from .database import db

@app.route('/initialize_db')
def initialize_db():
    """
    Route to initialize the database schema.
    
    This will create all tables defined in models.py.
    
    Warning: Running this route will drop all existing tables and recreate them.
             Use with caution in production environments.
    
    Returns:
        str: Success message after initializing the database.
    """
    
    # Drop all existing tables (if any) and recreate them
    with app.app_context():
        try:
            # Drop all tables (for development purposes only!)
            db.drop_all()
            
            # Create new tables based on models.py definitions
            db.create_all()
            
            return "Database initialized successfully!"
        except Exception as e:
            return f"An error occurred while initializing the database: {str(e)}"
