"""
Telegram I/O utils
"""
import os
import boto3
import json
import csv
from datetime import datetime

class Telegram:
	BOT_TOKEN = os.environ['BOT_TOKEN']
	URL = os.environ['URL'].format(BOT_TOKEN)
	BUCKET = os.environ['BUCKET']
	FILE_NATIONAL = os.environ['FILE_NATIONAL']
	FILE_PROVINCE = os.environ['FILE_PROVINCE']

	table = boto3.resource('dynamodb').Table('')
	bucket = boto3.resource('s3').Bucket(BUCKET)

	def __init__(self, req):
		self.requests = req

	def send_txt(self, chat_id, text):
		params = {
			"chat_id": chat_id,
			"text": text,
			#"parse_mode": "HTML"
		}
		url = self.URL + "sendMessage"
		self.requests.get(url, params=params)

	def send_keyboard(self, chat_id, text, buttons):
		reply_markup = {
			'keyboard': [buttons],
			'resize_keyboard': True,
			'one_time_keyboard': True
		}

		reply_markup = json.dumps(reply_markup)

		params = {
			"chat_id": chat_id,
			"text": text,
			"reply_markup": reply_markup
		}
		url = self.URL + "sendMessage"

		self.requests.get(url, params=params)

	def send_inline_keyboard(self, chat_id, text, buttons):
		reply_markup = {'inline_keyboard': buttons}
		reply_markup = json.dumps(reply_markup)

		params = {
			"chat_id": chat_id,
			"text": text,
			"reply_markup": reply_markup
		}

		url = self.URL + "sendMessage"


		self.requests.get(url, params=params)

	def update_bucket(self, url, file_name):
		data = self.requests.get(url).content.decode('utf-8')
		self.bucket.put_object(Key=file_name, Body=data)

	def get_csv_from_bucket(self, file_name):
		obj = self.bucket.Object(file_name)
		data = obj.get()[u'Body'].read().decode('utf-8')

		return list(csv.DictReader(data.splitlines(), delimiter=','))

	def comparator(self, old, new, compare_value):
		increment = int(new[compare_value])-int(old[compare_value])
		increment_perc = round((increment/int(old[compare_value]))*100, 1)

		return [increment, increment_perc]

	def today_response(self, chat_id):
		national = self.get_csv_from_bucket(self.FILE_NATIONAL)

		today_data = national[-1]
		actual_date = datetime.fromisoformat(today_data['data']).date()
		yesterday_data = national[-2]

		new_pos = self.comparator(yesterday_data, today_data, 'totale_positivi')
		new_osp = self.comparator(yesterday_data, today_data, 'totale_ospedalizzati')
		new_dec = self.comparator(yesterday_data, today_data, 'deceduti')
		new_ta = self.comparator(yesterday_data, today_data, 'terapia_intensiva')
		new_dim = self.comparator(yesterday_data, today_data, 'dimessi_guariti')

		message = (
			"Dati del {}\n\nNuovi positivi: {:+} ({:+.1f}%)\n"
			"Ospedalizzati: {:+} ({:+.1f}%)\n"
			"Terapia intensiva: {:+} ({:+.1f}%)\n"
			"Deceduti: {:+} ({:+.1f}%)\n"
			"Dimessi: {:+} ({:+.1f}%)").format(
				actual_date,
				new_pos[0], new_pos[1],
				new_osp[0], new_osp[1],
				new_ta[0], new_ta[1],
				new_dec[0], new_dec[1],
				new_dim[0], new_dim[1]
		)

		self.send_txt(chat_id, message)

	def provincia_response(self, chat_id, text):
		province = self.get_csv_from_bucket(self.FILE_PROVINCE)

		user_provincia = text[11:].lower()

		provincia_data = list(
			filter(
				lambda prov: \
					user_provincia in prov['denominazione_provincia'].lower(),
					province
			)
		)

		actual_date = datetime.fromisoformat(provincia_data[-1]['data']).date()

		message = (
			"""Dati del {} - {}\n\nCasi totali: {}""").format(
				actual_date,
				provincia_data[-1]['denominazione_provincia'],
				provincia_data[-1]['totale_casi']
			)

		self.send_txt(chat_id, message)

	def total_response(self, chat_id, text):
		national = self.get_csv_from_bucket(self.FILE_NATIONAL)
		today_data = national[-1]
		actual_date = datetime.fromisoformat(today_data['data']).date()

		pos = int(today_data['totale_positivi'])
		osp = int(today_data['totale_ospedalizzati'])
		dec = int(today_data['deceduti'])
		ta = int(today_data['terapia_intensiva'])
		dim = int(today_data['dimessi_guariti'])
		tam = int(today_data['tamponi'])

		message = (
			"Totali del {}\n\n"
			"Positivi: {}\n"
			"Ospedalizzati: {}\n"
			"Terapia intensiva: {}\n"
			"Deceduti: {}\n"
			"Dimessi: {}\n"
			"Tamponi: {}").format(
				actual_date,
				pos,
				osp,
				ta,
				dec,
				dim,
				tam
		)

		self.send_txt(chat_id, message)
