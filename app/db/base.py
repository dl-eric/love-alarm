from pymongo import MongoClient
import redis
import boto3

from app.config import REDIS_URL, MONGO_URI, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION

r = redis.from_url(REDIS_URL)

print("Redis ping:", r.ping())

mongo = MongoClient(MONGO_URI)
db = mongo.wink

print("Mongo ping:", db.command('ping'))

aws = boto3.client('s3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION)
