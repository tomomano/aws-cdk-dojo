import simplejson as json
import os
import boto3

TABLE_NAME = os.environ.get('TABLE_NAME', '')
PRIMARY_KEY = os.environ.get('PRIMARY_KEY', '')


def handler(event, context):

    try:
        path_parameters = event.get("pathParameters", None)
        if path_parameters is None:
            raise ValueError("invalid request, you are missing the path parameter id")
        
        req_item_id = path_parameters.get("id", None)
        if req_item_id is None:
            raise ValueError("invalid request, you are missing the path parameter id")
        
        ddb = boto3.resource('dynamodb')
        table = ddb.Table(TABLE_NAME)
        response = table.delete_item(Key={ PRIMARY_KEY: req_item_id })

        status_code = 200
        resp = {"description": "Successfully deleted."}
    
    except ValueError as e:
        status_code = 400
        resp = {"description": f"Bad request. {str(e)}"}
    
    except Exception as e:
        status_code = 500
        resp = {"description": f"Internal server error. {str(e)}"}

    return { "statusCode": status_code, "body": json.dumps(resp) }

