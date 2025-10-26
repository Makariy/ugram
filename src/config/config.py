import os 
import dotenv


dotenv.load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PORT = os.environ.get("DB_PORT")
DB_PASS = os.environ.get("DB_PASS")

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_PASS = os.environ.get("REDIS_PASS")
REDIS_DB = 0

WEBSOCKET_HOST = os.environ.get("WEBSOCKET_HOST")
WEBSOCKET_PORT = os.environ.get("WEBSOCKET_PORT")

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_GROUP_ID = "messenger"

