#!/usr/bin/python

import os
from os import path
import boto3
import datetime
import logging



## Set up logging
log_file_path = path.join(path.dirname(path.abspath(__file__)), '/app/logging/logging.ini')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger(__name__)
logger_list = ['boto', 'boto3', 'chardet', 'urllib3', 'botocore', 's3transfer', 'PIL']
for i in logger_list:
    logging.getLogger(i).setLevel(logging.CRITICAL) #sets all #logging sources to crit level

# GET Datetime NOW
now  = datetime.datetime.now()
config_create_date = now.strftime('%Y%d%m%H%M%S')

# Amazon S3 client
s3_client = boto3.client('s3', region_name='us-west-2')
s3_resource = boto3.resource('s3', region_name='us-west-2')

def check_against_s3_objects(s3_pdf_name, case_link=None):
    """Build a list of S3 objects already in S3
    We then match the current file against the list to avoid double downloads

    :param s3_pdf_name: PDF Filename to check if exists
    :return: True if exists, else False
    """
    objects = None
    results = None
    filename_prefix = s3_pdf_name[0:6]

    pdf_file_name = s3_pdf_name

    logging.debug(pdf_file_name)

    try:
        objects = s3_client.list_objects_v2(
            Bucket='bpwa.pdf-storage',
            Prefix=filename_prefix
            )
    except Exception as e:
        logging.info('Failed to list S3 objects')
        logging.error(e)
        exit(1)

    if objects != None:
        count = 0
        logging.info('Found ' + str(objects['KeyCount']) + ' S3 objects matching prefix')
        s3_objects = []
        while count < objects['KeyCount']:
            s3_objects.append(objects['Contents'][count]['Key'])
            count += 1
        if pdf_file_name in s3_objects:
            return True
        else:
            return False
    else:
        return False

def download_pdf_from_s3_archive(s3_pdf_name, case_link):
    logging.info('Downloading S3 from Archive: ' + s3_pdf_name)
    #split_case_link = case_link.split('?')
    pdf_file_name = s3_pdf_name# +'.'+ split_case_link[1] + '.pdf'
    destination = 'results/' + pdf_file_name

    try:
        s3_resource.Bucket('bpwa.pdf-storage').download_file(pdf_file_name, destination)
    except Exception as e:
        logging.info('S3 Archive download failed: ' + s3_pdf_name)
        logging.error(e)
        return False

    return destination



def main():
    check_against_s3_objects()

# MAIN
if __name__ == '__main__':
    main()
