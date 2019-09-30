'''

 ________   ________   _________   ________   ________   _________
|\   ____\ |\   __  \ |\___   ___\|\   __  \ |\   __  \ |\___   ___\
\ \  \___| \ \  \|\  \\|___ \  \_|\ \  \|\ /_\ \  \|\  \\|___ \  \_|
 \ \  \     \ \   __  \    \ \  \  \ \   __  \\ \  \\\  \    \ \  \
  \ \  \____ \ \  \ \  \    \ \  \  \ \  \|\  \\ \  \\\  \    \ \  \
   \ \_______\\ \__\ \__\    \ \__\  \ \_______\\ \_______\    \ \__\
    \|_______| \|__|\|__|     \|__|   \|_______| \|_______|     \|__|

'''
########################################################################
# A BOT THAT RETWETS IMAGES OF CATS                                    #
# version: idk, probably a trillion?                                   #
# follow me on twitter meow                                            #
# made by me                                                           #
########################################################################

# import libraries needed
import os
import json
import tweepy
import requests

from time import sleep
from ssl import SSLError
from requests.exceptions import Timeout, ConnectionError
from urllib3.exceptions import ReadTimeoutError
from io import BytesIO
from PIL import Image
from PIL import ImageFile

# import the list with words to block
from setup import slist
#from cat_detector import cv_cat_detector


# create an OAuthHandler
consumer_key = '1Wd25mHfJ344bUO0A7ApPsh7q'
consumer_secret = 'NqbcMRO2hh5Z3ooxLS3UmcnnDYLjKwA3LkpPU7OeFbMNi9sORb'
access_token = '1177596135529226240-C5ZnVSj8Pi7jBzzWZ4hcxvs7pz2RLR'
access_token_secret = 'He6eI8SRwFwqQrwd2HC2f1PUhAYIjPrsZlbv7AlWH5O6A'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def check_safety(status):
#check if a tweet is violent or contains porn

    # get tweet out of json package
    tweet_json = json.dumps(status._json)
    tweet = json.loads(tweet_json)

    # Ignore tweets with no text or description or name
    if status.text == None:
        print("no status")
        return False
    #if tweet['user']['description'] == None:
    #    print("no descripton")
    #ca    return False
    if tweet['user']['name'] == None:
        print("no name")
        return False

    # Make sure it's not a RT
    if (not status.retweeted) and ('RT @' not in status.text) and ('media' in status.entities):

        if not any(word in status.text.lower() for word in slist):

            if not any(word in tweet['user']['description'].lower() for word in slist):

                if not any(word in tweet['user']['name'].lower() for word in slist):

                    if tweet['possibly_sensitive'] == False:

                        for image in status.entities['media']:

                            url = image['media_url']
                            print("URL ------>" + url)

                            filename = 'temp.png'

                            # send a get request
                            request = requests.get(url, stream=True)
                            if request.status_code == 200:

                                # read data from downloaded bytes and returns a PIL.Image.Image object
                                i = Image.open(BytesIO(request.content))

                                # Saves the image under the given filename
                                i.save(filename)

                                # call computer vision function
                                cats = cv_cat_detector()

                                if cats == True:

                                    # say its safe
                                    print('Got a safe tweet')
                                    print(status.text)
                                    return True
                                else:
                                    return False

                            else:
                                print("unable to download image")
                                return False

                    # SHOW REMOVED TWEETS
                    # if the tweet has kpop or porn on the username:
                    else:
                        print('FOUND A UNSAFE ONE!!! - possibly_sensitive')
                        print(status.text)
                        print(tweet['user']['name'])
                        print(tweet['user']['description'])
                        return False

                # SHOW REMOVED TWEETS
                # if the tweet has kpop or porn on the username:
                else:
                    print('FOUND A UNSAFE ONE!!! - NAME')
                    print(status.text)
                    print(tweet['user']['name'])
                    print(tweet['user']['description'])
                    return False

            # if the tweet has kpop or porn on the user description:
            else:
                print('FOUND A UNSAFE ONE!!! - DESCRIPTION')
                print(status.text)
                print(tweet['user']['name'])
                print(tweet['user']['description'])
                return False

        # if the tweet has kpop or porn on the text:
        else:
            print('FOUND A UNSAFE ONE!!! - TEXT')
            print(status.text)
            print(tweet['user']['name'])
            print(tweet['user']['description'])
            return False


# Creates a class for the listener
class MyStreamListener(tweepy.StreamListener):

    # if a new tweet gets found out...
    def on_status(self, status):

        # check if tweet is safe
        check = check_safety(status)

        # if its indeed safe
        if check == True:

            # tries to retweet the tweet - or just gives up
            try:
                print('about to retweet')
                api.retweet(status.id)
                print('RETWEETED!!!')
                sleep(1800) # for tweeting every 50 mins
                print('done sleeping!')
            except:
                print('passing...')
                pass


    # if there is any error
    def on_error(self, status_code):

        # Being rate limited for making too many requests.
        if status_code == 420:
            print('ERROR 420: Too many requests')
            sleep(300)
            print('Back to work!')
            return True

        # Cannot retweet the same Tweet more than once
        if status_code == 327:
            print('ERROR 327: You have already retweeted this Tweet')
            return True

def cv_cat_detector():

    # import the necessary packages
    #import argparse
    import cv2

    image = cv2.imread ("temp.png", 1)
    #image = i

    # load the input image and convert it to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #resized_img = cv2.resize(img, (500,500))
    resized_img = cv2.resize(image, (int(image.shape[1]/2),int(image.shape[0]/2)))

    # load the cat detector Haar cascade, then detect cat faces
    # in the input image
    detector = cv2.CascadeClassifier("haarcascade_frontalcatface.xml")

    #rects = detector.detectMultiScale(gray, scaleFactor=1.3,
    #	minNeighbors=10, minSize=(75, 75))

    rects = detector.detectMultiScale(resized_img, scaleFactor=1.3,
        minNeighbors=10, minSize=(75,75))

    # loop over the cat faces and draw a rectangle surrounding each
    for (i, (x, y, w, h)) in enumerate(rects):
    	cv2.rectangle(resized_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    	cv2.putText(resized_img, "Cat #{}".format(i + 1), (x, y - 10),
    		cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)


    # show the detected cat faces
    #cv2.imshow("Cat Faces", resized_img)
    #cv2.waitKey(0)

    if len(rects) == 0:
        print("no catto on image :(")
        return False

    else:
        print("catto on image!!! Catto on image!! :3 ")
        return True

# Start a stream listener to look for tweets with puppies
myStreamListener = MyStreamListener()
stream = tweepy.Stream(auth, myStreamListener)

while not stream.running:
    try:
        # start stream
        print("Started listening to stream...")
        stream.filter(track=['cat '])

    except (Timeout, SSLError, ReadTimeoutError, ConnectionError) as e:
        # if there is a connection error
        print("Network error. Keep calm and carry on.", str(e))
        sleep(300)

    except Exception as e:
        # if there is another kind of error
        print(e)

    finally:
        # wars about the crash
        print("Stream has crashed. System will restart twitter stream soon!")

# if error escapes jail...
print("This error was so bad I have no idea what it was!")
