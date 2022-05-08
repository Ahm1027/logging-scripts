import requests
from urllib.parse import urljoin
import time
import sys
import os
import json
import re
from datetime import datetime

global log_file, log_position_file, json_log_file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(BASE_DIR, 'snare.log')
log_position_file = os.path.join(BASE_DIR, 'snare.log.position')
json_log_file = os.path.join(BASE_DIR, 'snare_log.json')


"""
format_access_request
Function that adds fields to intermediate access request logs dictionary
Params:
	=> _idx: int (line indicating index for request type in log string that can be used for positioning of other parameters)
	=> _chunks : list (log string divided into chunks based on space delimiter)
	=> method: str (specifying GET or POST)
Returns:
	=> log : Dictionary
	{
	'method': str/null,
	'request': str/null,
	'http': str/null,
	'status': str/null,
	'port': str/null,
	'dump' (useragent and non formatted characters): str/null
	}
"""
def format_access_request(idx, chunks, method):
    request = {}
    request['method'] = method
    request['request'] = chunks[idx+1].rstrip()
    request['http'] = chunks[idx+2]
    request['status'] = chunks[idx+3]
    request['port'] = chunks[idx+4]
    request['dump'] = ' '.join(chunks[idx+6: len(chunks)-1])
    return request



"""
parses_access_requests
Function that parses Aiohttp access request type logs
Params:
	=> _logs: str (single line from .log file)
Returns:
	=> log : Dictionary
	{
	'type': str/null,
	'timestamp': str/null,
	'destination_IP': str/null,
	'method': str/null,
	'request': str/null,
	'http': str/null,
	'status': str/null,
	'port': str/null,
	'dump' (useragent and non formatted characters): str/null
	}
"""
def parse_access_requests(_log):
    request = {}
    request['type'] = 'aiohttp.access:log'
    request['timestamp'] = re.match(r'[\d]{4}-[\d]{2}-[\d]{2} [\d]{2}:[\d]{2}:[\d]{2}', _log, re.M|re.I).group()
    
    chunks = _log.split(" ")
    for idx, partition in enumerate(chunks):
        match_IP = re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', partition, re.M|re.I)
        if match_IP:
            request["destination_IP"] = match_IP.group()
            continue

        if partition == r'"GET' or partition == 'GET':
            return {**request, **format_access_request(idx, chunks, 'GET')}
        if partition == r'"POST' or partition == 'POST':
            return {**request, **format_access_request(idx, chunks, 'POST')}


def new_position_file():
	global log_position_file
	try:
		with open(log_position_file, "r") as position_file_handler:
			lines = position_file_handler.readlines()
			return len(lines) == 0
	except:
		return True


"""
Main Runner method
"""
def log_to_json():
    global log_file, log_position_file, json_log_file
    with open(log_file, "r") as log_file:
    	lines = log_file.readlines()
    	total_lines = len(lines)
    	if not new_position_file():
    		with open(log_position_file, "r") as position_file_handler:
		    	position = position_file_handler.readline()
    			if position != "":
	    			position = int(position)
	    			lines = lines[position:]
    	if len(lines) == 0: return
    	json_file_handler = open(json_log_file, "a+")
    	for line in lines:
            try:
                log_data = ''
                if re.search(r"aiohttp\.access:log", line, re.M|re.I):
                    log_data = json.dumps(parse_access_requests(line))
                if log_data != '': 
                	json_file_handler.write(str(log_data+"\n"))
            except:
                continue
    	json_file_handler.close()
    	with open("snare.log.position", "w") as f:
        	f.write(str(total_lines))

log_to_json()