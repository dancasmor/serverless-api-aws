import os

import boto3

# Instanciamos a la BBDD de dynamodb
dynamodb = boto3.resource('dynamodb')


def delete(event, context):
    # Instanciamos la tabla
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # Eliminamos el emparejamiento
    table.delete_item(
        Key={
            'id': event['pathParameters']['id']
        }
    )

    # Respondemos con un código positivo
    response = {
        "statusCode": 200
    }

    return response
