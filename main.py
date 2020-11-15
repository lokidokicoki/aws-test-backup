import argparse
import boto3

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="enable debug output", action="store_true")
    parser.add_argument("basedir", help="base directory path to upload from")
    parser.add_argument("s3bucket", help="target S3 bucket name")
    args = parser.parse_args() 

    print(f'aws-backup from:{args.basedir} to:{args.s3bucket}')

if __name__ == "__main__":
    main()