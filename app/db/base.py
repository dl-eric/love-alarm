from pymongo import MongoClient
import redis

from app.config import REDIS_HOST, REDIS_PASS, REDIS_PORT, MONGO_URI

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, db=0)

mongo = MongoClient(MONGO_URI)
db = mongo.wink