#!/usr/bin/env python

import argparse
import logging
from os import path, scandir, walk
from botocore.exceptions import ClientError

try:
    import boto3
except ImportError:
    print("Missing required boto3 lib")
    raise


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket, taken form https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client("s3")
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def main():
    """
    Parse incoming arguments; require basedir and s3bucket

    check connectivitiy to target S3 bucket; if unavailable, raise and exit
    get list of files to process from basedir; if empty, exit
    process each file:
        upload to s3
        object naming convention: base-dir/location/YYYY/MM/DD/HH/mm-topic.dat
        on success remove from basedir; else raise and exit
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--debug", help="enable debug output", action="store_true"
    )
    parser.add_argument("basedir", help="base directory path to upload from")
    parser.add_argument("s3bucket", help="target S3 bucket name")
    args = parser.parse_args()

    print(f"aws-backup from:{args.basedir} to:{args.s3bucket}")

    if not path.exists(args.basedir):
        raise RuntimeError(f"The basedir `{args.basedir}` does not exist!")

    # get s3 client
    s3 = boto3.resource("s3")
    found = False

    # raise an error is the passed bucket is not accessible
    for bucket in s3.buckets.all():
        if bucket.name == args.s3bucket:
            found = True

    if not found:
        raise RuntimeError(
            f"S3 bucket `{args.s3bucket}` either does not exist or is not accessible!"
        )

    # we have got this far, so the basedir and s3bucket are 'valid', now to get the file list
    # r=root, d=directories, f = files
    for r, d, f in walk(args.basedir):
        for file in f:
            print(path.join(r, file))


if __name__ == "__main__":
    main()