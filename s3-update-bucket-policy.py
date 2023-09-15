import boto3

BucketName = 's3acl-test03-lxy'

client = boto3.client('s3')

response = client.put_bucket_policy(
    Bucket = BucketName ,
    Policy = '{ "Version": "2012-10-17", "Statement": [ { "Sid": "Allow-public-read", "Effect": "Allow", "Principal": "*", "Action": "s3:GetObject", "Resource": "arn:aws:s3:::s3acl-test03-lxy/*" } ] }'
)
