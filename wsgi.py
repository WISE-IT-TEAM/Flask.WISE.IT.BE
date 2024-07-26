import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "production")
    app.run(debug=(env == "production"))
