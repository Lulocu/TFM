from pymongo import MongoClient
from os import listdir
import gridfs
import base64
import matplotlib.pyplot as plt
import numpy as np

def get_database():
 
   # Provide the mongodb atlas url to connect python to mongodb using pymongo
   CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.1"
   client = MongoClient(CONNECTION_STRING)
 
   return client['Instagram']
dbname = get_database()
collection_post = dbname["Post"]
collection_comments = dbname["Comments"]
fs = gridfs.GridFS(dbname,collection='Images')

for post in collection_post.find():
    #print(a['images'])
    img_id = post['images']

img_id = img_id[0]
image_coded = fs.get(img_id).read()
image = base64.b64decode(image_coded)
with open('image.png', 'wb')  as outfile:   
    outfile.write(image)  # Write your data 
print('a')