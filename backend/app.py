from flask import Flask
from flask_cors import CORS
from backend.controllers.driver_controller import driver_bp

app = Flask(__name__)
CORS(app, origins="*")

app.register_blueprint(driver_bp, url_prefix='/drivers')

if __name__ == "__main__":
    app.run(debug=True)
