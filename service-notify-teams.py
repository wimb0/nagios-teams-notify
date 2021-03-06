#!/usr/bin/env python3
#
#
# Author: Isaac J. Galvan
# Date: 2018-12-04
# https://github.com/isaac-galvan
#
# Enhanced by: Wim Baars
# Date: 2020-07-01
# https://github.com/wimb0/nagios-teams-notify
#

import argparse
import json
import requests
import sys
import socket


def format_servicelinks(host_name, service=''):
    # replace spaces with '+'
    service_link = str.replace(service, ' ', '+')
    return 'https://%s/nagiosxi/includes/components/xicore/status.php?show=servicedetail&host=%s&service=%s' % (socket.gethostname(), host_name, service_link)


def create_message(url, notification_type, host_name, host_alias, service, alert, output, long_message=None):
    ''' creates a dict with for the MessageCard '''
    message = {}

    message['summary'] = '%s: %s on %s (%s) is %s' % (
        notification_type, service, host_name, host_alias, alert)
    message['title'] = '%s: %s on %s (%s) is %s' % (
        notification_type, service, host_name, host_alias, alert)
    message['text'] = output

    if alert == 'WARNING':
        color = 'FFFF00'
    elif alert == 'CRITICAL':
        color = 'FF0000'
    elif alert == 'OK':
        color = '00FF00'
    elif alert == 'UNKNOWN':
        color = 'FF7F00'
    else:
        color = '808080'

    message['themeColor'] = color

    # if not long_message is None:
    if long_message:
        message['text'] += '\n\n%s' % (long_message)

    service_link = format_servicelinks(host_name, service)
    action = [{
        '@context': 'http://schema.org',
        '@type': 'ViewAction',
        "name": "View",
        "target": [service_link]
    }]
    message['@type'] = 'MessageCard'
    #message['@type'] = 'ActionCard'
    message['@context'] = 'https://schema.org/extensions'
    if notification_type != 'ACKNOWLEDGEMENT':
        message['potentialAction'] = action

    return message


def send_to_teams(url, message_json):
    """ posts the message to the ms teams webhook url """
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=message_json, headers=headers)
    if r.status_code == requests.codes.ok:
        print('success')
        return True
    else:
        print('failure')
        return False


def main(args):

    # verify url
    url = args.get('url')
    if url is None:
        # error no url
        print('error no url')
        exit(2)

    host_name = args.get('host_name')
    host_alias = args.get('host_alias')
    notification_type = args.get('type')
    service = args.get('service')
    alert = args.get('alert')
    output = args.get('output')
    long_message = args.get('long_message')

    message_dict = create_message(
        url, notification_type, host_name, host_alias, service, alert, output, long_message)
    message_json = json.dumps(message_dict)

    send_to_teams(url, message_json)


if __name__ == '__main__':
    args = {}

    parser = argparse.ArgumentParser()
    parser.add_argument('type', action='store', help='notification type')
    parser.add_argument('host_name', action='store', help='host_name')
    parser.add_argument('host_alias', action='store', help='host_alias')
    parser.add_argument('service', action='store', help='service description')
    parser.add_argument('alert', action='store', help='warning, crit, or ok')
    parser.add_argument('output', action='store', help='output of the check')
    parser.add_argument('url', action='store',
                        help='teams connector webhook url')

    parsedArgs = parser.parse_args()

    args['type'] = parsedArgs.type
    args['host_name'] = parsedArgs.host_name
    args['host_alias'] = parsedArgs.host_alias
    args['service'] = parsedArgs.service
    args['alert'] = parsedArgs.alert
    args['url'] = parsedArgs.url
    args['output'] = parsedArgs.output

    if not sys.__stdin__.isatty():
        args['long_message'] = sys.__stdin__.read()
        pass

    main(args)
