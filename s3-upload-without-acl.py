import boto3

# File to upload
LocalFileName = "image2.jpg"

BucketName = 's3acl-test01-lxy'
FileData = open(LocalFileName, 'rb')

client = boto3.client('s3')
response = client.put_object(
    Body = FileData,
    Bucket = BucketName,
    Key = LocalFileName,
    ContentType = 'image/jpeg',
    StorageClass = 'INTELLIGENT_TIERING'
)
