''' Split captchas into character images

 Author: Bradley Reeves
   Date: 04/27/2021
Contact: reevesbra@outlook.com

'''

import os
import cv2
from utilities import Utilities

class PreProcessor:
    def __init__(self, directory):
        ''' Initialize PreProcessor instance
            Parameters
            ----------
            self : object
                PreProcessor instance
            directory : string
                Location of captcha images
            Returns
            -------
            None
        '''
        if directory != "":
            self.captchas = self.__extract_captchas(directory)
        else:
            self.captchas = None
            raise ValueError("No captcha directory provided.")

        self.util = Utilities()

    def __extract_captchas(self, directory):
        ''' Load captcha images
            Parameters
            ----------
            self : object
                PreProcessor instance
            directory : string
                Location of captcha images
            Returns
            -------
            list of strings
                All captcha image paths
        '''
        return [os.path.join(directory, f) for f in os.listdir(directory)]

    def __get_label(self, image):
        ''' Get captcha image label
            Parameters
            ----------
            self : object
                PreProcessor instance
            image : string
                Captcha image path
            Returns
            -------
            label : string
                Captcha label
        '''
        filename = os.path.basename(image)
        label = filename.split(".")[0]
        return label

    def __to_array(self, image):
        ''' Read captcha image
            Parameters
            ----------
            self : object
                PreProcessor instance
            image : string
                Captcha image path
            Returns
            -------
            numpy ndarray
                Image as array
        '''
        return cv2.imread(image)

    def preprocess(self):
        ''' Convert captcha images to character images
            Parameters
            ----------
            self : object
                PreProcessor instance
            Returns
            -------
            None
        '''
        output_dir = "../dat/char_imgs"
        char_counts = {}

        for image in self.captchas:
            captcha_label = self.__get_label(image)
            captcha_image = self.__to_array(image)

            # Transform image
            transformed_image = self.util.to_grayscale(captcha_image)
            transformed_image = self.util.threshold_image(transformed_image)
            transformed_image = self.util.dilate_chars(transformed_image)

            # Get contours for extracting characters
            image_contours = self.util.find_contours(transformed_image)

            # Create and save character images
            char_bounding_rects = self.util.split_rects(self.util.compute_bounding_rects(image_contours))
            char_bounding_rects = self.util.sort_bounding_rects(char_bounding_rects)
            char_images = self.util.get_char_images(char_bounding_rects, captcha_image)

            for char_image, current_char in zip(char_images, captcha_label):
                if len(char_images) == 4:
                    save_dir = os.path.join(output_dir, current_char)
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir)
                    char_count = char_counts.get(current_char, 0)
                    image_save_path = os.path.join(save_dir, str(char_count) + ".png")
                    cv2.imwrite(image_save_path, char_image)
                    char_counts[current_char] = char_count + 1


