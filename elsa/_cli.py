import os
import urllib.parse
import warnings

from flask import Response
import click

from ._deployment import deploy as deploy_
from ._shutdown import ShutdownableFreezer, inject_shutdown


def port_option():
    return click.option(
        '--port', type=int, default=8003,
        help='Port to listen at')


def cname_option():
    return click.option(
        '--cname/--no-cname', default=True,
        help='Whether to create the CNAME file, default is to create it')


def path_option(app):
    return click.option(
        '--path', default=os.path.join(app.root_path, '_build'),
        help='Input path, default _build')


def freeze_app(app, freezer, path, base_url):
    if not base_url:
        raise click.UsageError('No base URL provided, use --base-url')
    print('Generating HTML...')
    app.config['FREEZER_DESTINATION'] = path
    app.config['FREEZER_BASE_URL'] = base_url
    app.config['SERVER_NAME'] = urllib.parse.urlparse(base_url).netloc
    # make sure the warnings are treated as errors
    warnings.simplefilter('error')
    freezer.freeze()


def inject_cname(app):
    """Create CNAME route for GitHub pages"""
    @app.route('/CNAME')
    def cname():
        return Response(app.config['SERVER_NAME'],
                        mimetype='application/octet-stream')


def cli(app, *, freezer=None, base_url=None):
    """Get a cli() function for provided app"""
    if not freezer:
        freezer = ShutdownableFreezer(app)

    @click.group(context_settings=dict(help_option_names=['-h', '--help']),
                 help=__doc__)
    def command():
        pass

    @command.command()
    @port_option()
    @cname_option()
    def serve(port, cname):
        """Run a debug server"""

        # Workaround for https://github.com/pallets/flask/issues/1907
        auto_reload = app.config.get('TEMPLATES_AUTO_RELOAD')
        if auto_reload or auto_reload is None:
            app.jinja_env.auto_reload = True

        inject_shutdown(app)
        if cname:
            inject_cname(app)

        app.run(host='0.0.0.0', port=port, debug=True)

    @command.command()
    @path_option(app)
    @click.option('--base-url', default=base_url,
                  help='URL for the application, used for external links, ' +
                  ('default {}'.format(base_url) if base_url else 'mandatory'))
    @click.option('--serve/--no-serve',
                  help='After building the site, run a server with it')
    @port_option()
    @cname_option()
    def freeze(path, base_url, serve, port, cname):
        """Build a static site"""
        if cname:
            inject_cname(app)

        freeze_app(app, freezer, path, base_url)

        if serve:
            freezer.serve(port=port)

    @command.command()
    @path_option(app)
    @click.option('--base-url', default=base_url,
                  help='URL for the application, used for external links, ' +
                  ('default {}'.format(base_url) if base_url else 'mandatory'
                   ' with --freeze'))
    @click.option('--push/--no-push', default=None,
                  help='Whether to push the gh-pages branch, '
                  'deprecated default is to push')
    @click.option('--freeze/--no-freeze', default=True,
                  help='Whether to freeze the site before deploying, '
                  'default is to freeze')
    @cname_option()
    def deploy(path, base_url, push, freeze, cname):
        """Deploy the site to GitHub pages"""
        if push is None:
            warnings.simplefilter('always')
            msg = ('Using deploy without explicit --push/--no-push is '
                   'deprecated. Assuming --push for now. In future versions '
                   'of elsa, the deploy command will not push to the remote '
                   'server by default. Use --push explicitly to maintain '
                   'current behavior.')
            warnings.warn(msg, DeprecationWarning)
            push = True
        if freeze:
            if cname:
                inject_cname(app)
            freeze_app(app, freezer, path, base_url)

        deploy_(path, push=push)

    return command()
