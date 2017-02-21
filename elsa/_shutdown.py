from flask import request
from flask_frozen import Freezer


PATH = '/__shutdown__/'


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def shutdown_response():
    shutdown_server()
    return 'Server shutting down...'


def inject_shutdown(app):
    """Create a shutdown route in given app"""
    @app.route(PATH, methods=['POST'])
    def shutdown():
        return shutdown_response()


class ShutdownableFreezer(Freezer):
    """
    Like Freezer from Frozen-Flask, but can be shut down while serving
    via HTTP POST
    """
    def make_static_app(self):
        app = super().make_static_app()
        old_dispatch_request = app.dispatch_request

        def dispatch_request():
            if request.path == PATH and request.method == 'POST':
                return shutdown_response()
            return old_dispatch_request()

        app.dispatch_request = dispatch_request
        return app
