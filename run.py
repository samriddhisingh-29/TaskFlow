import os
from app import create_app
from app.models import db
from app.services import seed_sample_data

# Create application instance using development configuration
app = create_app(os.environ.get("FLASK_CONFIG", "development"))

# Ensure tables and sample data exist upon startup
with app.app_context():
    db.create_all()
    seed_sample_data()

if __name__ == "__main__":
    print("=" * 60)
    print(" TaskFlow — Smart Task & Project Management Dashboard")
    print(" Tagline: 'Plan better. Work smarter.'")
    print(" Running on: http://127.0.0.1:5000")
    print(" Press CTRL+C to quit.")
    print("=" * 60)
    app.run(debug=True, host="127.0.0.1", port=5000)
