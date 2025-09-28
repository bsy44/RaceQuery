from flask import Flask
from flask_cors import CORS
from backend.controllers.driver_controller import driver_bp
from backend.controllers.driver_standing_controller import driver_standing_bp
from backend.controllers.team_standing_controller import constructor_standing_bp
from backend.controllers.constructor_controller import contructor_bp

app = Flask(__name__)
CORS(app, origins="*")

app.register_blueprint(driver_bp, url_prefix='/drivers')
app.register_blueprint(contructor_bp, url_prefix='/constructors')
app.register_blueprint(driver_standing_bp, url_prefix='/drivers-standing')
app.register_blueprint(constructor_standing_bp, url_prefix='/constructors-standings')

if __name__ == "__main__":
    app.run(debug=True)
