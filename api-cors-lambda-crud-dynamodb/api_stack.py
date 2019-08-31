#!/usr/bin/env python3

from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
    aws_apigateway as apigw
)

class ApiLambdaCrudDynamoDBStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create a dynamo db table
        dynamo_table = ddb.Table(
            self, 'items',
            partition_key={
                'name': 'itemID',
                'type': ddb.AttributeType.STRING
            },
            table_name='items',
            removal_policy=core.RemovalPolicy.DESTROY # NOT recommended for production code
        )

        # this lambda function implements
        # get_one_lambda = _lambda.Function(
        #     self, 'getOneItemFunction',
        #     code=_lambda.AssetCode('api'),
        #     handler='get_one.handler',
        #     runtime=_lambda.Runtime.PYTHON_3_7,
        #     environment={
        #         "TABLE_NAME": dynamo_table.table_name,
        #         "PRIMARY_KEY": 'itemID'
        #     }
        # )

        create_one = _lambda.Function(
            self, 'createItemFunction',
            code=_lambda.AssetCode('api'),
            handler='create.handler',
            environment={
                "TABLE_NAME": dynamo_table.table_name,
                "PRIMARY_KEY": 'itemID'
            }
        )

        # grant permission for this lambda function
        dynamo_table.grant_read_write_data(create_one)

        # create apigateway
        api = apigw.RestApi(
            self, 'itemsApi',
            rest_api_name="Items Service" # A name for the API Gateway RestApi resource
        )

        # create a resource
        items = api.root.add_resource('items')

        create_one_integration = apigw.LambdaIntegration(create_one)
        items.add_method('POST', create_one_integration)
