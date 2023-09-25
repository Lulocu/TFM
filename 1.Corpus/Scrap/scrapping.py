
import argparse
import sys

import instaloader
from pymongo import MongoClient

def process_location(post):
    try:
        location = post.location.name
    except AttributeError:
        location = 'None'
    return location

def process_sponsor(post):
    if len(post.sponsor_users)>0:
        sponsor_users= [user.username for user in post.sponsor_users]
    else:
        sponsor_users= post.sponsor_users
    return sponsor_users


def pocess_comments(puiblication):

    comments = []
    comments_id = []

    for comment in puiblication.get_comments():

        comments_com_id, comments_com = pocess_comments(comment)

        comment_data = {
            'id': comment.id,
            'parent_id': puiblication.mediaid,
            'profile': comment.owner.username,
            'date': comment.created_at_utc.isoformat(),
            'text':comment.text,
            'comments': comments_com_id,
        }

        comments.append(comment_data)
        comments_id.append(comment.id)

        comments.append(comments_com)

    return comments_id, comments


def process_post(post):

    comments_id, comments = pocess_comments(post)

    post_data = {
        'id': post.mediaid,
        'title': post.title,
        'profile': post.profile,
        'date': post.date,
        'caption': post.caption,
        'accessibility_caption': post.accessibility_caption,
        'n_comments': post.comments,
        'caption_hashtags': post.caption_hashtags,
        'caption_mentions': post.caption_mentions,
        'likes': post.likes,
        'url': f'https://www.instagram.com/p/{post.shortcode}',
        'tagged_users': post.tagged_users,
        'location': process_location(post),
        'sponsor_users': process_sponsor(post),
        'comments': comments_id,
    }

    return post_data, comments


def scrap(L, database, hashtag, post_collection, comment_collection):

    L.save_metadata = False
    L.download_video_thumbnails = False
    L.download_comments = False
    L.post_metadata_txt_pattern = ""

    posts = instaloader.Hashtag.from_name(L.context, hashtag).get_posts_resumable()

    for post in posts:
        post_data, comment_data = process_post(post)
        L.download_post(post, target=f"{post.mediaid}")
        database[post_collection].insert_one(post_data)
        if len(comment_data) > 0:
            database[comment_collection].insert_many(comment_data)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A script to scrap an Instagram hashtag")

    scrap_args = parser.add_argument_group("Scrapping")

    scrap_args.add_argument("-a", "--hashtag", type=str, required= True,
                        help="Hashtag to scrap. It must not include #")
    scrap_args.add_argument("-u", "--username", type=str, required= True,
                        help="Instagram username")
    scrap_args.add_argument("-c","--cookies", type=str, required= True,
                        help="Filepath to cookies session")
    
    mongodb_args = parser.add_argument_group("Scrapping")

    mongodb_args.add_argument("-du","--database_uri", type=str, required= False,
    default= "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.1",
                        help="MongoDB string connection")
    mongodb_args.add_argument("-dn","--database_name", type=str, required= False, default= "Instagram",
                        help="MongoDB database name")
    mongodb_args.add_argument("-dp","--database_post", type=str, required= False, default= "Post",
                        help="MongoDB Posts collection")
    mongodb_args.add_argument("-dc","--database_comment", type=str, required= False, default= "Comment",
                    help="MongoDB Comment collection")
    args = parser.parse_args()

    L = instaloader.Instaloader()

    try:
        L.load_session_from_file(args.username,args.cookies)
    except FileNotFoundError:
        print("Error: cookies file not found")
        sys.exit()

    try:
        db = MongoClient(args.database_uri)[args.database_name]
    except AttributeError:
        print("Error: DB not found")
        sys.exit()

    scrap(L, db, args.hashtag, args.database_post, args.database_comment)
