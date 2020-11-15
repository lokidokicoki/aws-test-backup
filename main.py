#!/usr/bin/env python

import argparse

try:
    import boto3
except ImportError:
    print("Missing required boto3 lib")
    raise


def main():
    """
    Parse incoming arguments; require basedir and s3bucket
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


if __name__ == "__main__":
    main()