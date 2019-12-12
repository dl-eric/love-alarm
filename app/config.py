import os

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost').replace('\r', '')
REDIS_PASS = os.environ.get('REDIS_PASS', 'password').replace('\r', '')
REDIS_PORT = os.environ.get('REDIS_PORT', '6649').replace('\r', '')
REDIS_URL = os.environ.get('REDIS_URL', '').replace('\r', '')
MONGO_URI = os.environ.get('MONGO_URI', '').replace('\r', '')

# JWT/Auth/Security Stuff
SECRET_KEY = os.environ.get('SECRET_KEY', '').replace('\r', '')
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080 # 7 Days

# Nexmo
NEXMO_API_KEY = os.environ.get('NEXMO_API_KEY', '').replace('\r', '')
NEXMO_SECRET = os.environ.get('NEXMO_SECRET', '').replace('\r', '')

# AWS S3
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', '').replace('\r', '')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', '').replace('\r', '')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY', '').replace('\r', '')
AWS_REGION     = os.environ.get('AWS_REGION', '').replace('\r', '')
S3_URL_EXPIRE_TIME = 300 # 5 minutes

# Wink config
MAX_NUMBER_USER_IMAGES = 10