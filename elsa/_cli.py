import os
import urllib.parse

from flask_frozen import Freezer
import click


def freeze_app(app, freezer, path, base_url):
    app.config['FREEZER_DESTINATION'] = path
    app.config['FREEZER_BASE_URL'] = base_url
    app.config['SERVER_NAME'] = urllib.parse.urlparse(base_url).netloc
    freezer.freeze()


def cli(app, *, freezer=None, base_url=None):
    """Get a cli() function for provided app"""
    if not freezer:
        freezer = Freezer(app)

    @click.group(context_settings=dict(help_option_names=['-h', '--help']),
                 help=__doc__)
    def command():
        pass

    @command.command()
    @click.option('--port', type=int, default=8003,
                  help='Port to listen at')
    def serve(port):
        """Run a debug server"""
        app.run(host='0.0.0.0', port=port, debug=True)

    @command.command()
    @click.option('--path', default=os.path.join(app.root_path, '_build'),
                  help='Output path')
    @click.option('--base-url', default=base_url,
                  help='URL for the application, used for external links, ' +
                  ('default {}'.format(base_url) if base_url else 'mandatory'))
    @click.option('--serve/--no-serve',
                  help='After building the site, run a server with it')
    @click.option('--port', default=8003,
                  help='Port used for --serve, default 8003')
    def freeze(path, base_url, serve, port):
        """Build a static site"""
        if not base_url:
            raise click.UsageError('No base URL provided, use --base-url')
        freeze_app(app, freezer, path, base_url)
        if serve:
            freezer.serve(port=port)

    return command()
