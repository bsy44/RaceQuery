import os

from flask import Flask
from flask_cors import CORS
from drivers.driver_controller import driver_bp
from teams.team_controller import team_bp
from races.race_controller import race_bp


app = Flask(__name__)

env_origins = os.environ.get('ALLOWED_ORIGINS')

if env_origins:
    allowed_origins = [origin.strip() for origin in env_origins.split(',')]
else:
    allowed_origins = ["http://localhost:4200"]

CORS(app, resources={r"/*": {"origins": allowed_origins}})

app.register_blueprint(driver_bp)
app.register_blueprint(team_bp)
app.register_blueprint(race_bp)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    is_debug = os.environ.get('FLASK_ENV') == 'development'

    app.run(debug=is_debug, host='0.0.0.0', port=port)