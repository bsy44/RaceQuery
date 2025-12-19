from flask import Flask
from flask_cors import CORS
from drivers.driver_controller import driver_bp
from teams.team_controller import team_bp
from races.race_controller import event_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(driver_bp)
app.register_blueprint(team_bp)
app.register_blueprint(event_bp)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
