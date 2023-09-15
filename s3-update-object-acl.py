import boto3

FileName = "image1.jpg"
BucketName = 's3acl-test01-lxy'

client = boto3.client('s3')
response = client.put_object_acl(
    ACL = 'public-read',
    Bucket = BucketName,
    Key = FileName
)
