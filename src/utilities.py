''' Captcha Breaker Utilities

 Author: Bradley Reeves
   Date: 04/27/2021
Contact: reevesbra@outlook.com

'''

import cv2
import numpy as np
import imutils

WHITE = (255, 255, 255)

class Utilities:
    @staticmethod
    def display_image(image):
        ''' Display an image
            Parameters
            ----------
            image : numpy ndarray
                Image to display
            Returns
            -------
            None
        '''
        cv2.imshow("window name", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def to_grayscale(image):
        ''' Transform captcha image to grayscale
            Parameters
            ----------
            image : numpy ndarray
                Image to transform
            Returns
            -------
            numpy ndarray
                Transformed image
        '''
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def threshold_image(image):
        ''' Binarizes image pixels
            Parameters
            ----------
            image : numpy ndarray
                Image to threshold
            Returns
            -------
            numpy ndarray
                Thresholded image
        '''
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    @staticmethod
    def dilate_chars(image):
        ''' Ensure char strokes are contiguous
            by slightly expanding them
            Parameters
            ----------
            image : numpy ndarray
                Image to dilate
            Returns
            -------
            numpy ndarray
                Dilated image
        '''
        kernel = np.ones((2, 2), np.uint8) 
        return cv2.dilate(image, kernel, iterations = 1)

    @staticmethod
    def find_contours(image):
        ''' Compute contours of chars in captcha image
            Parameters
            ----------
            image : numpy ndarray
                Captcha image to process
            Returns
            -------
            list numpy ndarrays
                Countours for each char in image
        '''
        return cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    @staticmethod
    def compute_bounding_rects(contours):
        ''' Computes the bounding rects of the contours
            Parameters
            ----------
            contours : list of numpy ndarrays
                Countours for each char in image
            Returns
            -------
            list of (x, y, w, h)
                Char bounding rectangles
        '''
        return list(map(cv2.boundingRect, contours))

    @staticmethod
    def show_bounding_rects(rects, image):
        ''' Display captcha with bounding rects
            Parameters
            ----------
            rects : list of (x, y, w, h)
                Bounding rectangles
            image : numpy ndarray
                Captcha image
            Returns
            -------
            None
        '''
        for rect in rects:
            x, y, w, h = rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        __display(image)

    @staticmethod
    def split_rects(rects):
        ''' Split rects that bounded multiple chars
            Parameters
            ----------
            rects : list of (x, y, w, h)
                Bounding rectangles
            Returns
            -------
            list of (x, y, w, h)
                New bounding rectangles
        '''
        char_bounding_rects = []
        for rect in rects:
            (x, y, w, h) = rect
            if w/h > 1.25:
                half_width = int(w/2)
                char_bounding_rects.append((x, y, half_width, h))
                char_bounding_rects.append((x + half_width, y, half_width, h))
            else:
                char_bounding_rects.append(rect)
        return char_bounding_rects

    @staticmethod
    def get_char_images(rects, image):
        ''' Extract chars defined by bounding rects
            Parameters
            ----------
            rects : list of (x, y, w, h)
                Char bounding rects
            image : numpy ndarray
                Captcha image
            Returns
            -------
            char_images : list of numpy ndarrays
                Extracted char images
        '''
        char_images = []
        for rect in rects:
            x, y, w, h = rect
            char_image = image[y - 1:y + h + 1, x - 1:x + w + 1]
            char_images.append(char_image)
        return char_images

    @staticmethod
    def sort_bounding_rects(rects):
        ''' Sort bounding rects by x coordinate
            Parameters
            ----------
            rects : list of (x, y, w, h)
                Char bounding rects
            Returns
            -------
            list of (x, y, w, h)
                Sorted bounding rects
        '''
        return(sorted(rects, key = lambda x: float(x[0])))

    @staticmethod
    def read_image(file_path):
        ''' Initialize PreProcessor instance
            Parameters
            ----------
            file_path : string
                Image path
            Returns
            -------
            numpy ndarray
                Image
        '''
        return cv2.imread(file_path)

    @staticmethod
    def normalize(image, desired_width=20, desired_height=20):
        ''' Resize image to desired dimensions
            Parameters
            ----------
            image : numpy ndarray
                Image
            desired_width : integer
                New image width
            desired_height : integer
                New image height
            Returns
            -------
            new_image : numpy ndarray
                Scaled image
        '''
        (h, w) = image.shape[:2]

        if w > h:
            image = imutils.resize(image, width=desired_width)
        else:
            image = imutils.resize(image, height=desired_height)

        width_padding = int((desired_width - image.shape[1])/2)
        height_padding = int((desired_height - image.shape[0])/2)

        new_image = cv2.copyMakeBorder(image, height_padding, height_padding, width_padding, width_padding, cv2.BORDER_CONSTANT, value=WHITE)
        new_image = cv2.resize(new_image, (desired_width, desired_height), interpolation=cv2.INTER_AREA)

        return new_image

    @staticmethod
    def reshape(image):
        ''' Adds dummy dimension to fit keras 
            input requirements
            Parameters
            ----------
            image : numpy ndarray
                Image to modify
            Returns
            -------
            numpy ndarray
                Reshaped image
        '''
        return np.expand_dims(image, axis=2)


