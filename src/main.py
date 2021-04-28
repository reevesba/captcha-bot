''' Captcha Breaking Driver

 Author: Bradley Reeves
   Date: 04/27/2021
Contact: reevesbra@outlook.com

'''
from preprocessor import PreProcessor
from model import CNN
from breaker import BreakerBot

def main():
    # 1. Preprocess training data
    do_pp = input("Would you like to preprocess captcha images for training? [Y/n]:")
    if do_pp in ['', ' ', 'Y', 'y', 'Yes', 'yes']:
        print("Splitting captchas into character images...")
        pp = PreProcessor("../dat/captchas")
        pp.preprocess()

    # 2. Create and train model
    do_train = input("Would you like to train a new model? [Y/n]:")
    if do_train in ['', ' ', 'Y', 'y', 'Yes', 'yes']:
        print("Building and training CNN...")
        model = CNN("../dat/char_imgs")
        model.create_model()

    # 3. Run the bot
    print("Executing bot...")
    bot = BreakerBot()
    bot.execute()

    print("Process complete!")

if __name__ == '__main__':
    print("-----------------------------------------------------------------")
    print("                 ╔═╗ ┌─┐ ┌─┐  ╔╗  ┌─┐ ┌┬┐                        ")
    print("                 ║   ├─┤ ├─┘  ╠╩╗ │ │  │                         ")
    print("                 ╚═╝ ┴ ┴ ┴    ╚═╝ └─┘  ┴                         ")
    print("                                    v1.0                         ")
    print("-----------------------------------------------------------------")

    main()
