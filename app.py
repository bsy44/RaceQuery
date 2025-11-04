from flask import Flask
from flask_cors import CORS
from drivers.driver_controller import driver_bp
from teams.team_controller import team_bp
from events.event_controller import event_bp

app = Flask(__name__)
CORS(app, origins="*")

app.register_blueprint(driver_bp, url_prefix='/drivers')
app.register_blueprint(team_bp, url_prefix='/teams')
app.register_blueprint(event_bp, url_prefix='/events')

@app.route('/f1')
def hello():
    return {"message": "Hello from flask"}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
