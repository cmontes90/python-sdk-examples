import requests
import json
from PIL import Image, ImageFilter
import shutil
import sys
import os


def image_grey(image_folder, output_folder):

    for filename in os.listdir(image_folder):
        img = Image.open(f'{image_folder}{filename}')
        grey_img = img.convert('L')
        clean_file = os.path.splitext(filename)[0]
        grey_img.save(f'{output_folder}{clean_file}.png', 'png')


def image_scraper(args):
    
    # requesting the digimon API and making a json file with the info that we get
    resp = requests.get("https://digimon-api.vercel.app/api/digimon")
    digimon_list = resp.json()
    
    # Creating the folders where we are going to save the images, if they don't exists
    image_folder = sys.argv[1]
    
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
 
    count = 1
    for character in digimon_list:
            
        if character["level"] == "Champion" and count < 11:
            count += 1
            imgs_url = character["img"]
            filename =  imgs_url.split("/")[-1]
            filepath = f'{image_folder}{filename}'
            r = requests.get(imgs_url, stream = True)

            if r.status_code == 200: 
                r.raw.decode_content = True             

                with open(filepath, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)

                print(f'image succesfully downloaded: {filename}')
            
            else:
                print('Image could not be retreived')
    
    output_folder = sys.argv[2]
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    return image_grey(image_folder, output_folder)


image_scraper(sys.argv[1:])





