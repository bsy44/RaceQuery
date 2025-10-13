from flask import Flask
from flask_cors import CORS
from backend.drivers.driver_controller import driver_standing_bp
from backend.teams.constructor_controller import team_standing_bp
from events.event_controller import event_bp

app = Flask(__name__)
CORS(app, origins="*")

app.register_blueprint(driver_standing_bp, url_prefix='/drivers')
app.register_blueprint(team_standing_bp, url_prefix='/teams')
app.register_blueprint(event_bp, url_prefix='/events')

@app.route('/f1')
def hello():
    return {"message": "Hello from flask"}

if __name__ == "__main__":
    app.run(debug=True)
