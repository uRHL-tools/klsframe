import requests


class APIworker:
    def __init__(self, methods, ):
        __HTTP_METHODS__ = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']
        if methods is None:
            methods = ['GET']
        self.consecutive_failures = 0
        self.statistics = {
            'executionTime': 0,
            'numOfRequests': 0,
            'consumedBandwidth': 0
        }
        self._allowed_methods = methods
        self.force_https = False
        self.base_url = 'https://blabla.com'
        self.endpoints = {
            'cart': 'cart',
            'products': 'products/{productId}?param1=value1&param2=value2'
        }
        # TODO: Wrapper for params
        # Opt 1. Vanilla string -> 'products': 'products/{productId}?param1=value1&param2=value2'
        # requests.get(f"{self.sec_problems_url}?{'&'.join(_query_params)}", headers=_headers).json()
        # Opt 2. Structured data
        endpoints = [
            {
                'endpoint': 'entities',
                'method': 'GET',
                'path_params': {
                    'entityID'
                },
                'request_params': {
                    'param1': 'value1',
                    'param2': 'value2'
                }
            },
            {
                'endpoint': 'securityProblems',
                'path_params': {
                    'entityID'
                },
                'request_params': {
                    'param1': 'value1',
                    'param2': 'value2'
                }
            }
        ]


    def request(self, url, method='GET', params=None, headers=None, cookies=None):
        # TODO: develop enconde params and url
        # TODO: review authentication, files... and the rest of parameters
        req_args = {'method': method, 'url': url, 'params': params, 'headers': headers, 'cookies': cookies}
        if method in self._allowed_methods:
            response = requests.request(**req_args)
        else:
            raise requests.HTTPError(f"Invalid request method {method}. Allowed: {', '.join(self._allowed_methods)}")

        if response.status_code == 200:
            return response
        else:
            raise requests.HTTPError(f'Unexpected status code ({response.status_code}) for the request {req_args}')
