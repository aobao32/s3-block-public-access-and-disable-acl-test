# S3将阻止Public公开访问和禁用文件ACL两项功能作为默认设置的安全改进

摘要：本文介绍了2023年以来S3将阻止Public公开访问和禁用文件ACL两项功能作为新创建存储桶时候的默认设置这一变化由此带来的安全方面的改进。同时，介绍了在此场景下如何配置存储桶公开对外发布数据。

## 一、背景

在S3控制台上，可以看到如下信息：

    The S3 Block Public Access and S3 Object Ownership features provide settings to manage public access and object ownership for your Amazon S3 resources. All Block Public Access settings are enabled by default, and all new buckets, access points, and objects do not allow public access. By default, Object Ownership is set to bucket owner enforced, which disables the use of access control lists (ACLs).
    
    These default settings have been in place in the S3 console since 2018 and 2021, respectively, and are recommended security best practices. Since April 2023, these default settings apply to all new buckets, regardless of how they are created. If you require public access, you can edit the Block Public Access settings, and grant access by using bucket policies. Unless you need to control access for each object individually, using ACLs to grant access isn't recommended. For more information, see Access control best practices.

以上两项功能，分别推出与2018年和2021年，之前是可选配置，目前成为了新建存储桶Bucket时候的默认配置。本文对这两个功能的使用进行介绍。

## 二、以往存储桶公开访问的使用场景

使用S3文件的一个主要场景是对外提供托管的文件访问，包括S3图片、PDF、日志、其他压缩包下载对等访问场景。这时候主要用户场景是从互联网上发起匿名请求S3 URL，无须身份验证即可访问文件。

在阻止Public公开访问和禁用文件ACL两项功能成为默认值之前，将文件设置为Public的配置方式是：

1. 将存储桶的`Block All Public Access`选项关闭掉；
2. 清空本存储桶的Policy策略；
3. 为单个文件赋予ACL，显式的允许所有人（含匿名用户）具有Read-only权限。

第三步时候，由于要显式声明，所以需要在代码中包含对应的ACL，例如Python使用Boto3 SDK上传文件到S3时候，声明单个文件ACL是Public的样例代码如下：

```python
import boto3

# File to upload
LocalFileName = "image1.jpg"

BucketName = 's3acl-test01-lxy'
FileData = open(LocalFileName, 'rb')

client = boto3.client('s3')
response = client.put_object(
    ACL = 'public-read',
    Body = FileData,
    Bucket = BucketName,
    Key = LocalFileName,
    ContentType = 'image/jpeg',
    StorageClass = 'INTELLIGENT_TIERING'
)
```

这里可以看到，上传的单个文件具有自己单独的ACL。如果没有显式声明，即上传代码中不声明ACL，这时候本文件会自动保存为Private私有状态。这里就产生了一个问题，如果文件写入的时候，有的文件加了ACL，有的文件没有加ACL，那么他们的公开状态会不一致。这里会产生安全管理上的隐患。

## 三、FAQ常见问题 - 如何通过本次默认设置的变化让存储桶更安全

为何自2023年起，S3将阻止Public公开访问和禁用文件ACL两项功能作为默认设置？

### 1、日益增长的数据湖场景

S3作为数据湖的核心，可通过多种服务进行联动的分析，包括Kinesis Data Firehose流式传输的文件落盘、Kafka S3 Connector的文件落盘、Athena查询、Glue ETL转换、加载到Redshift数据仓库、机器学习的训练素材等、SageMaker训练好的模型文件等。除了以上用户生成的数据外，还有大量AWS服务生成的日志，包括ELB、WAF等也直接保存在S3。

在以上场景下，生成的日志都是企业核心数据，需要严格的数据保护，没有使用Public对外发布场景。由此，新创建的S3存储桶的默认选项`Block All Public Access`就是开启状态，意味着更安全。

### 2、安全基线的提升要求

在允许单个文件有独立的ACL的场景下，一个存储桶内许多文件的ACL各不一样，有的文件是Public匿名可读的，有的是Public可写，有的是private的。这些文件的状态和他们上传的代码息息相关。同时，存储桶级别无法统一对桶内所有文件实施统一的权限管理。由此，一些历史遗留代码可能造成潜在的安全风险。另外，如果是存在跨AWS账户的文件写入操作，每个写入的文件的owner所有人是属于写入者的，并不属于当前AWS账户。这样也更难于管理。

在以上场景下，将整个存储桶内的所有文件置于同一的Bucket policy权限管理是更安全的，同时废除（禁用）单个文件拥有自己的ACL，可实施“一刀切”的安全整改效果，确保所有文件的Owner明确、安全策略明确，显著的提升了安全。

“禁用ACL”这种说法是使用效果的简称，而在AWS S3 API上，这个特性被称为ObjectOwnership，当参数设置为BucketOwnerEnforced的时候，文件ACL就会被禁用。如果设置为其他参数，那么文件ACL继续可用。

### 3、本次默认设置的变更对之前已经存在的存储桶和规则有什么影响

无影响。表现在：

- （1）之前已经创建好并且在使用中的存储桶、以及单个文件赋予的ACL都不会被影响到；
- （2）新创建的存储桶，在创建向导页面，默认设置会开启`Block All Public Access`和禁用文件ACL；
- （3）除非用户手工编辑已经存在的存储桶，将本存储原来没有打开的`Block All Public Access`和禁用文件ACL两个开关的状态修改，才会对已经存在的存储桶产生影响。不修改现有存储桶的话，没有影响。

### 4、现有的存储桶如果也想提升安全是否可以变更设置

答：可以。

如果使用AWS网页控制台的话，进入存储桶的Permission设置标签页，可以调整`Block All Public Access`选项，也可以调整禁用文件ACL选项。

此外，这两个选项也可以通过API调用。参考[Block All Public Access](https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/userguide/configuring-block-public-access-bucket.html)和[禁用文件ACL](https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/userguide/object-ownership-existing-bucket.html)有AWSCLI和SDK的代码（Java语言）样例。

### 5、新创建的存储桶时候可以继续按照以前的规则来管理

答：可以按以前的方式使用。

新的规则在新创建存储桶的向导页面中成为了默认选项，但是创建时候可以人为的修改这两个选项，可以关闭`Block All Public Access`选项，也可以打开文件ACL允许单个文件拥有自己的ACL。但是不再推荐这样使用。

如果需要发布文件，可参考如下章节对不同场景的说明。

### 6、WEB类型应用对外发布数据的安全最佳实践

如果是典型的WEB应用，需要对外发布文件，也应该将S3存储桶设置为`Block All Public Access`的状态，然后通过CloudFront CDN服务对外发布文件。CloudFront通过OAC功能可以访问处于私有状态的存储桶。由此实现了S3无须Public即可对外发布。 

CloudFront OAC功能的配置请参考[这篇](https://blog.bitipcman.com/cloudfront-s3-origin-upgrade-from-oai-to-oac/)博客。

### 7、分析类数据对外发布的安全最佳实践

如果是数据分析场景，需要将S3存储桶数据共享给其他AWS用户，那么可以通过S3存储桶Policy显式的为其他AWS账户授权。请参考这篇[博客](https://blog.bitipcman.com/copy-s3-data-across-aws-count/)进行跨账户S3存储桶数据分享。此时，互联网上匿名请求没有权限访问S3存储桶的文件。

## 四、禁用单个文件ACL之后如何将存储桶设置为公开

### 1、禁用账号级别的`Block All Public Access`开关

在创建存储桶时候，需要关闭掉全局`Block All Public Access`的开关。进入S3服务，从左侧找到`Block Public Access settings for this account`，确认其中的选项都是关闭（OFF）状态。如下截图。

![](https://blogimg.bitipcman.com/workshop/s3-acl/s3-01.png)

### 2、创建存储桶

接下来分别从API上和网页界面控制台来完成。两种方式二选一即可。

#### （1）通过网页控制台图形界面创建

进入S3存储桶界面，点击创建按钮。在名称部分输入`s3acl-test01-lxy`，选择正确的Region。如下截图。

![](https://blogimg.bitipcman.com/workshop/s3-acl/s3-02.png)

在`Object Ownership`位置，选择`ACLs diabled(recommended)`，也就是禁用ACL。如下截图。

![](https://blogimg.bitipcman.com/workshop/s3-acl/s3-03.png)

在设置`Block Public Access settings for this bucket`位置，取消选中，不要打开这个功能。下边的四个单独选项也不要打开。最后选中下方的我确认这个设置的风险。如下截图。

![](https://blogimg.bitipcman.com/workshop/s3-acl/s3-04-2.png)

在创建向导其他选项位置保持默认值，最后点击页面右下角的创建按钮，完成存储桶创建。

当存储桶刚创建完毕后、且存储桶Policy为空还没有来得及设置的时候，在S3存储桶列表界面，本存储桶的公开状态将显示为`Objects can be public`，表示存储桶内的文件有可能是公开的状态（依据后续设置）。但实际上截止此时，存储桶内的文件是不能公开访问的。如下截图。

#### （2）通过API创建

如果不希望通过界面操作，而是通过API发起创建存储桶操作，则可使用各语言的SDK发起。在使用API创建存储桶时候有个问题，创建的存储桶默认都是开启`Block All Public Access`的。因此在创建存储桶之后，还需要一个额外的操作，去关闭`Block All Public Access`功能。这需要在API上分别发出两个请求。

以Python代码通过Boto3 SDK为例，创建存储桶并关闭`Block All Public Access`功能如下。

```python
import boto3

BucketName = 's3acl-test01-lxy'

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
```

### 3、设置存储桶级别的策略

#### （1）准备策略

现在开始配置存储桶策略。准备好如下一段存储桶Policy。请替换其中的存储桶名称为实际的名字。注意后边的`/*`必须保留，这里表示存储桶内的文件将获得授权。如果没有这个`/*`，那么授权只是给到存储桶，并不能完成对所有文件的授权。

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Allow-public-read",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::s3acl-test01-lxy/*"
        }
    ]
}
```

接下来分别从API上和网页界面控制台来完成。两种方式二选一即可。

#### （2）通过网页控制台图形界面创建

将这段Policy配置到一个已经存在的存储桶。点击存储桶，选择第三个标签页`Permissions`权限。如下截图。

![](https://blogimg.bitipcman.com/workshop/s3-acl/s3-06.png)

向下滚动页面，在`Bucket policy`存储桶策略位置，点击`Edit`编辑按钮。如下截图。

![](https://blogimg.bitipcman.com/workshop/s3-acl/s3-07.png)

粘贴这段策略，注意替换存储桶名字，并且保留`/*`的根目录和通配符。如下截图。

![](https://blogimg.bitipcman.com/workshop/s3-acl/s3-08.png)

将页面滚动到最下方，点击保存修改按钮。如下截图。

![](https://blogimg.bitipcman.com/workshop/s3-acl/s3-09.png)

再次返回到存储桶列表界面，对浏览器执行页面刷新。刷新后可以看到存储桶清单中的访问权限一列，已经显示为`Public`公开状态了。

![](https://blogimg.bitipcman.com/workshop/s3-acl/s3-10.png)

由此存储桶内所有文件已经可以公开访问了。

#### （3）通过API添加存储桶Policy

执行如下代码，请注意替换Policy中的存储桶名称为实际名称。

```python
import boto3

BucketName = 's3acl-test01-lxy'

client = boto3.client('s3')

response = client.put_bucket_policy(
    Bucket = BucketName ,
    Policy = '{ "Version": "2012-10-17", "Statement": [ { "Sid": "Allow-public-read", "Effect": "Allow", "Principal": "*", "Action": "s3:GetObject", "Resource": "arn:aws:s3:::s3acl-test01-lxy/*" } ] }'
)
```

### 4、上传单个文件的样例代码

上传单个文件，注意不要夹带任何ACL。

```python
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
```

从浏览器或者CURL使用匿名请求，验证文件可以访问。

至此，配置一个可公开访问的存储桶，配置成功。

### 5、验证单个文件ACL是禁用状态（可选测试）

上传单个文件，包含带有Public的ACL请求，测试是否被禁用。

```python
import boto3

# File to upload
LocalFileName = "image3.jpg"

BucketName = 's3acl-test01-lxy'
FileData = open(LocalFileName, 'rb')

client = boto3.client('s3')
response = client.put_object(
    ACL = 'public-read',
    Body = FileData,
    Bucket = BucketName,
    Key = LocalFileName,
    ContentType = 'image/jpeg',
    StorageClass = 'INTELLIGENT_TIERING'
)
```

以上代码包含了ACL，执行这段代码，返回如下：

```
botocore.exceptions.ClientError: An error occurred (AccessControlListNotSupported) when calling the PutObject operation: The bucket does not allow ACL
```

这表示显式声明带有ACL的上传将被拒绝。

试图修改现存文件ACL，测试ACL是否被禁用。

```python
import boto3

FileName = "image1.jpg"
BucketName = 's3acl-test01-lxy'

client = boto3.client('s3')
response = client.put_object_acl(
    ACL = 'public-read',
    Bucket = BucketName,
    Key = FileName
)
```

返回信息：

```
botocore.exceptions.ClientError: An error occurred (AccessControlListNotSupported) when calling the PutObjectAcl operation: The bucket does not allow ACLs
```

由此看到，禁用文件ACL选项生效。上传时候指定文件ACL，也禁止了修改现存文件添加ACL。这里与预期的行为一致。

## 五、小结

综上所述，在默认开启`Block All Public Access`并且默认禁用单个文件ACL之后，几个典型场景如下：

如果是数据分析等私有数据使用场景，即使代码试图将某个文件Public ACL，这个请求也会被拒绝。这时候存储桶的Policy是存储桶统一的安全规则管理入口，在存储桶Policy中可显式的授权其他AWS账户的访问。由此实现了存储桶安全的提升。

如果S3对外直接发布文件但是不通过CloudFront CDN，那么直接在S3存储桶级别配置Policy，即可让存储桶内所有文件都对外公开可读。此时上传单个文件不需要带有ACL参数。

如果是WEB应用对外发布文件，请使用默认的`Block All Public Access`和默认的禁用单个文件ACL，即然存储桶保持私有状态。然后通过CloudFront CDN服务配置OAC授权，将私有的S3存储桶的文件通过CDN方式对外发布。

## 六、参考文档

### 1、最佳实践

S3最佳安全实践

[https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/userguide/security-best-practices.html#security-best-practices-prevent]()

### 2、功能讲解

阻止对您的 Amazon S3 存储的公有访问

[https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/userguide/access-control-block-public-access.html]()

为您的桶控制对象所有权和禁用ACL

[https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/userguide/about-object-ownership.html#object-ownership-changes]()

### 3、S3存储桶策略样例

桶策略示例

[https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/userguide/example-bucket-policies.html]()

### 4、S3存储桶级别的API操作代码样例

通过AWSCLI或者SDK为S3桶配置阻止公有访问设置的例子

[https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/userguide/configuring-block-public-access-bucket.html]()

通过AWSCLI或者SDK为现有桶设置对象所有权的例子

[https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/userguide/object-ownership-existing-bucket.html]()

Java等语言使用SDK将S3存储桶策略添加到存储桶的代码样例

[https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/userguide/example_s3_PutBucketPolicy_section.html]()

Python Boto3 SDK创建存储桶代码样例

[https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html]()

Python Boto3 SDK关闭存储桶Block Public Access开关代码样例

[https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/delete_public_access_block.html]()