import os
import urllib.parse

from flask_frozen import Freezer
import click

from ._deployment import deploy as deploy_


def freeze_app(app, freezer, path, base_url):
    if not base_url:
        raise click.UsageError('No base URL provided, use --base-url')
    print('Generating HTML...')
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
                  help='Output path, default _build')
    @click.option('--base-url', default=base_url,
                  help='URL for the application, used for external links, ' +
                  ('default {}'.format(base_url) if base_url else 'mandatory'))
    @click.option('--serve/--no-serve',
                  help='After building the site, run a server with it')
    @click.option('--port', default=8003,
                  help='Port used for --serve, default 8003')
    def freeze(path, base_url, serve, port):
        """Build a static site"""
        freeze_app(app, freezer, path, base_url)
        if serve:
            freezer.serve(port=port)

    @command.command()
    @click.option('--path', default=os.path.join(app.root_path, '_build'),
                  help='Input path, default _build')
    @click.option('--base-url', default=base_url,
                  help='URL for the application, used for external links, ' +
                  ('default {}'.format(base_url) if base_url else 'mandatory'
                   ' with --freeze'))
    @click.option('--push/--no-push', default=True,
                  help='Whether to push the gh-pages branch, '
                  'default is to push')
    @click.option('--freeze/--no-freeze', default=True,
                  help='Whether to freeze the site before deploying, '
                  'default is to freeze')
    def deploy(path, base_url, push, freeze):
        """Deploy the site to GitHub pages"""
        if freeze:
            freeze_app(app, freezer, path, base_url)
        deploy_(path, push=push)

    return command()
