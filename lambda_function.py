import json
import os
import uuid
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("TABLE_NAME", "Tasks"))

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method")

    try:
        if method == "POST":
            body = json.loads(event.get("body") or "{}")
            title = body.get("title")

            if not isinstance(title, str) or not title.strip():
                return response(400, {"error": "Title is required"})

            task = {
                "taskId": str(uuid.uuid4()),
                "title": title.strip(),
                "completed": False,
                "createdAt": datetime.now(timezone.utc).isoformat()
            }

            table.put_item(Item=task)
            return response(201, task)

        elif method == "GET":
            result = table.scan(Limit=100)
            return response(200, result.get("Items", []))

        return response(405, {"error": "Method not allowed"})

    except (ValueError, TypeError):
        return response(400, {"error": "Invalid request"})
    except Exception:
        print("Request processing failed")
        return response(500, {"error": "Internal server error"})

def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
