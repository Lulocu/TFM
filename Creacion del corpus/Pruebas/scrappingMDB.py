from datetime import datetime
from itertools import repeat
from shutil import rmtree
from pymongo import MongoClient
from os import listdir
import gridfs
import base64

import instaloader
USER = 'luisdevtest'
L = instaloader.Instaloader()
L.save_metadata = False
L.post_metadata_txt_pattern = ''
# Optionally, login or load session
#L.login(USER, PASSWORD)        # (login)
L.interactive_login(USER)      # (ask password on terminal)


def storeImages(dir, post_id):
    img_id = []
    media = listdir(dir)
    for m in media:
        with open(f"{dir}/{m}", "rb") as imageFile:
            img_enc = base64.b64encode(imageFile.read())
        id = fs.put(img_enc)
        img_id.append(id)

    dbname["Comments"].insert_one({"id":id,'post_id': post_id})
    return img_id

def zip_longest(list_of_iters, fillvalue=None):
    # zip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
    iterators = [iter(it) for it in list_of_iters]
    num_active = len(iterators)
    if not num_active:
        return
    while True:
        values = []
        for i, it in enumerate(iterators):
            try:
                value = next(it)
            except StopIteration:
                num_active -= 1
                if not num_active:
                    return
                iterators[i] = repeat(fillvalue)
                value = fillvalue
            values.append(value)
        yield tuple(values)

def procLocation(post):
    try:
        location = post.location.name
    except:
        location = 'None'
    return location

def procSponsor(post):
    if len(post.sponsor_users)>0:
        sponsor_users= [user.username for user in post.sponsor_users]
    else:
        sponsor_users= post.sponsor_users
    return sponsor_users

def procesarComentarios(post):
    coms = []
    comsid = []

    for comment in post.get_comments():
        resp = []
        respid = []
        for respuesta in comment.answers:

            data = {
                'id': respuesta.id,
                'parent_id': comment.id,
                'profile': respuesta.owner.username,
                'date': respuesta.created_at_utc.isoformat(),
                'text':respuesta.text,
            }
            resp.append(data)
            respid.append(respuesta.id)
            
        post_data = {
            'id': comment.id,
            'parent_id': post.mediaid,
            'profile': comment.owner.username,
            'date': comment.created_at_utc.isoformat(),
            'text':comment.text,
            'comments': respid,
        }
        if len(resp) > 0:
            collection_comments.insert_many(resp)

        coms.append(post_data)
        comsid.append(comment.id)
 

    if len(coms) > 0:
        collection_comments.insert_many(coms)
    
    return comsid


def procesarPost(post):

    data_to_store = {
        'id': post.mediaid,
        'title': post.title,
        'profile': post.profile,
        'date': post.date,
        'caption': post.caption,
        'tagged_users': post.tagged_users,
        'accessibility_caption': post.accessibility_caption,
        'n_comments': post.comments,
        'caption_hashtags': post.caption_hashtags,
        'caption_mentions': post.caption_mentions,
        'likes': post.likes,
        'url': f'https://www.instagram.com/p/{post.shortcode}',
        'tagged_users': post.tagged_users,
        'location': procLocation(post),
        'sponsor_users': procSponsor(post),
        'comments': procesarComentarios(post),
    }

    time = datetime.now()
    downloaded = L.download_post(post, 'temp')

    if downloaded:
        
        data_to_store['images'] = storeImages('temp', post.mediaid)
        try:
            rmtree('temp')
        except:
            pass

    return data_to_store 
    
                               
def scrap(hashtags):

    hashtags_iter = [instaloader.Hashtag.from_name(L.context, hashtag).get_posts_resumable() for hashtag in hashtags]

    i = 0
    for retrieved in hashtags_iter:
        for post in retrieved:
            procesado = procesarPost(post)
            collection_post.insert_many([procesado])
            i+=1
            if i >= 10000:
                print(f'Retrieved {i}')

def get_database():
 
   # Provide the mongodb atlas url to connect python to mongodb using pymongo
   CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.1"
   client = MongoClient(CONNECTION_STRING)
 
   return client['Instagram']
dbname = get_database()
collection_post = dbname["Post"]
collection_comments = dbname["Comments"]
fs = gridfs.GridFS(dbname,collection='Images')

hashtags = ['noalaborto','salvemoslasdosvidas','sialavida','mareaverde','quesealey','provida']
scrap(hashtags)