import json
import logging
import os
import uuid
import boto3

# Instanciamos a la BBDD de dynamodb
dynamodb = boto3.resource('dynamodb')


def create(event, context):
    # Extraemos y verificamos los datos de entrada
    data = json.loads(event['body'])
    if 'chatid' not in data:
        logging.error("Validation Failed")
        raise Exception("Couldn't create the todo item.")
    
    # Instanciamos la tabla
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    
    # Generamos el token
    token = str(uuid.uuid1())
    # Creamos el objeto a almacenar en la BBDD
    item = {
        'id': token,
        'id_chat1': data['chatid'],
        'id_chat2': "",
    }

    # Escribimos el objeto en la BBDD
    table.put_item(Item=item)

    # Respondemos al cliente
    response = {
        "statusCode": 200,
        "body": token
    }

    return response
