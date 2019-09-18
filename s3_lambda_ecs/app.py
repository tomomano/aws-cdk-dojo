#!/usr/bin/env python3

import os
from aws_cdk import core

from my_stack import MyStack

app = core.App()
MyStack(
    app, "s3-lambda-ecs",
    env={
        "region": "us-east-1",
        "account": os.environ["CDK_DEFAULT_ACCOUNT"], 
    }
)

app.synth()
