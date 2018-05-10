{% if cookiecutter.include_apigw == "y" %}import json
{% endif %}
import os

import boto3


def runs_on_aws_lambda():
    """
        Returns True if this function is executed on AWS Lambda service.
    """
    return 'AWS_SAM_LOCAL' not in os.environ and 'LAMBDA_TASK_ROOT' in os.environ


def handler(event, context):
    """
        AWS Lambda handler

        This method is invoked by the API Gateway: /Prod/first/{proxy+} endpoint.
    """
    session = boto3.Session()
    message = get_message(session)
{% if cookiecutter.include_apigw == "y" %}
    return {
        "statusCode": 200,
        "body": json.dumps(message)
    }
{% else %}
    return message
{% endif %}

def get_message(session):
    return {"hello": "world"}
