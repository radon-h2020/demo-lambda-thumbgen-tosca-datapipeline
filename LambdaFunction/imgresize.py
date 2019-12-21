import PIL
from PIL import Image
import base64


def write_to_file(save_path, data):
  with open(save_path, "wb") as f:
    f.write(base64.b64decode(data))


def lambda_handler(event, context):    
    # get the image from the "body" which is encoded in some format and is in the HTTP request itself.
    write_to_file("/tmp/photo.jpg", event["body"])
    
    size = 64, 64 # size of thumbnail img
    print("Open the image from /tmp/ dir")
    img = Image.open('/tmp/photo.jpg')
    print("Creating the thumbnail")
    img.thumbnail(size)
    print("Saving the thumbnail")
    img.save( "/tmp/photo_thumbnail.jpg", "JPEG")


    # open again for encoding
    with open("/tmp/photo_thumbnail.jpg", "rb") as imageFile:
      str = base64.b64encode(imageFile.read())
      encoded_img = str.decode("utf-8")

    print("Print the encoded image:")
    print(encoded_img)
    print("# Now return the encoded img.\n")

    return {
      "isBase64Encoded": True,
      "statusCode": 200,
      "headers": { "content-type": "image/jpeg"},
      "body": encoded_img
    }
