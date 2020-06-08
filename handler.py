"""
Lambda handler file for AWS
"""
import os
import re
import traceback
import json
import requests
from telegram_utils import Telegram


URL_NATIONAL = os.environ['URL_NATIONAL']
URL_PROVINCE = os.environ['URL_PROVINCE']
FILE_NATIONAL = os.environ['FILE_NATIONAL']
FILE_PROVINCE = os.environ['FILE_PROVINCE']


def lambda_handler(event, context):
	try:
		telegram = Telegram(requests)

		if 'operation' in event:
			message = event['operation']
			telegram.update_bucket(URL_NATIONAL, FILE_NATIONAL)
			telegram.update_bucket(URL_PROVINCE, FILE_PROVINCE)
		else:
			if 'body' in event:
				message = json.loads(event['body'])

			if 'callback_query' in message:
				chat_id = int(message['callback_query']['message']['chat']['id'])
				text = message['callback_query']['message']['text']
				data = message['callback_query']['data']
			else:
				chat_id = message['message']['chat']['id']
				text = message['message']['text']
				data = ['']

			if text == '/start':
				telegram.send_txt(chat_id, "First test")

			if re.match("/oggi", text):
				telegram.today_response(chat_id)

			if re.match("/provincia", text):
				telegram.provincia_response(chat_id, text)

			if re.match("/totale", text):
				telegram.total_response(chat_id, text)

	except Exception as inst:
		print(inst)
		traceback.print_exc()

	finally:
		return {'statusCode': 200}
