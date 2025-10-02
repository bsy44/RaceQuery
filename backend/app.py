from flask import Flask
from flask_cors import CORS
from backend.drivers.driver_controller import driver_standing_bp
from backend.teams.constructor_controller import team_standing_bp
from circuits.circuit_controller import circuit_bp
from races.race_controller import race_bp

app = Flask(__name__)
CORS(app, origins="*")

app.register_blueprint(driver_standing_bp, url_prefix='/standings/drivers')
app.register_blueprint(team_standing_bp, url_prefix='/standings/teams')
app.register_blueprint(circuit_bp, url_prefix='/circuits')
app.register_blueprint(race_bp, url_prefix='/races')

@app.route('/f1')
def hello():
    return {"message": "Hello from flask"}

if __name__ == "__main__":
    app.run(debug=True)
