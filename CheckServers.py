# CheckServers.py
#
# Main application
#
# @author   Orhun Dalabasmaz
# @since    Dec, 2015

import sys
import time

from ConnectionService import *
from MailService import *

on_fail_only = True


def do_check_servers(on_fail):
    system_status, server_status_list = check_servers()
    is_succeed = not has_any_failure(system_status, server_status_list)
    status_list_str = get_server_status_result_str(server_status_list)
    result_html_content = get_server_status_as_htlm_table(system_status, server_status_list, is_succeed)
    print status_list_str
    if is_succeed:
        print 'EVERYTHING IS OK!'
        if not on_fail:
            print 'sending email'
            send_success_mail(result_html_content)
        else:
            print 'skipping email'
    else:
        print 'HOUSTON WE HAVE A PROBLEM!'
        send_failure_mail(result_html_content)


def init():
    global on_fail_only
    if len(sys.argv) == 1:
        print 'No argument. Acceptable arguments: {onFailOnly}'
    elif len(sys.argv) == 2:
        param = sys.argv[1]
        print param
        if param.startswith("onFailOnly="):
            value = param.split("=")[1]
            on_fail_only = value != "False"
        else:
            print 'Acceptable arguments: {onFailOnly}'
    else:
        print 'At most 1 argument is acceptable.'


if __name__ == '__main__':
    print 'Checking servers... [Datetime: ', time.strftime("%d/%m/%Y %H:%M:%S"), "]"
    init()
    do_check_servers(on_fail_only)
