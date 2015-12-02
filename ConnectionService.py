# ConnectionService.py
#
# Handles the connection to WebLogic Application Server
#
# @author   Orhun Dalabasmaz
# @since    Dec, 2015

import re
from types import NoneType

import mechanize
from BeautifulSoup import BeautifulSoup

from config.WLConfig import *

# list-dictionary
header_list = []
server_list = []
column_sizes = {}


def do_login_and_request_page():
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.addheaders = [("User-agent",
                      "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13")]

    br.open(wl_login_uri)

    br.select_form(name="loginData")

    br["j_username"] = wl_username
    br["j_password"] = wl_password

    logged_in = br.submit()

    login_response = logged_in.read()
    is_failed = "Authentication Denied" in login_response
    if is_failed:
        print "Authentication Denied"
        return "Authentication Denied"

    res = br.open(wl_main_uri).read()
    return res


def arrange_column_size(c_count, size):
    if c_count in column_sizes:
        curr_size = column_sizes[c_count]
        column_sizes[c_count] = curr_size if curr_size > size else size
    else:
        column_sizes[c_count] = size


def get_server_status(response_value):
    soup = BeautifulSoup(response_value)

    # server_status
    table = soup.find('table', 'datatable')
    is_header = False
    r_count = 0
    for tr in table.findAll('tr'):
        c_count = 0
        if not is_header:
            for th in tr.findAll('th'):
                header = format_value(th.find(text=True))
                arrange_column_size(c_count, len(header))
                header_list.append(header)
                c_count += 1
            is_header = True
            continue

        statuses = {}
        for td in tr.findAll('td'):
            header = header_list[c_count]
            column = format_value(td.find(text=True))
            arrange_column_size(c_count, len(column))
            statuses[header] = column
            c_count += 1
        server_list.append(statuses)
        r_count += 1

    # system_status
    system_status = {}
    status_data = soup.find('div', 'serverStatusDataArea')
    for row in status_data.findAll('div', attrs='statusRow'):
        status_label = format_value(row.find('div', attrs='statusLabel').text)
        res = re.search('(\\w+) \((\\d+)\)', status_label)
        status_name = res.group(1)
        status_count = res.group(2)
        system_status[status_name] = status_count

    return system_status, server_list


def format_value(value):
    if isinstance(value, NoneType):
        return ""
    return BeautifulSoup(value, convertEntities=BeautifulSoup.HTML_ENTITIES).__str__().strip() \
        .replace('\xc2', '').replace('\xa0', '')


def get_server_status_result_str(status_list):
    result_str = ""
    c_count = 0
    for h in header_list:
        result_str += ('{0:' + str(column_sizes[c_count]) + '}').format(h) + " "
        c_count += 1
    result_str += '\n'

    for server in status_list:
        c_count = 0
        for h in header_list:
            result_str += ('{0:' + str(column_sizes[c_count]) + '}').format(server[h]) + " "
            c_count += 1
        result_str += '\n'

    return result_str


def get_server_status_as_htlm_table(system_status, status_list, is_succeed):
    response_header = "<!DOCTYPE html>" \
                      "<html>" \
                      "<head>" \
                      "    <style>" \
                      "        table#t01 {" \
                      "            width: 100%;" \
                      "        }" \
                      "        table, th, td {" \
                      "            border: 1px solid black;" \
                      "            border-collapse: collapse;" \
                      "        }" \
                      "        th, td {" \
                      "            padding: 5px;" \
                      "            text-align: left;" \
                      "        }" \
                      "        table tr:nth-child(even) {" \
                      "            background-color: #eee;" \
                      "        }" \
                      "        table tr:nth-child(odd) {" \
                      "            background-color: #fff;" \
                      "        }" \
                      "        table th {" \
                      "            background-color: gray;" \
                      "            color: white;" \
                      "        }" \
                      "    </style>" \
                      "</head>"

    response_body = "<body>"
    response_body_header = "ALL SERVERS RUNNING PROPERLY" if is_succeed else "FAILURE DETECTED ON SOME SERVERS"
    response_body += "<h3>" + response_body_header + "</h3>"

    # system_status Health of Running Servers
    result_table = "<table id=\"t00\">"
    result_table += "<tr>"
    result_table += "<th>" + "System" + "</th>"
    result_table += "<th>" + "Count" + "</th>"
    result_table += "</tr>"

    for status in system_status:
        result_table += "<tr>"
        result_table += "<td>" + status + "</td>"
        result_table += "<td>" + system_status[status] + "</td>"
        result_table += "</tr>"
    result_table += "</table>"

    response_body += "<h4>Health of Running Servers</h4>"
    response_body += result_table + "</br>"

    # status_list
    result_table = "<table id=\"t01\">"
    result_table += "<tr>"
    for h in header_list:
        result_table += "<th>" + h + "</th>"
    result_table += "</tr>"

    for server in status_list:
        result_table += "<tr>"
        for h in header_list:
            result_table += "<td>" + server[h] + "</td>"
        result_table += "</tr>"
    result_table += "</table>"

    response_body += "<h4>Running Server Status</h4>"
    response_body += result_table
    response_body += "</body></html>"

    return response_header + response_body


def has_any_failure(system_status, status_list):
    for status in system_status:
        count = int(system_status[status])
        if status != "OK" and count != 0:
            return False

    key_state = 'State'
    key_health = 'Health'
    for server in status_list:
        if server[key_state] == 'RUNNING' and server[key_health] == 'OK':
            continue
        else:
            return True
    return False


def check_servers():
    response = do_login_and_request_page()
    system_status, server_status_list = get_server_status(response)
    return system_status, server_status_list
