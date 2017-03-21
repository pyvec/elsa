import warnings

from flask import Flask


app = Flask('warning')


@app.route('/')
def index():
    warnings.warn('test', PendingDeprecationWarning)
    return '<html><body>SUCCESS</body></html>'


if __name__ == '__main__':
    from elsa import cli
    cli(app, base_url='https://example.org')
