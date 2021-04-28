''' Keras Deep Learning Model

 Author: Bradley Reeves
   Date: 04/27/2021
Contact: reevesbra@outlook.com

'''

import os
import numpy as np
import pickle
from utilities import Utilities
from imutils import paths
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from tensorflow.keras import backend
from keras.models import Sequential
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.layers.core import Flatten, Dense
from ann_visualizer.visualize import ann_viz

class CNN:
    def __init__(self, directory):
        ''' Initialize CNN instance
            Parameters
            ----------
            self : object
                CNN instance
            directory : string
                Location of char images
            Returns
            -------
            None
        '''
        self.util = Utilities()
        self.images, self.labels = self.__get_images_labels(directory)
        self.binarizer = None

    def __get_images_labels(self, directory):
        ''' Load character images and labels
            Parameters
            ----------
            self : object
                CNN instance
            directory : string
                Location of char images
            Returns
            -------
            images : list of numpy ndarrays
                Preprocessed images
            labels : list of strings
                Char image labels
        '''
        images = []
        labels = []

        for file_path in paths.list_images(directory):
            image = self.util.read_image(file_path)
            image = self.util.to_grayscale(image)
            image = self.util.normalize(image)
            image = self.util.reshape(image)
            images.append(image)
            label = file_path.split(os.path.sep)[-2]
            labels.append(label)

        return (images, labels)

    def __get_X_y(self):
        ''' Initialize CNN instance
            Parameters
            ----------
            self : object
                CNN instance
            Returns
            -------
            X : numpy ndarray
                Model input vectors
            y : numpy ndarray
                Labels transformed to binary vectors
        '''
        X = np.array(self.images, dtype="float")/255.0
        labels = np.array(self.labels)
        self.binarizer = LabelBinarizer().fit(labels)
        y = self.binarizer.transform(labels)
        return (X, y)

    def create_model(self):
        ''' Create, train, and save Keras model
            Parameters
            ----------
            self : object
                CNN instance
            Returns
            -------
            None
        '''
        num_classes = len(set(self.labels))

        # Build model
        model = Sequential()
        model.add(Conv2D(20, (5, 5), padding="same", input_shape=(20, 20, 1), activation="relu"))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
        model.add(Conv2D(50, (5, 5), padding="same", activation="relu"))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
        model.add(Flatten())
        model.add(Dense(512, activation="relu"))
        model.add(Dense(num_classes, activation="softmax"))
        model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

        # View model details
        #model.summary()
        #ann_viz(model, title="CNN Model Visualization")

        # Train model
        X, y = self.__get_X_y()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True)
        model.fit(X_train, y_train, validation_data=(X_test, y_test), batch_size=32, epochs=5, verbose=1)

        # Save model
        pickle.dump(self.binarizer, open("../out/binarizer.pkl", "wb"))
        model.save_weights("../out/weights.h5")



