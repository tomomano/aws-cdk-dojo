import json, os
import uuid
import boto3

TABLE_NAME = os.environ.get('TABLE_NAME', '')
PRIMARY_KEY = os.environ.get('PRIMARY_KEY', '')

ddb = boto3.resource('dynamodb')

def handler(event, context):

    if not "body" in event:
        return { "statusCode": 400, "body": "invalid request, you are missing the parameter body"}
    
    item = json.loads(event["body"])

    item[PRIMARY_KEY] = uuid.uuid4().hex

    try:
        table = ddb.Table(TABLE_NAME)
        response = table.put_item(item)
        return { 
            "statusCode":201,
            "body": json.dumps(response['Item'])
        }
    except Exception as e:
        return { "statusCode": 500, "body": json.dumps(e) }