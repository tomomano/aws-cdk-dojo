import os
from aws_cdk import core

from api_stack import ApigatewayCognitoStack

app = core.App()
ApigatewayCognitoStack(app, "apigateway-cognito")

app.synth()