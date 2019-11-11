import os
from aws_cdk import core

from api_stack import ApigatewayCognitoStack

# obtain Cognito ARN from env variable
cognito_arn = os.environ["COGNITO_ARN"]

app = core.App()
ApigatewayCognitoStack(app, "apigateway-cognito", cognito_arn)

app.synth()