import requests
import json
from PIL import Image, ImageFilter
import sys
import boto3
import io

session = boto3.Session(profile_name="A4L-MASTER")
s3 = session.client("s3")
bucket_name = "cmontes-images"


def modify_images(file_content, filename):

    img = Image.open(io.BytesIO(file_content))
    grey_img = img.convert("L")

    filename = filename.split(".")[0]
    file_png = f"{filename}.png"
    folder = "new_images/"

    put_objects(file_content, file_png, folder)


def put_objects(file_content, filename, folder):

    put_object = s3.put_object(
        Body=file_content, Bucket=bucket_name, Key=f"{folder}{filename}"
    )
    object_status = put_object["ResponseMetadata"]["HTTPStatusCode"]

    if object_status == 200:
        print(f"File: {filename} has been uploaded it to S3 on folder {folder}")
        print("")

    else:
        print(f"File: {filename} could not be uploaded it")

    if folder == "original/":
        modify_images(file_content, filename)


def get_img():
    #  take only 10 images from the request that are in level training

    url = "https://digimon-api.vercel.app/api/digimon"
    resp = requests.get(url)

    if resp.status_code == 200:
        digimon_list = resp.json()
        count = 1

        for char in digimon_list:
            if (
                char["level"] == "In Training"
                or char["level"] == "Rookie"
                and count < 6
            ):
                count += 1
                img_url = char["img"]
                filename = img_url.split("/")[-1]
                r = requests.get(img_url, stream=True)

                if r.status_code == 200:
                    r_body = r.content
                    folder = "original/"
                    print(f"File: {filename} retreived from API")
                    put_objects(r_body, filename, folder)

                else:
                    print("Data could not be retreived from the API")
                    sys.exit(1)

    else:
        print(f"ERROR: {resp}")
        print(f"Something went wrong with the request, please check the API: \n{url}")
        sys.exit(1)
    print("")


get_img()


# # take the images form the bucket transform to PNG and black and white
# # Save the images in a new prefix
# # erase the first images from the bucket
