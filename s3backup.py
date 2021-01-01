import threading
import boto3
import os
import sys
import sys
import zipfile
from boto3.s3.transfer import TransferConfig

BUCKET_NAME = ""
ACCESS_KEY = ""
SECRET_KEY = ""


class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


def multi_part_upload_with_s3(file_path):
    # Multipart upload of a single file
    config = TransferConfig(multipart_threshold=1024 * 25, max_concurrency=10,
                            multipart_chunksize=1024 * 25, use_threads=True)
    client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )
    client.upload_file(file_path, BUCKET_NAME, file_path, Config=config, Callback=ProgressPercentage(file_path) )
    print()


def folder_upload(folder_path, prefix=None):
    # Walk a directory and upload files within it.
    client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

    for subdir, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(subdir, file)
            key = os.path.join(prefix, full_path).replace('\\', '/')
            print(key)
            client.upload_file(full_path, BUCKET_NAME, key)


def compress_and_upload(directory):
    print(directory)
    name = directory + '.zip'
    zipf = zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(directory):
        for file in files:
            zipf.write(os.path.join(root, file))
    zipf.close()
    multi_part_upload_with_s3(name)
    os.remove(name)


def compress_subdirs(directory):
    for path in os.listdir(directory):
        if len(path.split('.')) == 1:
            compress_and_upload(path)
        # Alternate way of checking if a directory.  Didn't detect everything for me.
        # if os.path.isdir(path):
        #     compress_and_upload(path)

if __name__ == '__main__':
    usage_message = "Usage: python3 multipart.py [-f for file | -d for directory | -s for separate sub-directories in a directory] path"
    if len(sys.argv) != 3:
        print(usage_message)
    else:
        path = sys.argv[2]
        if sys.argv[1] == '-f':
            multi_part_upload_with_s3(path)
        elif sys.argv[1] == '-d':
            compress_and_upload(path)
        elif sys.argv[1] == '-s':
            compress_subdirs(path)
        else:
            print(usage_message)
