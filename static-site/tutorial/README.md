# Tutorial

Original TypeScript code: https://github.com/aws-samples/aws-cdk-examples/tree/master/typescript/static-site

This is essentially a Python implementation of the above code, with some minor modifications. Below, I will explain, step-by-step, how to build this AWS app.

## Project structure
  * `app.py`: This will be the main entry point of the app.
  * `static_site_stack.py`: This is the main stack of the app.
  * `site_content`: A simple HTML files are stored here. You can upload them to your S3 bucket, to test your site.
  * `tutorial/`: The tutorial is here.

## Preparations

### 1. Obtain your own domain and get SSL/TLS certificate for it
* Obtain your own domain through [Route 53](https://aws.amazon.com/jp/route53/) console.
* Obtain SSL/TLS certificate for your domain through [Amazon Certificate Manager (ACM)](https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html)

**ACM must be obtained in us-east-1 region, because of the CloudFront's requirement** For more details, see [here](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-requirements.html).

By going to the ACM console, **find the ARN of the certificate you generated**. We will use that later.

### 2. Set account credentials by environmental variable
Set the account which you use to deploy the service:
```bash
$ export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
$ export AWS_SECRET_ACCESS_KEY=ABCDEFGHIJK
```

### 3. Set domain info by environmental variable
```bash
$ export MY_DOMAIN=<mydomain.com>
$ export MY_SUBDOMAIN=www
$ export CERTIFICATE_ARN=<your own value!>
```
Replce the `<...>` values with your own settings.

## Now, let's start coding!

### Initialize a project

This is almost certainly a routine task you have done many times, so I won't explain much.
Create a new directory where you will build your project:
```bash
$ mkdir static-site
$ cd static-site
$ cdk init app --language python
```
This command will create a directory named `static-site`. Delete it, since we do not need it for now.

Then,
```bash
source .env/bin/activate
pip install -r requirements.txt
```

### Install additional aws-cdk modules
We will use the following modules to construct our stack.
```bash
pip install aws-cdk.aws-s3 aws-cdk.aws-cloudfront aws-cdk.aws-route53 aws-cdk.aws-certificatemanager aws-cdk.aws_route53_targets
```

### Create app.py
Copy and paste the following code in `app.py`.
```python
import os
from aws_cdk import core
from static_site import StaticSite
from static_site import StaticSiteProps

class MyStaticSiteStack(core.Stack):

    def __init__(self, parent: core.App, name: str, **kwargs):
        super().__init__(parent, name, **kwargs)

        StaticSite(
            self, 'StaticSite',
            props=StaticSiteProps(
                domain_name=self.node.try_get_context('domain'),
                site_sub_domain=self.node.try_get_context('subdomain'),
                certificate_arn=self.node.try_get_context('certificate_arn')
            )
        )

app = core.App()
MyStaticSiteStack(
    app, "static-site", 
    env={
        "region": "us-east-1",
        "account": os.environ["CDK_DEFAULT_ACCOUNT"], 
    }
)

app.synth()
```

Some comments:
  * By `props=StaticSiteProps(...)` we're getting context information, specified by `-c` option of `cdk` command
  * `env={"region": "us-east-1", "account": os.environ["CDK_DEFAULT_ACCOUNT"]}` is necessary in order for `aws_route53` module to work properly.

`app.py` will be the entry point of our CDK app. As you can see, we are adding `MyStaticSiteStack` to our app. `MyStaticSiteStack` contains one constructor, named `StaticSite`. Below, we will create `StaticSite` constructor!

### Create static_site.py
Create a new python file named `static_site.py` and open it with your editor.

First, import cdk libraries that will be used in this stack:
```python
from aws_cdk import (
    core,
    aws_cloudfront as cfront,
    aws_route53 as route53,
    aws_route53_targets,
    aws_s3 as s3,
    aws_certificatemanager as acm
)
```

Let's define a utility class to store domain information. (Note: this was inspired by the original TypeScript code. This may not be the most Pythonic way to write this?)

```python
from dataclasses import dataclass

@dataclass
class StaticSiteProps:
    domain_name: str
    site_sub_domain: str
```

Then, create a new class, `StaticSite`, by extending `core.Construct`:

```python
class StaticSite(core.Construct):
    def __init__(self, parent: core.Construct, name: str, props: StaticSiteProps) -> None:
        super().__init__(parent, name)

        site_domain = props.site_sub_domain + '.' + props.domain_name
```

### Create a S3 bucket
Now, create a new bucket to serve a website content.

API ref: https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_s3/Bucket.html

```python
# Content bucket
site_bucket = s3.Bucket(
   self, "SiteBucket",
   bucket_name=site_domain,
   website_index_document="index.html",
   website_error_document="error.html",
   public_read_access=True,
   removal_policy=core.RemovalPolicy.DESTROY
)

core.CfnOutput(self, 'Bucket', value=site_bucket.bucket_name)
```

`core.CfnOutput()` is added so that the deployed bucket name are displayed when you run `cdk deploy`.

Now, deploy the system we have built so far. Run
```bash
$ cdk synth -c domain=$MY_DOMAIN -c subdomain=$MY_SUBDOMAIN -c certificate_arn=$CERTIFICATE_ARN
```
If the generated stack looks good, deploy it by
```bash
$ cdk deploy -c domain=$MY_DOMAIN -c subdomain=$MY_SUBDOMAIN -c certificate_arn=$CERTIFICATE_ARN
```

Then, go to your AWS console and confirm that a new bucket with public read access is created.

You can now upload the web site content manually. A simple HTML is available at `site_content/` of this repository. Try upload them!

### Create a CloudFront distribution
Now, attach a CloudFront distribution to the S3 bucket we've created.

API ref: https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_cloudfront/CloudFrontWebDistribution.html

```python
#cloudfront distribution that provies HTTPS
distribution = cfront.CloudFrontWebDistribution(
   self, 'SiteDistribution',
   origin_configs=[
      cfront.SourceConfiguration(
      behaviors=[cfront.Behavior(is_default_behavior=True)],
      s3_origin_source=cfront.S3OriginConfig(s3_bucket_source=site_bucket)
      )
   ],
   alias_configuration=cfront.AliasConfiguration(
      acm_cert_ref=props.certificate_arn,
      names=[site_domain],
      ssl_method=cfront.SSLMethod.SNI,
      security_policy=cfront.SecurityPolicyProtocol.TLS_V1_1_2016
   )
)

core.CfnOutput(self, 'DistributionID', value=distribution.distribution_id)
```

* By using `origin_configs`, we are specifying that S3 bucket is the source of our distribution.
* By using alias_configuration, we are specifying that the distribution should use HTTPS protocols.

Now, try deploying the system. Because deployment of CloudFront takes some time, this deployment may take ~10 mins to complete.

At this stage, your CloudFront distribution is hosted at some random address, which should look like `XXXXXX.cloudfront.net`. You can see your address by going to the CloudFront console. Check that your distribution is accessible through your web browser.

### Add record to Route 53
Finally, we add A record to our Route53's hosted zone, so that our CloudFront distribution can be accessed by using our own domain.

```python
# Route 53 alias record for the CloudFront distribution
zone = route53.HostedZone.from_lookup(
   self, 'MyHostedZone',
   domain_name=props.domain_name
)

# Add a A record to the hosted zone
route53.ARecord(
   self, 'SiteAliasRecord',
   zone=zone,
   record_name=site_domain,
   target=route53.AddressRecordTarget.from_alias(
         aws_route53_targets.CloudFrontTarget(distribution)
   )
)
```

That's it! Deploy our final product, and confirm that our pretty website is accessible through your domain!