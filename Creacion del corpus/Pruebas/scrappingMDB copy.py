from datetime import datetime
from itertools import repeat
from pymongo import MongoClient
from os import listdir
import gridfs
import base64
import instaloader
L = instaloader.Instaloader()

# Optionally, login or load session
#L.login(USER, PASSWORD)        # (login)
#L.interactive_login(USER)      # (ask password on terminal)
L.load_session_from_file('luislc99','/home/luis/session-luisdevtest.txt')

def storeImages(dir, post_id):
    img_id = []
    i = 0
    media = listdir(dir)
    for m in media:
        with open(f"{dir}/{m}", "rb") as imageFile:
            img_enc = base64.b64encode(imageFile.read())
        img_data = {
#            'id': f'{post_id}{i}',
            'post_id': post_id,
            'image': img_enc
        }
        i+=1
        id = fs.put(img_data)
        img_id.append(id)
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

def procesarRespuesta(respuesta):

    if type(respuesta) is instaloader.PosPostCommentAnswer:
        return []
    coms = []
    comsid = []

    for comment in respuesta.answers:
        post_data = {
                    'id': comment.id,
                    'parent_id': respuesta.id,
                    'profile': comment.owner.username,
                    'date': comment.created_at_utc.isoformat(),
                    'text':comment.text,
                    'comments': procesarRespuesta(comment),
                    }
    if len(coms) > 0:
        collection_comments.insert_many(coms)
    
    return comsid

def procesarComentarios(post):
    coms = []
    comsid = []

    for comment in post.get_comments():

        post_data = {
            'id': comment.id,
            'parent_id': post.mediaid,
            'profile': comment.owner.username,
            'date': comment.created_at_utc.isoformat(),
            'text':comment.text,
            'comments': procesarRespuesta(comment),
        }
        print('get_comm')
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

    return data_to_store 
    
                               
def scrap(hashtags):

    hashtags_iter = [instaloader.Hashtag.from_name(L.context, hashtag).get_posts_resumable() for hashtag in hashtags]

    i = 0
    for retrieved in hashtags_iter:
        for post in retrieved:
            procesado = procesarPost(post)
            collection_post.insert_many([procesado])
            i+=1
            print(i)
            if i >= 10:
                print('Finished')
                return None

def get_database():
 
   # Provide the mongodb atlas url to connect python to mongodb using pymongo
   CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.1"
   client = MongoClient(CONNECTION_STRING)
 
   return client['Instagram']
dbname = get_database()
collection_post = dbname["Post"]
collection_comments = dbname["Comments"]
fs = gridfs.GridFS(database)

hashtags = ['noalaborto','salvemoslasdosvidas','sialavida','mareaverde','quesealey','provida']
scrap(hashtags)