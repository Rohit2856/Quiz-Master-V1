from application import create_app, db
from application.models import db  # Import db from models.py
from flask_migrate import Migrate

app = create_app()  # Create the Flask app instance

# Initialize Flask-Migrate
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run()

app.config.from_object('config.DevelopmentConfig')