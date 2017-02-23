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


def do_http_request(host, port, url, verb, username, password, body=""):
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


def do_wls_http_get(url, verb):
    return do_http_request(WLS_HOST, WLS_PORT, url, verb, WLS_USERNAME, WLS_PASSWORD)


ROOT_KEYS = ['name', 'activeHttpSessionCount',
             'activeThreadCount', 'configuredServerCount',
             'overallServiceHealth', 'activeServerCount', 'productionMode']

SERVER_KEYS = ['health', 'activeHttpSessionCount',
               'activeThreadCount', 'heapFreeCurrent', 'heapSizeCurrent',
               'jvmProcessorLoad', 'usedPhysicalMemory']

DATASOURCE_KEYS = ['state', 'serverName',
                   'connectionsTotalCount', 'leakedConnectionCount', 'waitSecondsHighCount', 'waitingForConnectionCurrentCount',
                   'numAvailable', 'numUnavailable',
                   'activeConnectionsCurrentCount', 'currCapacity', 'waitingForConnectionCurrentCount']


def check_root(link):
    status_code, status_message, header, res = do_wls_http_get(link, "GET")
    if status_code != 200:
        print "HTTP status code: " + str(status_code)
        return

    producer = SimpleKafkaProducer()
    time = current_time_millis()
    jres = json.loads(res)
    print 'SERVER OVERALL HEALTH'
    item = jres['item']
    for key in ROOT_KEYS:
        if key == 'overallServiceHealth':
            print '\t', key, ':', item[key]['state']
        else:
            print '\t', key, ':', item[key]

    msg = Message(time)
    msg.tag('eventType', 'WLS_ROOT')
    msg.tag('eventSource', 'WLS_REST')
    msg.tag('name', item['name'])
    msg.tag('overallServiceHealth', item['overallServiceHealth']['state'])
    msg.tag('productionMode', item['productionMode'])
    msg.field('activeServerCount', item['activeServerCount'])
    msg.field('activeHttpSessionCount', item['activeHttpSessionCount'])
    msg.field('activeThreadCount', item['activeThreadCount'])
    msg.field('configuredServerCount', item['configuredServerCount'])
    producer.sendMessage('wls-health', msg, 'wls-test')


def check_servers(link):
    status_code, status_message, header, res = do_wls_http_get(link, "GET")
    if status_code != 200:
        print "HTTP status code: " + str(status_code)
        return

    jres = json.loads(res)
    print 'SERVERS HEALTH'
    items = jres['items']
    for item in items:
        name = item['name']
        state = item['state']
        print '\t', name
        print '\t\t', 'state', ':', state

        if state != 'running':
            continue

        for key in SERVER_KEYS:
            if key == 'health':
                print '\t\t', key, ':', item[key]['state']
            else:
                print '\t\t', key, ':', item[key]


def check_datasources(link):
    status_code, status_message, header, res = do_wls_http_get(link, "GET")
    if status_code != 200:
        print "HTTP status code: " + str(status_code)
        return

    jres = json.loads(res)
    print 'DATASOURCES'
    items = jres['items']
    for item in items:
        print '\t', item['name']
        print '\t\t', 'targets:', ', '.join(item['targets'])

        if not item.has_key('dataSourceMetrics'):
            continue

        for metric in item['dataSourceMetrics']:
            for key in DATASOURCE_KEYS:
                print '\t\t', key, metric[key]


def check_wls():
    check_root(WLS_ROOT)
    check_servers(WLS_SERVERS)
    check_datasources(WLS_DATASOURCES)
