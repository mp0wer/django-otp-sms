# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import urllib2
import urllib
import hashlib
import time
from django.utils.translation import ugettext_lazy as _
from .base import BaseAdapter, AdapterError


class SMSRuAdapter(BaseAdapter):
    BASE_URL = 'https://sms.ru'

    ANSWER_STATUS = {
        -1: _("Message not found"),
        100: _("Message is in the queue"),
        101: _("Message is on the way to the operator"),
        102: _("Message is on the way to the recipient"),
        103: _("Message delivered"),
        104: _("Message failed: out of time"),
        105: _("Message failed: cancelled by the operator"),
        106: _("Message failed: phone malfunction"),
        107: _("Message failed: unknown reason"),
        108: _("Message declined"),
        130: _("Message failed: exceeded limit of messages to this number per day"),
        131: _("Message failed: exceeded limit of identical messages to this number per minute"),
        132: _("Message failed: exceeded limit of identical messages to this number per day"),

        200: _("The supplied API key is wrong"),
        201: _("Out of money"),
        202: _("Bad recipient"),
        203: _("Message text not specified"),
        204: _("Bad sender (unapproved)"),
        205: _("Message too long"),
        206: _("Day message limit reached"),
        207: _("Can't send messages to that number"),
        208: _("Wrong time"),
        209: _("Blacklisted recipient"),
        210: _("GET used when POST must have been"),
        211: _("Unknown method"),
        212: _("Text must be in UTF-8"),
        220: _("The service is temporarily unavailable"),
        230: _("Exceeded limit of messages per day"),
        231: _("Exceeded limit of identical messages per minute"),
        232: _("Exceeded limit of identical messages per day"),
        300: _("Invalid token"),
        301: _("Wrong password"),
        302: _("User authenticated, but not confirmed"),
    }

    def __init__(self, auth):
        super(SMSRuAdapter, self).__init__(auth)
        self._token = None
        self._token_ts = 0
        self.login = auth.get('LOGIN')
        self.password = auth.get('PASSWORD')
        self.key = auth['KEY']

    def _call_raw(self, method, args={}):
        """Calls a remote method."""
        if not isinstance(args, dict):
            raise ValueError("args must be a dictionary")
        args["api_id"] = self.key

        if method in ("sms/send", "sms/cost") and self.login and self.password:
            args["login"] = self.login
            args["token"] = self._get_token()
            args["sig"] = hashlib.md5(self.password + args["token"]).hexdigest()
            del args["api_id"]

        url = "%s/%s?%s" % (self.BASE_URL, method, urllib.urlencode(args))
        try:
            res = urllib2.urlopen(url).read()
        except IOError as e:
            raise AdapterError(e.message)
        return res

    def _call(self, method, args={}):
        res = self._call_raw(method, args)
        res = res.strip().split("\n")

        code, params = res[0], res[1:]
        code = int(code)

        if code not in self.ANSWER_STATUS:
            raise AdapterError(_("Unknown status"))

        if code >= 200:
            raise AdapterError(self.ANSWER_STATUS[code])

        return code, params

    def _get_token(self):
        """Returns a token.  Refreshes it if necessary."""
        if self._token_ts < time.time() - 500:
            self._token = None
        if self._token is None:
            self._token = self.token()
            self._token_ts = time.time()
        return self._token

    def send(self, to, text, sender=None, translit=False, test=False):
        """Sends the message to the specified recipient.  Returns a numeric
        status code, its text description and, if the message was successfully
        accepted, its reference number."""
        if not isinstance(text, unicode):
            text = unicode(text)
        args = {"to": to, "text": text.encode("utf-8")}
        if sender:
            args["from"] = sender
        if translit:
            args["translit"] = "1"
        if test:
            args["test"] = "1"

        code, message_ids = self._call("sms/send", args)
        return message_ids[0]

    def status(self, msgid):
        """Returns message status."""
        code, params = self._call("sms/status", {"id": msgid})
        return self.STATUS_STATUS[code]

    def cost(self, to, message):
        """Prints the cost of the message."""
        code, (cost, length) = self._call("sms/cost", {"to": to, "text": message.encode("utf-8")})
        return cost, length

    def balance(self):
        """Returns your current balance."""
        code, (balance,) = self._call("my/balance")
        return float(balance)

    def limit(self):
        """Returns the remaining message limit."""
        code, (day_limit, sended) = self._call("my/limit")
        return int(day_limit) - int(sended)

    def token(self):
        """Returns a token."""
        return self._call_raw("auth/get_token")