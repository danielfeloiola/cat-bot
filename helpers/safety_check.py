''''
 ________  ___  ___  ________  ________     
|\   __  \|\  \|\  \|\   __  \|\   __  \    
\ \  \|\  \ \  \\\  \ \  \|\  \ \  \|\  \   
 \ \   ____\ \  \\\  \ \   _  _\ \   _  _\  
  \ \  \___|\ \  \\\  \ \  \\  \\ \  \\  \| 
   \ \__\    \ \_______\ \__\\ _\\ \__\\ _\ 
    \|__|     \|_______|\|__|\|__|\|__|\|__|
                                            
'''

###############################################################################
# A BOT THAT RETWETS IMAGES OF CATS                                           #
# This file checks the tweet for unsafe words                                 #
# and calls the computer vision function to check for cats in the pictures    #
###############################################################################

import os
import json
import requests

# img stuff
from io import BytesIO
from PIL import Image
from PIL import ImageFile

# db stuff
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# TF detector
from .cat_detector import cat_detector

# make a database
uri = os.getenv("DATABASE_URI")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
engine = create_engine(uri)
db = scoped_session(sessionmaker(bind=engine))

# create an OAuthHandler
if not os.getenv("CONSUMER_KEY"):
    raise RuntimeError("CONSUMER_KEY is not set")


def check_safety(status):
    '''
    check if a tweet is adequate
    Looks for bad words on username, text and description
    checks if threre is a image on the tweet
    '''

    # get tweet out of json package
    tweet_json = json.dumps(status._json)
    tweet = json.loads(tweet_json)

    # get words from db and put them on a list
    safe_list_db = db.execute("SELECT * FROM slist").fetchall()
    slist = []
    for item in safe_list_db:
        slist.append(item[0])

    # check if there is indeed a picture in it
    # don't bother checking words if there's no image
    if ('media' in status.entities):

        # Make sure it's not a RT
        if status.retweeted or 'RT @' in status.text:
            print('-----------------------> RT!')
            return False

        # check for evil cucumbers or kpop on the tweet
        if any(word in status.text.lower() for word in slist):
            print('-----------------------> unsafe - text: ')
            print(status.text)
            return False

        # check user name
        if any(word in tweet['user']['name'].lower() for word in slist):
            print('-----------------------> unsafe - name: ')
            print(tweet['user']['name'])
            return False

        # if the tweet is not marked as sensitive:
        if tweet['possibly_sensitive'] == True:
            print('Marked as sensitive by Twitter')
            return False
        else:
            print('not sensitive and contains image')
            return True

    else:
        print('-----------------------> no image on the tweet')
        return False


def check_cat(status):
    '''
    Checks if there is a cat on the image using TensorFlow
    '''

    for image in status.entities['media']:

        url = image['media_url']
        print("URL ------>" + url)
        filename = 'temp.png'

        # send a get request to get the image
        request = requests.get(url, stream=True)
        if request.status_code == 200:

            # read data from downloaded bytes and returns a PIL.Image.Image object
            i = Image.open(BytesIO(request.content))

            # Saves the image under the given filename
            i.save(filename)

            # call the detector function
            cat = cat_detector("temp.png")

            # confirm if a cat is detected 
            if cat == True:
                # say its safe
                print('GOT A CATTO!')
                print(status.text)
                return True
            else:
                return False

        # if the request for the image fails return false
        else:
            print("unable to download image")
            return False


if __name__ == '__main__':
    pass