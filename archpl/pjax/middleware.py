import json

from django.http import HttpResponse


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
        content_type = response.get('content-type', None)
        if content_type.startswith('application/json'):
            return response
        if content_type.startswith('text/html'):
            resp['html'] = response.content
        else:
            raise NotImplementedError
        json_response = json.dumps(resp)
        return HttpResponse(json_response,
                content_type='application/json; charset=utf-8')
