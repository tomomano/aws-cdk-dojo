#!/usr/bin/env python3

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
