# lambda-thumbGen-TOSCA-datapipeline
TOSCA Data pipeline to generate thumbnail of images in S3 bucket using Amazon lambda function. Push thumbnail to S3 bucket.  

**Short Description**: Deploying pipelines on multiple Openstack instances that would read, preprocess, and store the image files.  

**Long Description**: 
This data pipeline (DP) implementation can be visualized with below figure. Upon deployment of the DP, _Pipeline1_ will get the list of images present in one AWS S3 bucket (_AWS S3 bucket1_) followed by downloading the images to _Instance-1_. The images will be sent to another instance _Instance-2_. _Pipeline2_ on _Instance-2_ will be responsible for invoking lambda function to process the received images. Further, _Pipeline3_ will be responsible for pushing the processed images to another S3 bucket (_AWS S3 bucket2_).  

In doing so, no data is stored in another instance. The images in _AWS S3 bucket1_ will not be deleted.

![AbstractView](https://drive.google.com/uc?export=view&id=1RH9yjACzeDrhmHwNyCY4zsLfu_z0n1Se)


The *service.yml* template file will have the following tasks:
- Create two instances in openstack environment with Centos atop.
- Install and configure Apache Nifi on both instances
- Deploying and configuring *Pipelines3* atop Nifi on *Instance-2*.
- Deploying and configuring *Pipelines2* atop Nifi on *Instance-2*.
- Deploying and configuring *Pipelines1* atop Nifi on *Instance-1*.

## Preparing the Environment

## 1. Build the lambda function
- `mkdir lambdaFun`
- `cd lambdaFun`
- Download suitable PIL wheel file from [here](https://pypi.org/project/Pillow/#files "here"). This is for the supporting library for resizing the image that we will use in our python script.
- Extract the wheel file and remove the zip file from the current location.
- Write the python code to resize the image (given below). Save the code in `imgResize.py` file.  

**imgResize.py** [\[link to download\]](https://github.com/radon-h2020/lambda-thumbGen-TOSCA-datapipeline/blob/master/LambdaFunction/imgResize.py)
```python
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
```

- Make sure that the current directory contains only the python file and the supporting libraries. 
- Make a ZIP including own python file and the PIL library
    `zip -r9 code.zip .`  

Download the zip [here](https://github.com/radon-h2020/lambda-thumbGen-TOSCA-datapipeline/blob/master/LambdaFunction/thumbGenLambda.zip) and ignore above steps or some unexpected errors

## 2. Upload the function
- Create a lambda function called `imgResizer`.
- Upload `code.zip` to that function.
- Note down “`function name`” and “`region`”

## 3. Create two S3 buckets
- First bucket name: “`radon-utr-thumbgen`”. This is for keeping the original images.
- Second bucket name: “`radon-utr-thumbgen-resized`”. This is for storing the thumbnails.
- Note down the region names of those buckets.
- Upload some `.jpg` images.

# Prerequisites
This demo uses 
- Openstack environment for creating instances
   - we may refer the steps [here](https://github.com/radon-h2020/xopera-opera) to setup OpenStack client.
- Apache Nifi v1.11.1 for pipeline base
- xOpera release 0.5.2 [Download here](https://github.com/radon-h2020/xopera-opera/releases/tag/0.5.2 "Download here").
- TOSCA Simple Profile in YAML Version 1.3 [link](https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.3/TOSCA-Simple-Profile-YAML-v1.3.html)

## Assumptions:
- Openstack environment is ready and you are able to login and create instances through CLI.
- Lambda function is uploaded and tested.
- Two S3 buckets are created.
- Source codes are downloaded in placed in proper place.
## Source code modification:
- In `service.yml`:
	- Update the `template_file`, `cred_file_path`, and `file` under `pipeline3_pushImg`, `pipeline2_invokeLmabda`, and `pipeline1_getS3Img` nodes. 
	- Update `key_name` under `vmone` and `vmtwo` nodes
	- Update *properties values* under `vmone` and `vmtwo` nodes, if required.
- In `credentials file`: 
	- Update the access key and secret key to invoke AWS services
	- Update the template file path mentioned in the pipeline nodes.




# Execution:
- Setup the virtual environment
- Connect to openstack environment
- Execute the following command
`Opera deploy service.yml`


# Acknowledgement

This project has received funding from the European Union’s Horizon 2020 research and innovation programme under Grant Agreement No. 825040 (RADON).
