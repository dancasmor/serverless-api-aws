from telegram.ext import *
import requests
import json


####################################
# Variables TELEGRAM
####################################

# Token de identificación del bot
_token = 'YOUR_TOKEN_ID'

# Entidad encargada de comprobar si ha habido actualizaciones/nuevos mensajes en los chats
updater = Updater(token=_token, use_context=True)

# Textos por defecto del bot
MSG_INFO_HELP_T = "Los comandos empiezan por '/', quedando '/comando arg1 arg2'. En caso de introducir una frase con " \
           "espacios, colocarla entre \" \"." + "\n" + "Podemos encontrar los siguientes: " + "\n\n"
MSG_GENERAR_HELP_T = "    + '/generarToken' -> Genera un token para asociar el chat de telegram con otro\n"
MSG_EMPAREJAR_HELP_T = "    + '/emparejar token' -> Empareja el chat de telegram actual con el del asociado al token\n"
MSG_RERCORDAR_HELP_T = "    + '/recordar token' -> Devuelve que 2 chats están asociados por el token\n"
MSG_ELIMINAR_HELP_T = "    + '/eliminar token' -> Elimina el emparejamiento que use dicho token\n"
MSG_INFO_COMPUESTO_T = [MSG_INFO_HELP_T, MSG_GENERAR_HELP_T, MSG_EMPAREJAR_HELP_T, MSG_RERCORDAR_HELP_T,
                        MSG_ELIMINAR_HELP_T]
MSG_INFO_COMPUESTO_T = "".join(MSG_INFO_COMPUESTO_T)
MSG_START_T = MSG_INFO_COMPUESTO_T

# URLs API REST
URL_BASE = "YOUR_AWS_BASE_URL"
# Generate (post)
URL_GENERATE_ENDPOINT = URL_BASE + "/create"
# Get (get)
URL_GET_ENDPOINT = URL_BASE + "/get/"
# Update (put)
URL_PUT_ENDPOINT = URL_BASE + "/update/"
# Delete (delete)
URL_DELETE_ENDPOINT = URL_BASE + "/delete/"

# Variable con toda la lista de tokens
listaTokens = {}


####################################
# Funciones en común
####################################

# Busca todos los chats de telegram asociado al chat de tipo indicado
def buscarEmparejamientosTokens(grupoId, tipo):
    # Buscamos todos los tokens asociados al grupo
    token = []
    for emparejamiento in listaTokens.items():
        # Extraemos el par de grupos de cada conjunto y comprobamos si contiene al grupo deseado
        pareja = emparejamiento[1]
        if pareja[tipo] == grupoId:
            # En caso afirmativo, tomamos el conjunto completo
            token.append(emparejamiento)
    return token


####################################
# Lista de comandos TELEGRAM
####################################

# Presentación del bot
def start(update, context):
    # Respondemos al comando enviando un mensaje de comienzo del bot
    context.bot.send_message(chat_id=update.message.chat_id, text=MSG_START_T)


# Comando encargado de emparejar los chats
def emparejar(update, context):
    # Tomamos el id del chat del usuario actual
    chat_id = update.message.chat_id

    # Comprobamos el token adjuntado con el comando
    msg = update.message.text
    _, token = msg.split(' ')

    if token == "":
        context.bot.send_message(chat_id=chat_id, text="Token no añadido")
    else:
        # Comprobamos si dicho token pertenece a alguno de los generados y almacenados
        if token in listaTokens.keys():
            # En caso afirmativo, efectuamos el emparejamiento llamando a la API
            data = json.dumps({"chatid": chat_id})
            respuesta = requests.post(url=URL_PUT_ENDPOINT+token, data=data).text
            # Comprobamos la respuesta
            if "message" in respuesta:
                listaTokens[token]["receptor"] = chat_id
                # Comunicamos al usuario el emparejamiento correcto
                context.bot.send_message(chat_id=chat_id, text="Emparejado correctamente")
            else:
                context.bot.send_message(chat_id=chat_id,
                                         text="Error en el servidor de tokens, inténtelo de nuevo más tarde")
        else:
            context.bot.send_message(chat_id=chat_id, text="Ningún grupo ha generado dicho token")


# Genera un token y lo almacena asociado al chat en el que se ha solicitado
def generarToken(update, context):
    # Tomamos el id del chat del usuario actual
    chat_id = update.message.chat_id

    # Realizamos la petición a la API REST
    data = json.dumps({"chatid": chat_id})
    respuesta = requests.post(url=URL_GENERATE_ENDPOINT, data=data).text
    # Comprobamos la respuesta
    if "message" in respuesta:
        context.bot.send_message(chat_id=chat_id, text="Error en el servidor de tokens, inténtelo de nuevo más tarde")
    else:
        # Extreamos el token
        token = respuesta
        # Guardar token asociado al chat de telegram en el que se solicita, en la variable global
        listaTokens.update({token: {"emisor": chat_id, "receptor": ""}})

        # Se envía al chat
        context.bot.send_message(chat_id=chat_id, text="El token es: ")
        context.bot.send_message(chat_id=chat_id, text=token)


# Devuelve el emparejamiento asociado al token
def recordarToken(update, context):
    chatId = update.message.chat.id

    # Comprobamos el token adjuntado con el comando
    msg = update.message.text
    _, token = msg.split(' ')

    if token == "":
        context.bot.send_message(chat_id=chatId, text="Token no añadido")
    else:
        # En caso afirmativo, consultamos la API
        respuesta = requests.get(url=URL_GET_ENDPOINT + token).text
        # Comprobamos la respuesta
        if "message" in respuesta:
            context.bot.send_message(chat_id=chatId,
                                     text="Error en el servidor de tokens, inténtelo de nuevo más tarde")
        else:
            respuesta = eval(respuesta)
            chatId1 = respuesta["id_chat1"]
            chatId2 = respuesta["id_chat2"]
            context.bot.send_message(chat_id=chatId,
                                     text="Chats asociados a este token: " + "\n" + str(chatId1) + "\n" + str(chatId2))


# Elimina el token y, por ende, la sincronización entre chats, pasada por parámetro
def eliminarToken(update, context):
    # Tomamos el id del chat del usuario actual
    chat_id = update.message.chat_id

    # Comprobamos el token adjuntado con el comando
    msg = update.message.text
    _, token = msg.split(' ')

    if token == "":
        context.bot.send_message(chat_id=chat_id, text="Token no añadido")
    else:
        # Comprobamos si dicho token pertenece a alguno de los generados y almacenados
        if token in listaTokens.keys():
            if listaTokens[token]["emisor"] == chat_id or listaTokens[token]["receptor"] == chat_id:
                # En caso afirmativo, mandamos la petición API
                respuesta = requests.delete(url=URL_DELETE_ENDPOINT + token).text
                # Comprobamos la respuesta
                if "message" in respuesta:
                    context.bot.send_message(chat_id=chat_id,
                                             text="Error en el servidor de tokens, inténtelo de nuevo más tarde")
                else:
                    # eliminamos dicha definición en el diccionario
                    listaTokens.pop(token)
                    # Comunicamos al usuario de eliminación correcta
                    context.bot.send_message(chat_id=chat_id, text="Eliminado correctamente")
            else:
                context.bot.send_message(chat_id=chat_id, text="Token no eliminado, pertenece a otro grupo")
        else:
            context.bot.send_message(chat_id=chat_id, text="Ningún grupo ha generado dicho token")


# Función que maneja el envio de mensajes al chat del bot
def lectura(update, context):
    # Comprobamos el mensaje y el chat en el que se da
    msg = update.message.text
    chatId = update.message.chat.id
    autorNick = update.message.from_user.username

    # Buscamos todos los chats asociados al actual
    parejas = buscarEmparejamientosTokens(chatId, "emisor") + buscarEmparejamientosTokens(chatId, "receptor")
    if not (len(parejas) == 0):
        # Montamos el mensaje
        msg = "(" + autorNick + ") " + msg
        # Enviamos el mensaje a cada chat encontrado
        for chat_id in parejas:
            if not (chat_id[1]["emisor"] == "") and not (chat_id[1]["receptor"] == ""):
                if chat_id[1]["emisor"] == chatId:
                    chatDestino = chat_id[1]["receptor"]
                else:
                    chatDestino = chat_id[1]["emisor"]
                context.bot.send_message(chat_id=chatDestino, text=msg)


# Función de asignación de comandos a funciones (handler)
def handlerFunction(dp):
    # Comando /start
    handler = CommandHandler('start', start)
    dp.add_handler(handler)

    # Comando /generarToken
    handler = CommandHandler('generarToken', generarToken)
    dp.add_handler(handler)

    # Comando /emparejar
    handler = CommandHandler('emparejar', emparejar)
    dp.add_handler(handler)

    # Comando /recordarToken
    handler = CommandHandler('recordar', recordarToken)
    dp.add_handler(handler)

    # Comando /eliminarToken
    handler = CommandHandler('eliminar', eliminarToken)
    dp.add_handler(handler)

    # Mensajes
    handler = MessageHandler(Filters.text, lectura)
    dp.add_handler(handler)


####################################
# Inicialización del programa
####################################

# Inicialiación del bot de telegram
def botTelegram():
    # Objeto al cual el updater envía los mensajes recibidos para ser gestionados
    dispatcher = updater.dispatcher

    # Asociamos a cada comando/mensaje recibido una función que lo gestione
    handlerFunction(dispatcher)

    # Iniciamos la ejecución del bucle infinito (polling) del bot
    updater.start_polling()
    updater.idle()


def main():
    # El bot de telegram solo puede trabajar en el hilo principal
    botTelegram()


if __name__ == '__main__':
    main()
