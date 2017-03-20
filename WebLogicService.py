import base64
import httplib
import json
import string

from SimpleKafkaProducer import SimpleKafkaProducer
from Utils import current_time_millis
from config.WLConfig import *
from kafkaConnector.Message import Message

WLS_ROOT = "/management/wls/latest/"
WLS_SERVERS = "/management/wls/latest/servers"
WLS_DEPLOYMENTS = "/management/wls/latest/deployments"
WLS_DATASOURCES = "/management/wls/latest/datasources"
WLS_TARGETS = "/management/wls/latest/targets"

ROOT_KEYS = ['name', 'activeHttpSessionCount',
             'activeThreadCount', 'configuredServerCount',
             'overallServiceHealth', 'activeServerCount', 'productionMode']

SERVER_KEYS = ['health', 'activeHttpSessionCount',
               'activeThreadCount', 'heapFreeCurrent', 'heapSizeCurrent',
               'jvmProcessorLoad', 'usedPhysicalMemory']

DATASOURCE_KEYS = ['state',
                   'connectionsTotalCount', 'leakedConnectionCount', 'waitSecondsHighCount', 'waitingForConnectionCurrentCount',
                   'numAvailable', 'numUnavailable',
                   'activeConnectionsCurrentCount', 'currCapacity', 'waitingForConnectionCurrentCount']


class WebLogicService():
    def __init__(self):
        self.producer = SimpleKafkaProducer()
        self.printOut = False

    def do_http_request(self, host, port, url, verb, username, password, body=""):
        auth = string.strip(base64.encodestring(username + ':' + password))
        service = httplib.HTTP(host, port)

        # headers
        service.putrequest(verb, url)
        service.putheader("Host", host)
        service.putheader("User-Agent", "Python http auth")
        service.putheader("Content-type", "text/html; charset=\"UTF-8\"")
        service.putheader("Authorization", "Basic %s" % auth)
        service.putheader("Accept", "application/json")
        service.endheaders()
        service.send(body)

        # get the response
        status_code, status_message, header = service.getreply()
        res = service.getfile().read()
        return status_code, status_message, header, res

    def do_wls_http_get(self, url, verb):
        return self.do_http_request(WLS_HOST, WLS_PORT, url, verb, WLS_USERNAME, WLS_PASSWORD)

    def check_root(self, link, time):
        status_code, status_message, header, res = self.do_wls_http_get(link, "GET")
        if status_code != 200:
            self.error("HTTP status code: " + str(status_code))
            return

        jres = json.loads(res)
        self.info('SERVER OVERALL HEALTH')
        item = jres['item']
        for key in ROOT_KEYS:
            if key == 'overallServiceHealth':
                self.info('\t', key, ':', item[key]['state'])
            else:
                self.info('\t', key, ':', item[key])

        msg = Message(time)
        msg.tag('eventType', 'WLS_ROOT')
        msg.tag('eventSource', 'WLS_REST')
        msg.tag('name', item['name'])
        msg.tag('overallServiceHealth', item['overallServiceHealth']['state'])
        msg.field('overallServiceHealthValue', 1 if item['overallServiceHealth']['state'] == 'ok' else 0)
        msg.tag('productionMode', item['productionMode'])
        msg.field('activeServerCount', item['activeServerCount'])
        msg.field('activeHttpSessionCount', item['activeHttpSessionCount'])
        msg.field('activeThreadCount', item['activeThreadCount'])
        msg.field('configuredServerCount', item['configuredServerCount'])
        self.producer.sendMessage('wls-health', msg, 'wls-prod')

    def check_servers(self, link, time):
        status_code, status_message, header, res = self.do_wls_http_get(link, "GET")
        if status_code != 200:
            self.error("HTTP status code: " + str(status_code))
            return

        jres = json.loads(res)
        self.info('SERVERS HEALTH')
        items = jres['items']
        for item in items:
            name = item['name']
            state = item['state']
            self.info('\t', name)
            self.info('\t\t', 'state', ':', state)

            msg = Message(time)
            msg.tag('eventType', 'WLS_SERVERS')
            msg.tag('eventSource', 'WLS_REST')
            msg.tag('name', item['name'])
            msg.tag('state', item['state'])
            msg.field('running', 1 if item['state'] == 'running' else 0)

            if state != 'running':
                continue

            msg.tag('health', item['health']['state'])
            msg.field('healthValue', 1 if item['health']['state'] == 'ok' else 0)
            msg.field('activeHttpSessionCount', item['activeHttpSessionCount'])
            msg.field('activeThreadCount', item['activeThreadCount'])
            msg.field('heapFreeCurrent', item['heapFreeCurrent'])
            msg.field('heapSizeCurrent', item['heapSizeCurrent'])
            msg.field('heapUsageCurrent', item['heapSizeCurrent'] - item['heapFreeCurrent'])
            msg.field('jvmProcessorLoad', item['jvmProcessorLoad'])
            msg.field('usedPhysicalMemory', item['usedPhysicalMemory'])
            self.producer.sendMessage('wls-health', msg, 'wls-prod')

            for key in SERVER_KEYS:
                if key == 'health':
                    self.info('\t\t', key, ':', item[key]['state'])
                else:
                    self.info('\t\t', key, ':', item[key])

    def check_datasources(self, link, time):
        status_code, status_message, header, res = self.do_wls_http_get(link, "GET")
        if status_code != 200:
            print "HTTP status code: " + str(status_code)
            return

        self.info('DATASOURCES')
        jres = json.loads(res)
        items = jres['items']
        for item in items:
            self.info('\t', item['name'])
            self.info('\t\t', 'targets:', ', '.join(item['targets']))

            if not item.has_key('aggregateMetrics'):
                continue

            metric = item['aggregateMetrics']
            for key in DATASOURCE_KEYS:
                self.info('\t\t', key, metric[key])

            msg = Message(time)
            msg.tag('eventType', 'WLS_DATASOURCES')
            msg.tag('eventSource', 'WLS_REST')
            msg.tag('name', item['name'])
            msg.tag('targets', ', '.join(item['targets']))
            msg.tag('state', metric['state'])
            msg.field('stateValue', 1 if metric['state'] == 'Running' else 0)
            msg.field('connectionsTotalCount', metric['connectionsTotalCount'])
            msg.field('leakedConnectionCount', metric['leakedConnectionCount'])
            msg.field('waitSecondsHighCount', metric['waitSecondsHighCount'])
            msg.field('waitingForConnectionCurrentCount', metric['waitingForConnectionCurrentCount'])
            msg.field('numAvailable', metric['numAvailable'])
            msg.field('numUnavailable', metric['numUnavailable'])
            msg.field('activeConnectionsCurrentCount', metric['activeConnectionsCurrentCount'])
            msg.field('currCapacity', metric['currCapacity'])
            msg.field('waitingForConnectionCurrentCount', metric['waitingForConnectionCurrentCount'])
            self.producer.sendMessage('wls-health', msg, 'wls-prod')

    def info(self, *msg):
        if self.printOut:
            print(msg)

    def error(self, *msg):
        print(msg)

    def check_wls(self):
        time = current_time_millis()
        print('checking wls...')
        self.check_root(WLS_ROOT, time)
        self.check_servers(WLS_SERVERS, time)
        self.check_datasources(WLS_DATASOURCES, time)
        print('checked wls.')
