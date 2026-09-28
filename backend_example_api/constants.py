import os
from dotenv import load_dotenv

load_dotenv()

# URL base de la API
BASE_URL = ''

# Reglas de dominio
MIN_ID = 1

# Configuracion de la base de datos MySQL (levantada via docker-compose)
DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = int(os.getenv('DB_PORT', '3306'))
DB_USER     = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME     = os.getenv('DB_NAME', 'club_deportivo')
DB_URL      = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Codigos de error
ERROR_CODE_INVALID_BODY      = 'invalid.body'
ERROR_CODE_INVALID_MIN_VALUE = 'invalid.min.value'
