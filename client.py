#LuanNG
#Demo of using mqtt client


import sys
import re
import time
import random
from datetime import datetime as datetimep
# sys.path.append('../paho.mqtt.python/src/paho')
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
# ADDRESS = '222.255.167.8'
ADDRESS = '127.0.0.1'
PORT = 1883

#Type of device
TYPE_DEVICE = 'relayio'

#Topic to pusblish info about what device mqtt client stand for
DEFAULT_TOPIC = 'SYS/get_topic'
SUB_TOPIC = ''

#Topic will publish info about state of lamp
TOPIC = ''

#List state of device
# list_state = ['ON','OFF']

#Active state of device
SENSOR_STATE  = {1: False, 2: False, 3: False, 4: True, 5: False, 6: True, 7:False, 8:True}

LOCK_STATE  = {1: False, 2: False, 3: False, 4: True, 5: False, 6: True, 7:False, 8:True}


STATION = '1'

# client_id = TYPE_DEVICE + "/" + ''.join(random.choice("0123456789ADCDEF") for x in range(23-5))

client_id = TYPE_DEVICE + '/123456789abc'

def on_connect(mqttc, obj, flags, rc):
	print '\n',time.ctime(),' on_connect with obj=',obj,';flags=',flags,';rc=',rc


def on_disconnect(mqttc, obj, rc):
	print '\n',time.ctime(),' on_disconnect with obj=',obj,';rc=',rc

def on_publish(mqttc, userdata, mid):
	print '\n',time.ctime(),' on_publish userdata=',userdata,';mid=',mid

def on_subscribe(client, userdata, mid, granted_qos):
	print '\n'+str(datetimep.now())+' on_subscribe userdata=',userdata,';mid=',mid,';granted_qos=',granted_qos

def on_log(client, userdata, level, buf):
    print '\n',time.ctime(),' on_log userdata=',userdata,';level=',level,'buf=',buf

def on_message_msgs(mosq, obj, msg):
	global STATE, SUB_TOPIC 
    # This callback will only be called for messages with topics that match topic subscribe
	print '\n',time.ctime(),' on_message_msgs topic=',msg.topic,';qos=',msg.qos,'payload=',msg.payload
	payload = msg.payload
	if '_force_change_state_' in payload:
		regex = 'mqtt_client_id_([\S]+)_force_change_state_([\S]+)'
		data = re.findall(regex, payload)[0]
		if data[0] == client_id:
			rcv_state = data[1]
			
			print '\n data from publish_data_mqtt_client_ = ',data
			if rcv_state == 'change_to_next_state':
				index = list_state.index(STATE)
				if index < len(list_state) -1:
					STATE = list_state[index+1]
				else:
					STATE = list_state[0]

			elif data[1] in list_state:
				STATE = rcv_state
			print "\n Change state of device to: ", STATE

	elif '_topic_subscribe_' in payload:
		regex = 'mqtt_client_id_([\S]+)_topic_subscribe_([\S]+)'
		data = re.findall(regex, payload)[0]
		print "\n\n data from _topic_subcribe_ =",data
		if data[0] == client_id:
			mqttc.subscribe(data[1], 0)

			publish_data = 'mqtt_client_id_' + client_id + '_subcribed_on_' + data[1]
			mqttc.publish(data[1], publish_data)

			byte_sensor = get_byte_state(True)
			publish_data = 'mqtt_client_id_' + client_id + '_station_ALL_sensor_status_' + str(byte_sensor)
			mqttc.publish(data[1], publish_data)

			byte_lock = get_byte_state(False)
			publish_data = 'mqtt_client_id_' + client_id + '_station_ALL_lock_status_' + str(byte_lock)
			mqttc.publish(data[1], publish_data)

			SUB_TOPIC = data[1]

		else:
			print "\n\n\n different client Id"

	elif '_set_lock_' in payload:
		regex = 'mqtt_client_id_([\S]+)_station_([\S]+)_set_lock_([\S]+)'
		data = re.findall(regex, payload)[0]
		print "\n\n data from _set_lock_ =",data
		if data[0] == client_id:
			station = data[1].lower()
			lock = data[2].lower()
			lock = True if lock =='on' else False

			if station !='all':
				LOCK_STATE[int(station)] = lock
			else:
				for index in LOCK_STATE:
					LOCK_STATE[index] = lock

	elif 'get_status' in payload:
		regex = 'mqtt_client_id_([\S]+)_station_([\S]+)_get_status'
		data = re.findall(regex, payload)[0]
		print "\n\n data from get_status =",data
		if data[0] == client_id:
			station = data[1].lower()

			
			publish_data = 'mqtt_client_id_' + client_id 
			if station == 'all':
				byte_lock = get_byte_state(False)
				publish_data += '_station_ALL_sensor_status_' + str(byte_lock)
			else:
				lock = 'ON' if SENSOR_STATE[int(station)] else 'OFF'
				publish_data += '_station_' + station +'_sensor_status_' + lock

			publish.single(SUB_TOPIC, publish_data, hostname=ADDRESS, port=PORT)

	elif 'get_lock' in payload:
		regex = 'mqtt_client_id_([\S]+)_station_([\S]+)_get_lock'
		data = re.findall(regex, payload)[0]
		print "\n\n data from get_lock =",data
		if data[0] == client_id:
			station = data[1].lower()

			
			publish_data = 'mqtt_client_id_' + client_id 
			if station == 'all':
				byte_lock = get_byte_state(False)
				publish_data += '_station_ALL_lock_status_' + str(byte_lock)
			else:
				lock = 'ON' if LOCK_STATE[int(station)] else 'OFF'
				publish_data += '_station_' + station +'_lock_status_' + lock

			publish.single(SUB_TOPIC, publish_data, hostname=ADDRESS, port=PORT)



def get_byte_state(is_sensor_state=False):
	res = 0
	dict = {}
	if is_sensor_state:
		dict = SENSOR_STATE
	else: 
		dict = LOCK_STATE

	for item in dict:
		if dict[item]:
			res += 2**(item-1)

	return res

mqttc = mqtt.Client(client_id=client_id, clean_session=True)

mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_message = on_message_msgs
mqttc.on_subscribe = on_subscribe
# mqttc.on_log = on_log

mqttc.connect(ADDRESS, PORT, 60)

mqttc.subscribe(DEFAULT_TOPIC, 0)


# mqttc.message_callback_add(DEFAULT_TOPIC, on_message_msgs)
# 'mqtt_client_id_([\S]+)_state_([\S]+)_device_type_([\S]+)_station_info_([\S]+)_inititial_connect'


data = 'mqtt_client_id_'+mqttc._client_id+'_device_type_' +TYPE_DEVICE+'_initial_connect'
mqttc.publish(DEFAULT_TOPIC, data)

mqttc.loop_forever()

print '\n message after loop loop_forever'