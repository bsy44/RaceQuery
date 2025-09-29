from flask import Flask, render_template
from flask_cors import CORS
from controllers.driver_controller import driver_bp
from controllers.driver_standing_controller import driver_standing_bp
from controllers.team_standing_controller import constructor_standing_bp
from controllers.constructor_controller import contructor_bp
from controllers.circuit_controller import circuit_bp
from controllers.race_controller import race_bp
from controllers.result_controller import result_bp
from controllers.qualifying_controller import qualifying_bp
from controllers.sprint_controller import sprint_bp

app = Flask(__name__)
CORS(app, origins="*")

app.register_blueprint(driver_bp, url_prefix='/drivers')
app.register_blueprint(contructor_bp, url_prefix='/constructors')
app.register_blueprint(circuit_bp, url_prefix='/circuits')
app.register_blueprint(race_bp, url_prefix='/race')
app.register_blueprint(qualifying_bp, url_prefix='/qualifyng')
app.register_blueprint(sprint_bp, url_prefix='/sprint')
app.register_blueprint(result_bp, url_prefix='/results')
app.register_blueprint(driver_standing_bp, url_prefix='/drivers-standings')
app.register_blueprint(constructor_standing_bp, url_prefix='/constructors-standings')

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
