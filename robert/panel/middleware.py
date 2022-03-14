from werkzeug.wrappers import Request, Response, ResponseStream


class Middleware:
    def __init__(self, app):
        self.app = app

        self.admin_tokens = ['root-test']
        self.user_tokens = ['root-test', 'sami']

    def __call__(self, environ, start_response):
        request = Request(environ)

        token = request.headers.get('Authorization')

        if token in self.user_tokens:
            return self.app(environ, start_response)
        else:
            res = Response('Unauthorized', status=401)
            return res(environ, start_response)
