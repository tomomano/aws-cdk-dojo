import simplejson as json
import os
import boto3

TABLE_NAME = os.environ.get('TABLE_NAME', '')
PRIMARY_KEY = os.environ.get('PRIMARY_KEY', '')

def handler(event, context):

    try:
        ddb = boto3.resource('dynamodb')
        table = ddb.Table(TABLE_NAME)
        response = table.scan()

        status_code = 200
        resp = response['Items']
    
    except Exception as e:
        status_code = 500
        resp = {"description": f"Internal server error. {str(e)}"}

    return { "statusCode": status_code, "body": json.dumps(resp) }
