import sqlite3
import pandas as pd
import geoip2.database
from geoip2 import errors
import os
import datetime
import json

def create_df(cursor):
	cursor.execute('SELECT * FROM connections JOIN downloads ON connections.connection = downloads.connection')
	data = cursor.fetchall()
	header = [x[0] for x in cursor.description]
	df = pd.DataFrame(data, columns=header)
	position_file_path = os.path.join(BASE_DIR, "position.txt")
	if os.path.exists(position_file_path):
		records_already_read = 0
		with open(position_file_path, 'r+') as f:
			records_already_read = int(f.read())
			f.seek(0)
			f.write(str(records_already_read))
			df = df.iloc[records_already_read-1:]
			f.truncate()
	else:
		with open(position_file_path, 'w') as w:
			w.write(str(len(df)))

	try:
		df.drop(columns=['connection_type', 'connection_transport', 'connection_protocol', 'connection_root', 'connection_parent', 'download', 'remote_hostname'], inplace=True)
	except KeyError:
		print('df keys not found')

	df['country'] = get_countries(df)
	output_file_path = os.path.join(BASE_DIR, "dionaea_output.json")
	if os.path.exists(output_file_path):
		with open(output_file_path, 'a') as a:
			for x in df.iterrows():
				a.write(json.dumps(x[1].to_dict())+"\n")
		return
	with open(output_file_path, 'w') as w:
		for x in df.iterrows():
			w.write(json.dumps(x[1].to_dict())+"\n")

def get_countries(df):
	countries = []
	country_db_location = os.path.join(BASE_DIR, "geoip_data", "GeoLite2-Country.mmdb")
	with geoip2.database.Reader(country_db_location) as r:
		for x in df.iterrows():
			try:
				response_city = r.country(x[1]['remote_host'])
				countries.append(response_city.country.name)
			except errors.AddressNotFoundError:
				countries.append('Others')
				continue
	return countries


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "logsql.sqlite")

conn = sqlite3.connect(db_path)
c = conn.cursor()
create_df(c)
c.close()
conn.close()
