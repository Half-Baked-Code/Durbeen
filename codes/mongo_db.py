import os
from pymongo import MongoClient

url = "mongodb://192.168.1.9:27017"
db_name = "MyUstad"
mongo_client = MongoClient(url)
db_mongo = mongo_client[db_name]
mdDumps = db_mongo["mds"]

folder_path = r"C:\Users\user\Desktop\Tasks\Durbeen\markdowns"

for filename in os.listdir(folder_path):
    if filename.endswith(".md"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        doc = {
            "filename": filename,
            "content": content,
            "path": os.path.abspath(file_path),
        }

        print(f"Dumping document: {filename}")  # 👈 Print before dumping
        mdDumps.insert_one(doc)

print("All markdown files inserted.")
