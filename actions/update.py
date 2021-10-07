import json
import logging
import os

from actions import decimalencoder
import boto3

# Instanciamos a la BBDD de dynamodb
dynamodb = boto3.resource('dynamodb')


def update(event, context):
    # Extraemos y verificamos los datos de entrada
    data = json.loads(event['body'])
    if 'chatid' not in data:
        logging.error("Validation Failed")
        raise Exception("Couldn't update the todo item.")
        return
    
    # Instanciamos la tabla
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # Actualizamos/creamos el emparejamiento
    result = table.update_item(
        Key={
            'id': event['pathParameters']['id']
        },
        ExpressionAttributeNames={
          '#id_chat2': 'id_chat2',
        },
        ExpressionAttributeValues={
          ':id_chat2': data['chatid'],
        },
        UpdateExpression='SET #id_chat2 = :id_chat2',
        ReturnValues='ALL_NEW',
    )

    # Devolver el emparejamiento creado
    response = {
        "statusCode": 200,
        "body": json.dumps(result['Attributes'],
                           cls=decimalencoder.DecimalEncoder)
    }

    return response
