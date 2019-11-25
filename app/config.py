import os

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost').replace('\r', '')
REDIS_PASS = os.environ.get('REDIS_PASS', 'password').replace('\r', '')
REDIS_PORT = os.environ.get('REDIS_PORT', 6649).replace('\r', '')
MONGO_URI = os.environ.get('MONGO_URI', '').replace('\r', '')

# JWT/Auth/Security Stuff
SECRET_KEY = os.environ.get('SECRET_KEY', '').replace('\r', '')
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30