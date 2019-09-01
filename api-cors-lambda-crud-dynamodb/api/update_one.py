import simplejson as json # simple json resolves the common error "Object of type Decimal is not JSON serializable"
import os
import boto3

TABLE_NAME = os.environ.get('TABLE_NAME', '')
PRIMARY_KEY = os.environ.get('PRIMARY_KEY', '')

def handler(event, context):

    try:
        body = event.get("body", None)
        if body is None:
            raise ValueError("invalid request, you are missing the parameter body")
        
        path_parameters = event.get("pathParameters", None)
        if path_parameters is None:
            raise ValueError("invalid request, you are missing the path parameter id")
        
        req_item_id = path_parameters.get("id", None)
        if req_item_id is None:
            raise ValueError("invalid request, you are missing the path parameter id")
        
        edited_item = json.loads(body)
        edited_item_props = list(edited_item.keys())
        if not edited_item_props:
            raise ValueError("invalid request, no arguments provided")
        
        first_prop = edited_item_props[0]
        params = {
            "Key": { PRIMARY_KEY: req_item_id },
            "UpdateExpression": f"SET {first_prop} = :{first_prop}",
            "ExpressionAttributeValues": {},
            "ReturnValues": "UPDATED_NEW"
        }
        params["ExpressionAttributeValues"][f":{first_prop}"] = edited_item[f"{first_prop}"]
        
        edited_item.pop(first_prop) # delete the first item, caz we've already taken care of it

        for (key, val) in edited_item.items():
            params["UpdateExpression"] += f", {key} = :{key}"
            params["ExpressionAttributeValues"][f":{key}"] = val
        
        ddb = boto3.resource('dynamodb')
        table = ddb.Table(TABLE_NAME)
        response = table.update_item(**params)

        status_code = 204
        resp = {}
    
    except ValueError as e:
        status_code = 400
        resp = {"description": f"Bad request. {str(e)}"}
    
    except Exception as e:
        status_code = 500
        resp = {"description": f"Internal server error. {str(e)}"}

    return { "statusCode": status_code, "body": json.dumps(resp) }

