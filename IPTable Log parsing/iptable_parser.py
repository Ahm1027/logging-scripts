import re
import json
import sys
import os
import json
from datetime import datetime
import geoip2.database
from geoip2 import errors

global countries, pair_re, previous, log_file, log_position_file, json_log_file

countries = ["Qatar","India","Russia","China","Korea","Israel","Pakistan", "United States"]
# dpt = ["22","21","80","445","443","502"]
pair_re = re.compile('([^ ]+)=([^ ]+)')
previous = ""
data = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(BASE_DIR, 'kern.log')
log_position_file = os.path.join(BASE_DIR, 'kern_log.txt')
json_log_file = os.path.join(BASE_DIR, 'kern.json')

def new_position_file():
    global log_position_file
    try:
        with open(log_position_file, "r") as position_file_handler:
            lines = position_file_handler.readlines()
            return len(lines) == 0
    except:
        return True


def parse_logs():
    global log_file, log_position_file, json_log_file, previous, pair_re, countries
    with open(json_log_file, 'a') as f:
        with open(log_file, "r") as log_file_handler:
            lines = log_file_handler.readlines()
            total_lines = len(lines)
            if not new_position_file():
                with open(log_position_file, "r") as position_file_handler:
                    position = position_file_handler.readline()
                    if position != "":
                        position = int(position)
                        lines = lines[position:]
            if len(lines) == 0: return
            country_db_location = os.path.join(BASE_DIR, "geoip_data", "GeoLite2-Country.mmdb")
            with geoip2.database.Reader(country_db_location) as country_db_descriptor:
                for line in lines:
                        if "ping"  in line:
                            line = line.rstrip()
                            data = dict(pair_re.findall(line))
                            try:
                                previous =  data['SRC']
                                if previous ==  data['SRC'] and date[6] =="ping_others":
                                    pass

                                else:
                                    d = date[0]+" "+date[1]+" "+date[2]
                                    p = {'date_time': d, 'source':date[6],'proto':data['PROTO'],'ttl':data['TTL'],'src':data['SRC'],'dst':data['DST'],'len':data['LEN'],'result':'ping'}
                            except Exception as e:
                                print("Exception for data: ", data)

                        elif "_scan"  in line:
                            line = line.rstrip()
                            data = dict(pair_re.findall(line))
                            date = line.split()
                            try:
                                if previous ==  data['SRC'] and date[6] =="_scan":
                                    previous = ""
                                else:
                                    if data['SRC'] != "127.0.0.1" or data['DST'] != "127.0.0.1":
                                        previous =  data['SRC']
                                        d = date[0]+" "+date[1]+" "+date[2]
                                        country = 'Others'
                                        try:
                                            response_city = country_db_descriptor.country(data['SRC'])
                                            country = response_city.country.name
                                            if country not in countries:
                                                country = 'Others'
                                        except errors.AddressNotFoundError:
                                            country = 'Others'
                                        p = {'date_time': d, 'country': country, 'source':date[6],'proto':data['PROTO'],'dpt':data['DPT'],'spt': data['SPT'],'src':data['SRC'],'dst':data['DST'],'len':data['LEN'],'result':'scan'}
                                        
                                        log = json.dumps(p)
                                        f.write(str(log+"\n"))
                            except Exception as e:
                                print("Exception for data: ", data)

                        elif "interaction" in line:
                            line = line.rstrip()
                            data = dict(pair_re.findall(line))
                            date = line.split()
                            try:
                                if previous ==  data['SRC'] and date[6] =="interaction_others":
                                    previous = ""
                                else:
                                    previous =  data['SRC']
                                    d = date[0]+" "+date[1]+" "+date[2]
                                    country = 'Others'
                                    try:
                                        response_city = country_db_descriptor.country(data['SRC'])
                                        country = response_city.country.name
                                        if country not in countries:
                                            country = 'Others'
                                    except errors.AddressNotFoundError:
                                        country = 'Others'
                                    p = {'date_time': d, 'country': country, 'source':date[6],'proto':data['PROTO'],'dpt':data['DPT'],'spt': data['SPT'],'src':data['SRC'],'dst':data['DST'],'len':data['LEN'],'result':'scan'}
                                    
                                    log = json.dumps(p)
                                    f.write(str(log+"\n"))
                            except Exception as e:
                                print("Exception for data: ", data)

                        else:
                            pass
            with open(log_position_file, "w") as f:
                f.write(str(total_lines))

parse_logs()
