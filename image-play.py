import requests
import json
from PIL import Image, ImageFilter
import sys
import boto3
import botocore
import logging

s3 = boto3.client('s3')
paginator = s3.get_paginator('list_objects_v2')
bucket_name = 'cmontes-images'
folder = 'original/'
new_folder = 'new_images/'

def modify_images():
    
    
    iterator = paginator.paginate(Bucket=bucket_name, Prefix=folder)

    for page in iterator:
        if "Contents" in page:
            for key in page["Contents"]:
                keystring = key["Key"]
                
                objects=s3.get_object(
                Bucket=bucket_name,
                Key=keystring
                )

                object_body=objects['Body']
                img = Image.open(object_body, mode='r')
                grey_img = img.convert('L')

                img_byte = io.BytesIO()
                grey_img.save(img_byte, format='PNG')
                img_byte = img_byte.getvalue()

                filename = keystring.split('/')[1].split('.')[0]'.png'

                upload_images(img_byte, filename)
                
                put_object = s3.put_object(
                    Body=img_byte_arr,
                    Bucket= bucket_name,
                    Key=f'{new_folder}{filename}
                    ) 


def upload_images(file_content, filename):

    # Create the bucket 
    try:    
        create_bucket = s3.create_bucket(Bucket=bucket_name)
        bucket_status = create_bucket['ResponseMetadata']['HTTPStatusCode']
       
        if bucket_status == 200:
            put_object = s3.put_object(
            Body=file_content,
            Bucket=bucket_name,
            Key=f'{folder}{filename}'
            )    

    except botocore.exceptions.ClientError as error:
        print("Bucket already exist")
        raise error

    else: 
        print(f'File: {filename} upload to folder {folder} on S3')
        #modify_images()
    
    
def get_img():
#  take only 10 images from the request that are in level training
    
    url = "https://digimon-api.vercel.app/api/digimon"
    resp = requests.get(url)
    
    if resp.status_code == 200:
        digimon_list = resp.json()
        count = 1

        for char in digimon_list:
            if char['level'] == 'In Training' or char['level'] == 'Rookie' and count < 11:
                count += 1
                img_url = char['img']
                filename = img_url.split('/')[-1]
                r = requests.get(img_url, stream=True)
                r_body = r.content            
                
                if r.status_code == 200:
                    upload_images(r_body, filename)
                
                else: 
                    print("Data could not be retreived from the API")
                    sys.exit
        
    else: 
        print(f'ERROR: {resp}')
        print(f"Something went wrong with the request, please check the API: \n{url}")
        sys.exit
        

get_img()

# take the images form the bucket transform to PNG and black and white
# Save the images in a new prefix
# erase the first images from the bucket







