For any python script first install requirements

## NOTE
Before running these please make sure, scripts have permission to write read and execute over the directories they are assigned with 


Cron syntax for per minute job
*/1 * * * * /dionaea/lib/dionaea/convert_sqlite_to_json.py >> /var/log/cron_dionaea.log 2>&1  

Iptable script
Place in /var/log/

Dionaea Sqlite Script assigned to /dionaea/lib/dionaea
Place in /dionaea/lib/dionaea/
Ensure sqlite file is in same directory

Dionaea file script assigned to /dionaea/lib/dionaea
Place in /cuckoo/
Ensure dionaea binaries are in /dionaea/lib/dionaea/

Snare&Tanner assigned to /opt/snare/
Place with snare.log file

All these will generate json files
All these should be shcheduled with Cron

Fluentd should be configured at the end when are logging is configured correctly