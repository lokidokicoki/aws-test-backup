# Scope

Simple script ot uplaod files from a given directory to an S3 bucket.

**Usage:**

`python main.py <basedir> <s3bucket>`

**Dependencies:**

`pip3 install boto3`


**crontab setup**

`crontab -e`

add this line, adjust for path and timing:

`* * * * * /usr/bin/python3 /path/to/aws-test-backup/main.py <base-dir> <target-s3-bucket>`