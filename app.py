import logging

from flask import Flask
from flask_cors import CORS

from club_deportivo.constants import BASE_URL
from club_deportivo.routes.canchas import canchas_bp
from club_deportivo.routes.deportes import deportes_bp
from club_deportivo.routes.reservas import reservas_bp
from club_deportivo.routes.socios import socios_bp

logging.basicConfig(
    level=logging.DEBUG, format="%(levelname)s - %(name)s - %(message)s"
)

app = Flask(__name__)
app.json.sort_keys = False

app.register_blueprint(deportes_bp, url_prefix=BASE_URL)
app.register_blueprint(canchas_bp, url_prefix=BASE_URL)
app.register_blueprint(socios_bp, url_prefix=BASE_URL)
app.register_blueprint(reservas_bp, url_prefix=BASE_URL)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
