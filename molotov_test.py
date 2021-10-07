import os
import json
import random
import molotov
from molotov import global_setup, scenario

@global_setup()
def init_test(args):
	# Establecemos la URL base de la API
	BASE_URL=os.getenv('BASE_URL', 'YOUT_BASE_URL')
	molotov.set_var('base_url', BASE_URL)


@scenario(weight=50)
async def _test_create__get_update_join(session):
	# Tomamos la URL base
	base_url= molotov.get_var('base_url')
	# Realizamos la petición al endpoint de crear
	token = 0
	data = json.dumps({"chatid": random.randint(100000,999999)})
	async with session.post(base_url + '/create', data=data) as resp:
		# Extraemos la el cuerpo de la respuesta mediante bytes (problemas con json)
		content_byte = await resp.read()
		# Convertimos a cadena
		token = content_byte.decode("utf-8")
		assert resp.status == 200, resp.status
	# Continuamos con la petición de consulta de información relacionada con el token
	async with session.get(base_url + '/get/' + str(token)) as resp:
		assert resp.status == 200, resp.status
	# Solo nos queda hacer el update
	data = json.dumps({"chatid": random.randint(100000,999999)})
	async with session.put(base_url + '/update/' + token, data=data) as resp:
		assert resp.status == 200, resp.status



@scenario(weight=50)
async def _test_create_get_delete_join(session):
	# Tomamos la URL base
	base_url= molotov.get_var('base_url')
	# Realizamos la petición al endpoint de crear
	token = 0
	data = json.dumps({"chatid": random.randint(100000,999999)})
	async with session.post(base_url + '/create', data=data) as resp:
		# Extraemos la el cuerpo de la respuesta mediante bytes (problemas con json)
		content_byte = await resp.read()
		# Convertimos a cadena
		token = content_byte.decode("utf-8")
		assert resp.status == 200, resp.status
	# Continuamos con la petición de consulta de información relacionada con el token
	async with session.get(base_url + '/get/' + str(token)) as resp:
		assert resp.status == 200, resp.status
	# Solo nos queda hacer el delete
	async with session.delete(base_url + '/delete/' + str(token)) as resp:
		assert resp.status == 200, resp.status


# https://molotov.readthedocs.io/en/stable/examples/	
import time

_T = {}


def _now():
    return time.time() * 1000


@molotov.events()
async def record_time(event, **info):
    req = info.get("request")
    if event == "sending_request":
        _T[req] = _now()
    elif event == "response_received":
        _T[req] = _now() - _T[req]


@molotov.global_teardown()
def display_average():
    average = sum(_T.values()) / len(_T)
    print("\nAverage response time %dms" % average)
