#!/usr/bin/env python3

from aws_cdk import core

from api_stack import ApiLambdaCrudDynamoDBStack

app = core.App()
ApiLambdaCrudDynamoDBStack(app, "my_api", env={'region': 'us-east-1'})

app.synth()