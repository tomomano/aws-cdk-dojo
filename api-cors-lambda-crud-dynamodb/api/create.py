import json, os
import uuid
import boto3

TABLE_NAME = os.environ.get('TABLE_NAME', '')
PRIMARY_KEY = os.environ.get('PRIMARY_KEY', '')

def handler(event, context):
    
    try:
        body = event["body"]
        if body is None:
            raise ValueError("invalid request, you are missing the parameter body")
        
        item = json.loads(body)
        item[PRIMARY_KEY] = uuid.uuid4().hex

        ddb = boto3.resource('dynamodb')
        table = ddb.Table(TABLE_NAME)
        response = table.put_item(Item=item)

        status_code = 200
        resp = response['Item']
    except Exception as e:
        status_code = 401
        resp = {"description": str(e)}
    
    return { "statusCode": status_code, "body": json.dumps(resp) }