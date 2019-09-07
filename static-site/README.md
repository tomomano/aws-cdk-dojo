
# Static site
Original TypeScript code: https://github.com/aws-samples/aws-cdk-examples/tree/master/typescript/static-site

This is essentially a Python implementation of the above code, with some minor modifications.

## Preparations before deployment

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

## Deploy

## Build
Install Python dependencies:
```bash
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

Assuming that you have have finished the above preparation, you can build the CloudFormation template by:

```bash
$ cdk synth -c domain=$MY_DOMAIN -c subdomain=$MY_SUBDOMAIN -c certificate_arn=$CERTIFICATE_ARN
```

You can deploy the system by:

```bash
$ cdk deploy -c domain=$MY_DOMAIN -c subdomain=$MY_SUBDOMAIN -c certificate_arn=$CERTIFICATE_ARN
```

When you are done with the app, do not forget to destroy it:
```bash
cdk destroy
```

## Test
You can upload the web site content to the S3 bucket generated by the deployment. Then go to the domain that you registered, and your pretty website should be there!

## Project structure
  * `app.py`: This will be the main entry point of the app.
  * `static_site_stack.py`: This is the main stack of the app.
  * `site_content`: A simple HTML files are stored here. You can upload them to your S3 bucket, to test your site.
  * `tutorial/`: The tutorial is here.