from pymongo import MongoClient
import redis
import boto3

from app.config import REDIS_URL, MONGO_URI

r = redis.from_url(REDIS_URL)

print("Redis ping:", r.ping())

mongo = MongoClient(MONGO_URI)
db = mongo.wink

print("Mongo ping:", db.command('ping'))

aws = boto3.client('s3')