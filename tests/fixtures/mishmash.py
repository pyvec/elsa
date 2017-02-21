from flask import Flask


app = Flask('mishmash')


@app.route('/test')
def index():
    return '<html><body>SHOULD NOT WORK</body></html>'


if __name__ == '__main__':
    from elsa import cli
    cli(app, base_url='https://example.org')
