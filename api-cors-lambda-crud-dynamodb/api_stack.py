#!/usr/bin/env python3

from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
    aws_apigateway as apigw
)

class ApiLambdaCrudDynamoDBStack(core.Stack):

    def __init__(self, scope: core.Stack, id: str, **kwargs) -> None:
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

        get_one_lambda = _lambda.Function(
            self, 'getOneItemFunction',
            code=_lambda.AssetCode('api'),
            handler='get_one.handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            environment={
                "TABLE_NAME": dynamo_table.table_name,
                "PRIMARY_KEY": 'itemID'
            }
        )

        get_all_lambda = _lambda.Function(
            self, 'getAllItemsFunction',
            code=_lambda.AssetCode('api'),
            handler='get_all.handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            environment={
                "TABLE_NAME": dynamo_table.table_name,
                "PRIMARY_KEY": 'itemID'
            }
        )

        create_one = _lambda.Function(
            self, 'createItemFunction',
            code=_lambda.AssetCode('api'),
            handler='create.handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            environment={
                "TABLE_NAME": dynamo_table.table_name,
                "PRIMARY_KEY": 'itemID'
            }
        )

        update_one = _lambda.Function(
            self, "updateItemFunction",
            code=_lambda.AssetCode('api'),
            handler='update_one.handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            environment={
                "TABLE_NAME": dynamo_table.table_name,
                "PRIMARY_KEY": 'itemID'
            }
        )

        delete_one = _lambda.Function(
            self, 'deleteItemFunction',
            code=_lambda.AssetCode('api'),
            handler='delete_one.handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            environment={
                "TABLE_NAME": dynamo_table.table_name,
                "PRIMARY_KEY": 'itemID'
            }
        )

        # grant permission for this lambda function\
        dynamo_table.grant_read_write_data(get_one_lambda)
        dynamo_table.grant_read_write_data(get_all_lambda)
        dynamo_table.grant_read_write_data(create_one)
        dynamo_table.grant_read_write_data(update_one)
        dynamo_table.grant_read_write_data(delete_one)

        # create apigateway
        api = apigw.RestApi(
            self, 'itemsApi',
            rest_api_name="Items Service" # A name for the API Gateway RestApi resource
        )

        # create a resource
        items = api.root.add_resource('items')

        get_all_integration = apigw.LambdaIntegration(get_all_lambda)
        items.add_method('GET', get_all_integration)

        create_one_integration = apigw.LambdaIntegration(create_one)
        items.add_method('POST', create_one_integration)

        # create another resource
        single_item = items.add_resource('{id}')

        get_one_integration = apigw.LambdaIntegration(get_one_lambda)
        single_item.add_method('GET', get_one_integration)

        update_one_integration = apigw.LambdaIntegration(update_one)
        single_item.add_method("PATCH", update_one_integration)

        delete_one_integration = apigw.LambdaIntegration(delete_one)
        single_item.add_method('DELETE', delete_one_integration)