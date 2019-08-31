import json, os
import boto3

TABLE_NAME = os.environ.get('TABLE_NAME', '')
PRIMARY_KEY = os.environ.get('PRIMARY_KEY', '')

ddb = boto3.resource('dynamodb')

def handler(event, context):

    if "id" in event.pathParameters:
        requested_item_id = event.pathParameters["id"]
    else:
        return { "statusCode":400, "body": 'Error: You are missing the path parameter id' }

    try:
        table = ddb.Table(TABLE_NAME)
        response = table.get_item(Key={ PRIMARY_KEY: requested_item_id })
        return { 
            "statusCode":200,
            "body": json.dumps(response['Item'])
        }
    except Exception as e:
        return { "statusCode": 500, "body": json.dumps(e) }

