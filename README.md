# S3Backup
A simple script for backing up local files to an S3 bucket.  This handles files of any size through multi-part uploads.

To use the script, set the S3 bucket name (not the ARN) and a Secret Key and Access Key for your account.

Usage:
```
python3 multipart.py [-f for file | -d for directory | -s for separate sub-directories in a directory] path
```

File mode: Uploads a specific file as is

Directory mode: Zips and uploads a directory

Sub-directory mode: Zips and uploads each sub-directory in a directory.  

In the sub-direcotry mode, if a directory contains two directories and a file, the two directories will each be zipped and uploaded and nothing is done with the file.  I found this useful when I had many mid-sized directories that I didn't want to be bundled into a massive zip file.



