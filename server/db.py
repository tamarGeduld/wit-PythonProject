from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["code_analysis_python"]
analysis_collection = db["analysis_history"]


