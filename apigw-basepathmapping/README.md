# APIGateway with BasePathMapping option example

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
$ export DOMAIN_NAME=<mydomain.com>
$ export CERTIFICATE_ARN=<your own value!>
```
Replce the `<...>` values with your own settings.

## Build CloudFormation

```bash
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

Assuming that you have have finished the above preparation, you can build the CloudFormation template by:
```bash
cdk synth
```

## Deploy

```bash
cdk deploy DomainStack FirstAPI SecondAPI
```

## Clean up

```bash
cdk destroy
```

## Testing

* Go to your AWS console -> CloudFormation and verify that the stack is deployed successfully.
* Go to your AWS console -> API Gateway and check that two API Gateway resources (`api1` and `api2`) is deployed.
* Open your browser and type in `https://<DOMAIN_NAME>/api1`.
  * You will see a message that says `Hello, CDK! You have hit /api1`
* Likewise, try `https://<DOMAIN_NAME>/api2`
