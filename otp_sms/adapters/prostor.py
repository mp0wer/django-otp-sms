# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import urllib2
import urllib
from .base import BaseAdapter, AdapterError


class ProstorAdapter(BaseAdapter):
    base_url = 'http://api.prostor-sms.ru/messages/v2'

    def __init__(self, auth):
        self.login = auth['LOGIN']
        self.password = auth['PASSWORD']

    def _send_request(self, uri, params=None):
        url = self._get_url(uri, params)
        request = urllib2.Request(url)
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, self.login, self.password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        try:
            opener = urllib2.build_opener(authhandler)
            data = opener.open(request).read()
            return data
        except IOError, e:
            raise AdapterError(e.code)

    def _get_url(self, uri, params=None):
        url = "%s/%s/" % (self.base_url, uri)
        param_str = ''
        if params is not None:
            for k, v in params.items():
                if v is None:
                    del params[k]
                if isinstance(v, unicode):
                    params[k] = v.encode('utf-8')
            param_str = urllib.urlencode(params)
        if param_str:
            return "%s?%s" % (url, param_str)
        return url

    def send(self, phone, text, sender=None, status_queue_name=None, schedule_time=None, wap_url=None):
        """Sending sms """
        senders = self.senders()
        if not sender and senders:
            sender = senders[0]
        elif sender not in senders:
            raise AdapterError('Sender %s is not available' % sender)

        params = {'phone': phone, 'text': text, 'sender': sender, 'statusQueueName': status_queue_name,
                  'scheduleTime': schedule_time, 'wapurl': wap_url}
        answer = self._send_request('send', params)

        if not answer.startswith('accepted'):
            raise AdapterError(answer)

    def status(self, id):
        """Retrieve sms status by it's id """
        params = {'id': id}
        return self._send_request('status', params)

    def status_queue(self, status_queue_name, limit=5):
        """Retrieve latest statuses from queue """
        params = {'statusQueueName': status_queue_name, 'limit': limit}
        return self._send_request('statusQueue', params)

    def credits(self):
        """Retrieve current credit balance """
        return self._send_request('credits')

    def senders(self):
        """Retrieve available signs """
        answer = self._send_request('senders')
        lines = answer.splitlines()
        senders = []
        for line in lines:
            name, status = line.split(';')[:2]
            if status in ('active', 'default'):
                senders.append(name)
        return senders