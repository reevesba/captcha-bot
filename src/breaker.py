''' Captcha Breaking Bot

 Author: Bradley Reeves
   Date: 04/27/2021
Contact: reevesbra@outlook.com

'''

import utilities
import time
import urllib.request
import pickle
import os
import numpy as np
from selenium import webdriver
from keras.models import Sequential
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.layers.core import Flatten, Dense

class BreakerBot:
    def __init__(self):
        ''' Initialize BreakerBot instance
            Parameters
            ----------
            self : object
                BreakerBot instance
            Returns
            -------
            None
        '''
        self.util = utilities.Utilities()

    def __captcha_to_char_pipeline(self, file_path):
        ''' Extract and preprocess char images from captcha
            Parameters
            ----------
            self : object
                BreakerBot instance
            file_path : string
                Location of captcha image
            Returns
            -------
            char_images : list of numpy ndarrays
                Char images extracted from captcha
        '''
        captcha_image = self.util.read_image(file_path)

        # Transform image
        transformed_image = self.util.to_grayscale(captcha_image)
        transformed_image = self.util.threshold_image(transformed_image)
        transformed_image = self.util.dilate_chars(transformed_image)

        # Get contours for extracting characters
        image_contours = self.util.find_contours(transformed_image)

        # Extract and store character images
        char_bounding_rects = self.util.split_rects(self.util.compute_bounding_rects(image_contours))
        char_bounding_rects = self.util.sort_bounding_rects(char_bounding_rects)
        char_images = self.util.get_char_images(char_bounding_rects, captcha_image)

        return char_images

    def __load_classifier(self):
        ''' Load model for classification tasks
            Parameters
            ----------
            self : object
                BreakerBot instance
            Returns
            -------
            model : Keras instance
                Model used to predict chars
        '''
        num_classes = 32

        model = Sequential()
        model.add(Conv2D(20, (5, 5), padding="same", input_shape=(20, 20, 1), activation="relu"))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
        model.add(Conv2D(50, (5, 5), padding="same", activation="relu"))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
        model.add(Flatten())
        model.add(Dense(512, activation="relu"))
        model.add(Dense(num_classes, activation="softmax"))
        model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
        model.load_weights("../out/weights.h5")
        return model
        

    def __load_label_binarizer(self):
        ''' Load binarizer from file
            Parameters
            ----------
            self : object
                BreakerBot instance
            Returns
            -------
            LabelBinarizer instance
                For transforming binary vectors into labels
        '''
        return pickle.load(open("../out/binarizer.pkl", "rb"))

    def __load_model(self):
        ''' Load classifier and label binarizer
            Parameters
            ----------
            self : object
                BreakerBot instance
            Returns
            -------
            Keras instance
                Model used to predict chars
            LabelBinarizer instance
                For transforming binary vectors into labels
        '''
        return (self.__load_classifier(), self.__load_label_binarizer())

    def __predict_chars(self, char_images, model, label_binarizer):
        ''' Predict captcha chars
            Parameters
            ----------
            self : object
                BreakerBot instance
            char_images : list of numpy ndarrays
                Char images extracted from captcha
            model : Keras instance
                Model used to predict chars
            label_binarizer : LabelBinarizer instance
                For transforming binary vectors into labels
            Returns
            -------
            predicted_text : numpy ndarray of chars
                Captcha prediction
        '''
        X = []
        for char_image in char_images:
            image = self.util.to_grayscale(char_image)
            image = self.util.normalize(image)
            image = self.util.reshape(image)
            X.append(image)

        X = np.array(X, dtype="float")/255.0
        pred = model.predict(X)
        predicted_text = label_binarizer.inverse_transform(pred)
        return predicted_text

    def execute(self):
        ''' Solve captchas
            Parameters
            ----------
            self : object
                BreakerBot instance
            Returns
            -------
            None
        '''
        # Initialize chromedriver
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        driver.get("https://reevesba.github.io/captcha-bot/")
        time.sleep(2)

        # Extract captcha image from page
        captcha_image = driver.find_element_by_css_selector(".captcha-image")
        src = captcha_image.get_attribute("src")
        urllib.request.urlretrieve(src, "captcha.png")

        # Do predictions
        model, label_binarizer = self.__load_model()
        char_images = self.__captcha_to_char_pipeline("captcha.png")
        pred = self.__predict_chars(char_images, model, label_binarizer)

        # Submit the prediction
        captcha_input = driver.find_element_by_name("captcha-input")
        captcha_input.send_keys(pred)
        captcha_input.click()
        time.sleep(5)
        driver.quit()

        # Cleanup
        if os.path.exists("captcha.png"): os.remove("captcha.png")

        
