import base64
import os
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

# By default, cache dir is located in $TEMP/scp-temp
__root_dir__ = os.environ.get('TEMP')
__cache_dir__ = 'scp-temp'


class WebService:
    def __init__(self, host):
        self.host = str(host)
        self._endpoints = set()
        self.verify = True
        self.delay = 0.0
        self.consecutive_failures = 0
        self.statistics = {
            'executionTime': 0,
            'numOfRequests': 0,
            'consumedBandwidth': 0
        }

    def list_endpoints(self):
        print(self._endpoints)

    def get_endpoint(self, endp):
        for ep in self._endpoints:
            if endp in [ep.route, ep.title]:
                return ep
        return None

    def connect(self, endp):
        endpoint = self.get_endpoint(endp).connect()
        return do_request(f"{self.host}{endpoint.route}", delay=self.delay,
                          ignore_cache=endpoint.ignore_cache, verify=self.verify, **endpoint.properties)


class Endpoint:
    __HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

    def __init__(self, route, method=__HTTP_METHODS[0]):
        # TODO: Wrapper for params
        # Opt 1. Vanilla string -> 'products': 'products/{productId}?param1=value1&param2=value2'
        # requests.get(f"{self.sec_problems_url}?{'&'.join(_query_params)}", headers=_headers).json()
        # Opt 2. Structured data
        assert method in Endpoint.__HTTP_METHODS, f"Unknown method {method}"
        self.title = ''
        self.route = str(route)
        self.ignore_cache = False
        self.properties = {'method': method}  # Any of requests.request() params (headers, cookies, ...)

    def __repr__(self):
        return f"{self.properties.get('method')} {self.route}"

    def __eq__(self, other):
        return isinstance(other, Endpoint) and self.__dict__ == other.__dict__

    def request_template(self):
        return


def do_request(url, method='GET', delay=0.0, ignore_cache=False, **kwargs) -> Optional[BeautifulSoup]:
    # TODO: handle other types of files (json, xml, binaries ...)
    __MAX_URL_LEN__ = 250
    if len(url) > __MAX_URL_LEN__:
        raise ValueError(f"Max url length exceeded ({len(url)} > {__MAX_URL_LEN__})")
    time.sleep(delay)
    enc = base64.b64encode(url.encode('utf-8')).decode('utf-8')
    os.makedirs(os.path.join(__root_dir__, __cache_dir__), exist_ok=True)
    path = os.path.join(__root_dir__, __cache_dir__, f"{enc}.html")

    # TRY CACHE
    try:
        if ignore_cache:
            print(f"[DEBUG] Ignoring cache")
            raise FileNotFoundError
        with open(path, 'r', encoding='utf-8') as cached:
            print(f"[DEBUG] Cache hit")
            return BeautifulSoup(cached.read(), 'html.parser')
    except FileNotFoundError:
        print(f"[DEBUG] Cache miss")
        _res = requests.request(method, url, **kwargs)
        if _res.status_code not in range(100, 400):
            print(f"[ERROR] Request not successful [{_res.status_code}]\n{_res.text}")
            return None
        _page = BeautifulSoup(_res.text, 'html.parser')
        with open(path, 'w', encoding='utf-8') as dump:
            dump.write(_page.prettify())
        return _page
