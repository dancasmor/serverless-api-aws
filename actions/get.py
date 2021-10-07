import os
import json

from actions import decimalencoder
import boto3

# Instanciamos a la BBDD de dynamodb
dynamodb = boto3.resource('dynamodb')


def get(event, context):
    # Instanciamos la tabla
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # Buscamos la información relacionada con el token/id
    result = table.get_item(
        Key={
            'id': event['pathParameters']['id']
        }
    )

    # Devolvemos la información encontrada
    response = {
        "statusCode": 200,
        "body": json.dumps(result['Item'],
                           cls=decimalencoder.DecimalEncoder)
    }

    return response
