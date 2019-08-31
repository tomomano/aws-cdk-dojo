from aws_cdk import core

from api_stack import ApiLambdaCrudDynamoDBStack

app = core.App()
ApiLambdaCrudDynamoDBStack(app, "ApiLambdaCrudDynamoDBExample", env={'region': 'us-east-1'})

app.synth()