#!/usr/bin/python

import os
from os import path
import boto3
import datetime


# GET Datetime NOW
now  = datetime.datetime.now()
config_create_date = now.strftime('%Y%d%m%H%M%S')

# Amazon S3 client
s3_client = boto3.client('s3', region_name='us-west-2')
s3_resource = boto3.resource('s3', region_name='us-west-2')

s3_list = []
def check_against_s3_objects():
    """Build a list of S3 objects already in S3
    We then match the current file against the list to avoid double downloads

    :param s3_pdf_name: PDF Filename to check if exists
    :return: True if exists, else False
    """
    try:
        my_bucket = s3_resource.Bucket('bpwa.pdf-storage')
        for my_bucket_object in my_bucket.objects.all():
            #copy_object('bpwa.pdf-storage', str(my_bucket_object.key))
            s3_list.append(my_bucket_object.key)
    except Exception as e:
        exit(1)

def copy_object(bucket, mylist):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    # Upload the file
    for t in mylist:
        try:
            #response = s3_resource.Object(bucket, key_name).put(Body=str(object))
            # Copy object A as object B
            #key_name = 'wybk.2022bk20065.51117-0.pdf'
            new_obejct = t.replace("-0.pdf", "-petition.pdf")
            copy_source = {'Bucket': bucket, 'Key': t}
            s3_client.copy_object(Bucket=bucket, CopySource=copy_source, Key=new_obejct, MetadataDirective='REPLACE')
            #s3_resource.copyObject(bucket, new_obejct).copy_from(
            #CopySource=f"{bucket}/{key_name}")
            #s3_client.delete_object(Bucket=bucket, Key=key_name)
        except Exception as e:
            print(f'S3 COPY Failed: {e}')
            pass
    return True




def main():
    check_against_s3_objects()
    copy_object('bpwa.pdf-storage', s3_list)

# MAIN
if __name__ == '__main__':
    main()
