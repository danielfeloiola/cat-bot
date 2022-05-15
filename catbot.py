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
import tweepy
from time import sleep
from ssl import SSLError
from requests.exceptions import Timeout, ConnectionError
from urllib3.exceptions import ReadTimeoutError


# functions from the package to check tweets
from helpers import check_safety, check_cat


# Get Twitter keys
if not os.getenv("CONSUMER_KEY"):
    raise RuntimeError("CONSUMER_KEY is not set")


# get twitter api credentials
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_SECRET")

# make the api to retweet cats
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


# Creates a class for the listener
class MyStream(tweepy.Stream):

    # if a new tweet gets found out...
    def on_status(self, status):

        # check if tweet is safe
        check = check_safety(status)

        # if its indeed safe
        if check == True:

            cat_on_image = check_cat(status)
            if cat_on_image == True:


                # tries to retweet the tweet - or just gives up
                try:
                    print('about to retweet')
                    api.retweet(status.id)
                    print('RETWEETED!!!')
                    sleep(3600) # for tweeting every 30 mins
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


# start the kitten machine gun!
stream = MyStream(
    consumer_key, consumer_secret,
    access_token, access_token_secret
)

# error checking
while not stream.running:
    try:
        print("Started listening to stream...")
        stream.filter(track=['cat '])

    except (Timeout, SSLError, ReadTimeoutError, ConnectionError) as e:
        print("Network error. Keep calm and carry on.", str(e))
        sleep(300)

    except Exception as e:
        print(e)

    finally:
        print("Stream has crashed. System will restart twitter stream soon!")


