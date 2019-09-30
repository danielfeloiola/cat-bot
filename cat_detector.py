
def cv_cat_detector():

    # import the necessary packages
    #import argparse
    import cv2

    image = cv2.imread ("temp.png", 1)

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
    cv2.imshow("Cat Faces", resized_img)
    cv2.waitKey(0)

    if len(rects) == 0:
        print("no catto on iage :(")
        return False

    else:
        print("catto on image!!! Catto on image!! :3 ")
        return True
