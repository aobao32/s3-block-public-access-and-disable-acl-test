import boto3

BucketName = 's3acl-test04-lxy'

client = boto3.client('s3')

### 创建存储桶
response1 = client.create_bucket(
    Bucket = BucketName ,
    CreateBucketConfiguration={
        'LocationConstraint': 'ap-northeast-1',
    },
    ObjectOwnership = 'BucketOwnerEnforced'
)

### 关闭Block All Public Access功能
response2 = client.delete_public_access_block(
    Bucket = BucketName
)
