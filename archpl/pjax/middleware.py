import json
import re

from django.http import HttpResponse


BODY_RX = re.compile(r'<body>(.*?)</body>', re.MULTILINE|re.DOTALL|re.UNICODE)
HEAD_RX = re.compile(r'<head>(.*?)</head>', re.MULTILINE|re.DOTALL|re.UNICODE)
COMPRESSOR = re.compile(r'\s+', re.MULTILINE)


class AsPJAX(object):
    def process_response(self, request, response):
        if request.REQUEST.get('pjax', None):
            return self.as_ajax(request, response)
        return response

    def as_ajax(self, request, response):
        resp = {
            'status': 'ok',
            'code': response.status_code,
        }
        if response.status_code == 302:
            resp['location'] = response.get('Location')
            return response_as_json(resp)

        content = response.content
        content_type = response.get('content-type', None)
        if content_type.startswith('application/json'):
            return response
        if content_type.startswith('text/html'):
            resp['html'] = {
                'body': _extract(BODY_RX, content),
                'head': _extract(HEAD_RX, content),
            }
        else:
            raise NotImplementedError
        return response_as_json(resp)


def response_as_json(resp):
    json_response = json.dumps(resp)
    return HttpResponse(json_response,
            content_type='application/json; charset=utf-8')

def _extract(rx, html):
    try:
        sre = rx.finditer(html).next()
    except StopIteration:
        return None
    if not sre:
        return None
    data = sre.group()
    compressed_data = COMPRESSOR.sub(' ', data)
    return compressed_data
