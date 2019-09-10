## Now, let's start coding!

### Initialize a project
Create a new directory where you will build your project:
```bash
$ mkdir s3_lambda_ecs
```

`cd` into it and initialize a CDK project:
```bash
$ cd s3_lambda_ecs
$ cdk init app --language=python
```
This command will create a directory named `s3_lambda_ecs`. Delete it, since we do not need it for now.

Then install dependencies by pip:
```bash
source .env/bin/activate
pip install -r requirements.txt
```

### Install additional aws-cdk modules
```bash
pip install aws-cdk.aws-lambda aws-cdk.aws-dynamodb aws-cdk.aws-s3 aws_cdk.aws_ecs aws_cdk.aws_ec2
```

### Create app.py

Copy and paste the following code in `app.py`.
```python
import os
from aws_cdk import core

from data_bucket import DataBucket

class MyStack(core.Stack):

    def __init__(self, parent: core.App, name: str, **kwargs):
        super().__init__(parent, name, **kwargs)

        bucket = DataBucket(self, 'DataBucket')

app = core.App()
MyStack(
    app, "s3-lambda-ecs",
    env={
        "region": "us-east-1",
        "account": os.environ["CDK_DEFAULT_ACCOUNT"], 
    }
)
app.synth()
```

Below, we will create each construct.


### Create a S3 construct
Create a file named `data_bucket.py`. Copy and paste the following code.
```python
from aws_cdk import (
    core,
    aws_s3 as s3,
)

class DataBucket(core.Construct):
    """
    this construct defines a simple S3 bucket, to store movie data and their thumbnails.
    By connecting this bucket with lambda stack, lambda will invoke functions to handle uploaded data
    """

    @property
    def data_bucket(self):
        return self._data_bucket

    def __init__(self, parent: core.Construct, name: str) -> None:
        super().__init__(parent, name)

        bucket = s3.Bucket(
            self, "S3Bucket",
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # output generated bucket name
        core.CfnOutput(self, 'Bucket', value=bucket.bucket_name)

        self._data_bucket = bucket
```
