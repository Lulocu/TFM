from datetime import datetime
from itertools import dropwhile, takewhile
import csv

import instaloader
L = instaloader.Instaloader()

# Optionally, login or load session
#L.login(USER, PASSWORD)        # (login)
#L.interactive_login(USER)      # (ask password on terminal)
L.load_session_from_file('luisdevtest','/home/luis/session-luisdevtest.txt')

def procesarComentarios(comentarios):

    coms = []
    for comment in comentarios:
        profile =  f"'Autoria': {comment.owner.username}"
        text = f"'Comentario': {comment.text}'"
        date = f"'Fecha': {comment.created_at_utc.isoformat()}"
        try:
            respuestas = f'Respuestas: {procesarComentarios(comment[5])}'
        except:
            respuestas = f'Respuestas: []'
        coms.append({profile,text,date,respuestas})
    return coms
def procesarPost(post,hashtag,nPost,csvwriter):
    L.download_post(post, f"post{nPost}")
    post = {
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
    }

    if len(post.sponsor_users)>0:

        sponsor_users= [user.username for user in post.sponsor_users]

    else:
        sponsor_users= post.sponsor_users
    tagged_users= post.tagged_users
    comments = procesarComentarios(post.get_comments())
    try:
        location = post.location.name
    except:
        location = 'None'

    csvwriter.writerow([title,location,profile,date,caption,tagged_users,accessibility_caption,n_comments,comments,caption_hashtags,caption_mentions,likes,sponsor_users,tagged_users,f'=HIPERVINCULO("/post{nPost}")'])

def scrap(hashtag):
    posts = instaloader.Hashtag.from_name(L.context, hashtag).get_posts_resumable()
    #posts = instaloader.Profile.from_username(L.context, "luislc99").get_posts()


    SINCE = datetime.fromisoformat('2022-06-24')
    UNTIL = datetime.fromisoformat('2022-07-24')
    #a = list(dropwhile(lambda p: p.date > UNTIL, posts))
    #for element in a:
    #    print(element.date)

    #a = list(takewhile(lambda p: p.date > SINCE, posts))
    #for element in a:
    #    print(element.date)
    with open(f'{hashtag}.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='~',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL,lineterminator='\n')
        i = 0
        csvwriter.writerow(['title','location','profile','date','caption','tagged_users','accessibility_caption','Number of comments','comments','caption_hashtags','caption_mentions','likes','sponsor_users','tagged_users','Ruta a archivos multimeda'])
        for post in takewhile(lambda p: p.date > SINCE, dropwhile(lambda p: p.date > UNTIL, posts)):
            
            
            procesarPost(post,hashtag,i,csvwriter)
            i+=1
            if i >= 64:
            #    print(hashtag)
                return None

scrap('salvemoslasdosvidas')