#!/usr/bin/env python

import argparse
import time
import logging
from os import path, scandir, walk, remove
from botocore.exceptions import ClientError

try:
    import boto3
except ImportError:
    print("Missing required boto3 lib")
    raise


def uploadFile(fileName, bucket, objectName=None):
    """Upload a file to an S3 bucket, taken form https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if objectName is None:
        objectName = fileName

    # Upload the file
    s3Client = boto3.client("s3")
    try:
        s3Client.upload_file(fileName, bucket, objectName)

    except ClientError as e:
        logging.error(e)
        return False
    return True


def main():
    """
    Parse incoming arguments; require basedir and s3bucket

    S3object naming convention: base-dir/location/YYYY/MM/DD/HH/mm-topic.dat
    mapped to filename: base-dir/<sub-dri>/YYYY/MM/DD/HH/mm-<filename>.dat

    Process:
    check connectivitiy to target S3 bucket; if unavailable, raise and exit
    get list of files to process from basedir; if empty, exit
    process each file:
        upload to s3
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
            # construct object name from file
            fileName = path.join(r, file)

            modTime = time.strftime(
                "%Y/%m/%d/%H/%M", time.localtime(path.getmtime(fileName))
            )

            dirName = path.dirname(fileName)
            baseName = path.basename(fileName)
            if not baseName.endswith(".dat"):
                baseName = f"{baseName}.dat"

            objectName = f"{dirName}/{modTime}-{baseName}"

            if uploadFile(fileName, args.s3bucket, objectName):
                # remove file
                try:
                    remove(fileName)
                except OSError as e:
                    ## if failed, report it back to the user ##
                    print("Error: %s - %s." % (e.filename, e.strerror))
            else:
                print(f"Failed to upload: {fileName}")


if __name__ == "__main__":
    main()