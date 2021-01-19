from __future__ import print_function

import os
import json
import argparse
from pprint import pformat
from twisted.internet.task import react
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from twisted.internet import task, defer


parser = argparse.ArgumentParser(description="""
Exchange currencyscoop script.
This script helps you to convert one currency to another using the 
currencyscoop.com API. Can show all affordable currencies you can make a 
convertion from/to. Can make a convertion of desired amount from the base
currency to the chosen currency you would like to convert.
""")


class ConvertAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            setattr(namespace, self.dest, values)


parser.add_argument('-a', '--all', action='store_true',
                    help='shows all the currencies')
parser.add_argument('-c', '--convert', nargs=3, action=ConvertAction,
                    metavar=('BASE', 'TO', 'AMOUNT'),
                    help="""
                    converts the base currency amount to the currency you would
                     like to convert and shows the amount. Takes three 
                     additional arguments: 'BASE', 'TO', 'AMOUNT'
                     """)


args = parser.parse_args()

with open(os.path.join("./.api_key")) as fpin:
    api_key = fpin.read().strip()


if args.convert:
    base, to, amount = args.convert
    url = 'https://api.currencyscoop.com/v1/convert?api_key={}&base={}&to={}&amount={}'.format(
        api_key, base, to, amount)

    def callback_request(response):
        agent_reactor = readBody(response)
        agent_reactor.addCallback(callback_body)
        return agent_reactor

    def callback_body(body):
        data = json.loads(body)
        curr_from = data['response']['from']
        curr_to = data['response']['to']
        amount = data['response']['amount']
        value = data['response']['value']
        response_phrase = "{} {} is equal to {} {}"
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(response_phrase.format(amount, curr_from, value, curr_to))
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')

    def main(reactor, url=url):
        agent = Agent(reactor)
        agent_reactor = agent.request(
            b'GET', url,
            Headers({'User-Agent': ['Twisted Web Client Example']}),
            None)
        agent_reactor.addCallback(callback_request)
        return agent_reactor

    react(main)


if args.all:
    url = 'https://api.currencyscoop.com/v1/currencies?api_key={}'.format(
        api_key)

    def callback_request(response):
        agent_reactor = readBody(response)
        agent_reactor.addCallback(callback_body)
        return agent_reactor

    def callback_body(body):
        data = json.loads(body)
        curr_fiats = data['response']['fiats']
        for key, value in curr_fiats.items():
            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(key, value['countries'])
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')

    def main(reactor, url=url):
        agent = Agent(reactor)
        agent_reactor = agent.request(
            b'GET', url,
            Headers({'User-Agent': ['Twisted Web Client Example']}),
            None)
        agent_reactor.addCallback(callback_request)
        return agent_reactor

    react(main)
