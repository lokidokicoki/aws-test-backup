## Proposed enhancment

The current solution uses a simple loop to upload the files found in the `base-dir`.

The `s3.upload_file` function will block until it has completed, meaning that each file found has to uploaded sequentially.

This could be improved by using ThreadPool from the `multiprocessing` module and create a pool of 10 threads. This would allow upto 10 files to be uploaded simultanesously.

As the boto3 low-level clients are thread-safe, the code could re-use the established client to upload each file.

The file could then be refactored thus:

```python
import argparse
import time
import logging
from os import path, scandir, walk, remove
from botocore.exceptions import ClientError

from multiprocessing.pool import Threadpool

bucketName = None
s3Client = None
NUM_PROCESSES=10


try:
    import boto3
except ImportError:
    print("Missing required boto3 lib")
    raise

def uploadFile(fileDetails):
    try:
        s3Client.upload_file(fileDetails[0], bucketName, fileDetails[1])

        # once the file is uploaded, remove it from local
        remove(fileName)

    except ClientError as e:
        logging.error(e)
        return False
    return True

def main():

    #====
    # argument handling, checking removed for brevity
    #====

    bucketName = args.s3bucket
    s3Client = boto3.client("s3")

    # hold tuples of filename and objectName
    fileList = []

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
            fileList.append(fileName, objectName)

    
    pool = ThreadPool(processes=NUM_PROCESSES)
    pool.map(processFile, fileList)
```
