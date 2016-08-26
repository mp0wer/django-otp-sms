import urllib2
import urllib
import hashlib
import time
from .base import BaseAdapter, AdapterError


class SMSRuAdapter(BaseAdapter):
    SEND_STATUS = {
        100: "Message accepted",
        201: "Out of money",
        202: "Bad recipient",
        203: "Message text not specified",
        204: "Bad sender (unapproved)",
        205: "Message too long",
        206: "Day message limit reached",
        207: "Can't send messages to that number",
        208: "Wrong time",
        209: "Blacklisted recipient",
    }

    STATUS_STATUS = {
        -1: "Message not found",
        100: "Message is in the queue",
        101: "Message is on the way to the operator",
        102: "Message is on the way to the recipient",
        103: "Message delivered",
        104: "Message failed: out of time",
        105: "Message failed: cancelled by the operator",
        106: "Message failed: phone malfunction",
        107: "Message failed, reason unknown",
        108: "Message declined",
    }

    COST_STATUS = {
        100: "Success"
    }

    def __init__(self, auth):
        super(SMSRuAdapter, self).__init__(auth)
        self._token = None
        self._token_ts = 0
        self.login = auth.get('LOGIN')
        self.password = auth.get('PASSWORD')
        self.key = auth['KEY']

    def _call(self, method, args):
        """Calls a remote method."""
        if not isinstance(args, dict):
            raise ValueError("args must be a dictionary")
        args["api_id"] = self.key

        if method in ("sms/send", "sms/cost"):
            if self.login and self.password:
                args["login"] = self.login
                args["token"] = self._get_token()
                args["sig"] = hashlib.md5(self.password + args["token"]).hexdigest()
                del args["api_id"]

        url = "http://sms.ru/%s?%s" % (method, urllib.urlencode(args))
        # print url
        res = urllib2.urlopen(url).read().strip().split("\n")
        if res[0] == "200":
            raise AdapterError("The supplied API key is wrong")
        elif res[0] == "210":
            raise AdapterError("GET used when POST must have been")
        elif res[0] == "211":
            raise AdapterError("Unknown method")
        elif res[0] == "220":
            raise AdapterError("The service is temporarily unavailable")
        elif res[0] == "301":
            raise AdapterError("Wrong password")
        return res

    def _get_token(self):
        """Returns a token.  Refreshes it if necessary."""
        if self._token_ts < time.time() - 500:
            self._token = None
        if self._token is None:
            self._token = self.token()
            self._token_ts = time.time()
        return self._token

    def send(self, to, message, sender=None, express=False, test=False):
        """Sends the message to the specified recipient.  Returns a numeric
        status code, its text description and, if the message was successfully
        accepted, its reference number."""
        if not isinstance(message, unicode):
            message = unicode(message)
        args = {"to": to, "text": message.encode("utf-8")}
        if sender:
            args["from"] = sender
        if express:
            args["express"] = "1"
        if test:
            args["test"] = "1"
        res = self._call("sms/send", args)
        if res[0] != "100":
            res.append(None)
        return int(res[0]), self.SEND_STATUS.get(int(res[0]), "Unknown status"), res[1]

    def status(self, msgid):
        """Returns message status."""
        res = self._call("sms/status", {"id": msgid})
        code = int(res[0])
        text = self.STATUS_STATUS.get(code, "Unknown status")
        return code, text

    def cost(self, to, message):
        """Prints the cost of the message."""
        res = self._call("sms/cost", {"to": to, "text": message.encode("utf-8")})
        if res[0] != "100":
            res.extend([None, None])
        return int(res[0]), self.COST_STATUS.get(int(res[0]), "Unknown status"), res[1], res[2]

    def balance(self):
        """Returns your current balance."""
        res = self._call("my/balance", {})
        if res[0] == "100":
            return float(res[1])
        raise Exception(res[0])

    def limit(self):
        """Returns the remaining message limit."""
        res = self._call("my/limit", {})
        if res[0] == "100":
            return int(res[1])
        raise Exception(res[0])

    def token(self):
        """Returns a token."""
        return self._call("auth/get_token", {})[0]