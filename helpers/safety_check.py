###############################################################################
# A BOT THAT RETWETS IMAGES OF CATS                                           #
# This file checks the tweet for unsafe words                                 #
# and calls the computer vision function to check for cats in the pictures    #                                                          #
###############################################################################

# img stuff
from io import BytesIO
from PIL import Image
from PIL import ImageFile

# db stuff
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# TF detector
#from cat_app import cat_detector
from computer_vision.cat_detector import cat_detector

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

    # start checking if its a safe tweet
    # returns false if the test fails

    # Make sure it's not a RT
    if status.retweeted:
        print('------------------------------------------')
        print("RT!")
        print('------------------------------------------')
        return False
    if 'RT @' in status.text:
        print('------------------------------------------')
        print("RT!")
        print('------------------------------------------')
        return False

    # check if there is indeed a picture in it
    if ('media' in status.entities):

        # looking for bad words

        # check for p*rn or kpop on the tweet
        if any(word in status.text.lower() for word in slist):
            print('')
            print('------------------------------------------')
            print('')
            print('unsafe - text')
            print(status.text)
            #print(tweet['user']['name'])
            #print(tweet['user']['description'])
            print('')
            print('------------------------------------------')
            print('')
            return False


        # check user name
        if any(word in tweet['user']['name'].lower() for word in slist):
            print('')
            print('------------------------------------------')
            print('')
            print('unsafe - name')
            #print(status.text)
            print(tweet['user']['name'])
            #print(tweet['user']['description'])
            print('')
            print('------------------------------------------')
            print('')
            return False

        # if the tweet is not marked as sensitive:
        if tweet['possibly_sensitive'] == False:
            print('not sensitive')

            return True

    else:

        print('------------------------------------------\n\n')
        print("no image on the tweet\n\n")
        print('------------------------------------------\n\n')

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

            # if a cat is detected return true
            # else return false
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