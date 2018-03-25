import click
from flask import Flask


app = Flask('custom_command')


@app.route('/')
def index():
    return '<html><body>SUCCESS</body></html>'


if __name__ == '__main__':
    from elsa import cli
    elsa = cli(app, base_url='https://example.org', invoke_cli=False)

    @elsa.command()
    def custom_command():
        click.echo("Custom command")

    elsa()
