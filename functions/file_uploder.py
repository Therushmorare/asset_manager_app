#!/usr/bin/python3

from flask import Flask, request, url_for, redirect, jsonify, session, flash, render_template
import boto3
import time
from config import Config
import logging
from concurrent.futures import ThreadPoolExecutor
from werkzeug.utils import secure_filename
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from psycopg2 import OperationalError
from functions.celery_worker import celery_ext

S3_BUCKET = Config.bucket_name
S3_REGION = Config.bucket_region
S3_ACCESS_KEY = Config.bucket_access_key
S3_SECRET_KEY = Config.bucket_secret_key
CLOUDFRONT_DOMAIN = Config.cloudfront
CLOUDFRONT_ID = Config.cloudfront_id

s3_client = boto3.client('s3', region_name=S3_REGION, aws_access_key_id=S3_ACCESS_KEY, aws_secret_access_key=S3_SECRET_KEY)
cloudfront_client = boto3.client("cloudfront",aws_access_key_id=S3_ACCESS_KEY,aws_secret_access_key=S3_SECRET_KEY)

"""
Uploading files to project cdn
"""
@celery_ext.celery.task
def file_upload(file_obj, user_id):
    file_to_upload = f"{user_id}_{secure_filename(file_obj.filename)}"  # Add user_id prefix

    try:
        s3_client.upload_fileobj(file_obj, S3_BUCKET, file_to_upload)
        file_url = f"https://{CLOUDFRONT_DOMAIN}/{file_to_upload}"
        return file_url

    except (NoCredentialsError, PartialCredentialsError):
        logging.error("AWS credentials are missing or incorrect!")
        return {"success": False, "error": "AWS credentials error!"}

    except OperationalError:
        logging.error("Database operational error occurred!")
        return {"success": False, "error": "Database connection failed!"}

    except Exception as e:
        logging.error(f"File upload failed: {str(e)}")
        return {"success": False, "error": f"Upload error: {str(e)}"}

#upload multiple files
@celery_ext.celery.task
def upload_multiple_files(files, user_id):
    results = []
    for file in files:
        try:
            url = file_upload(file, user_id)
            results.append(url)
        except Exception as e:
            print(f"Error uploading file: {e}")
            results.append(None)
    return results

"""
Update uploaded files
"""
def update_file(new_file, existing_file, user_id):
    try:
        file_to_upload = f"{user_id}_{secure_filename(new_file.filename)}"
        #Delete file
        s3_client.delete_object(Bucket=S3_BUCKET, Key=f"{user_id+existing_file}")
        cloudfront = boto3.client(
            "cloudfront",
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY
        )
        cloudfront.create_invalidation(
            DistributionId=CLOUDFRONT_ID,
            InvalidationBatch={
                "Paths": {
                    "Quantity": 1,
                    "Items": [file_to_upload]
                },
                "CallerReference": str(time.time()).replace(".", "")  # Unique reference
            }
        )

        #upload the new file
        s3_client.upload_fileobj(new_file, S3_BUCKET, file_to_upload)
        new_file_url = f"https://{CLOUDFRONT_DOMAIN}/{user_id + file_to_upload}"
        return new_file_url

    except (NoCredentialsError, PartialCredentialsError):
        logging.error("AWS credentials are missing or incorrect!")
        return {"success": False, "error": "AWS credentials error!"}

    except OperationalError:
        logging.error("Database operational error occurred!")
        return {"success": False, "error": "Database connection failed!"}

    except Exception as e:
        logging.error(f"File upload failed: {str(e)}")
        return {"success": False, "error": f"Upload error: {str(e)}"}
