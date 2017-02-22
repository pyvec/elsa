import os
import shutil
import subprocess
import sys
from contextlib import contextmanager

import pytest
import requests


FIXTURES = 'tests/fixtures'

SCRIPT = 'website.py'
BUILDDIR = '_build'
INDEX = os.path.join(BUILDDIR, 'index.html')
CNAME = os.path.join(BUILDDIR, 'CNAME')

SCRIPT_FIXTURES = os.path.join(FIXTURES, SCRIPT)
BUILDDIR_FIXTURES = os.path.join(FIXTURES, BUILDDIR)
INDEX_FIXTURES = os.path.join(FIXTURES, INDEX)
CNAME_FIXTURES = os.path.join(FIXTURES, CNAME)


def parametrized_fixture(*args, **kwargs):
    @pytest.fixture(scope='module', params=args + tuple(kwargs.keys()))
    def fixture(request):
        if request.param in kwargs:
            return kwargs[request.param]
        return request.param
    return fixture


def is_true(option: str) -> bool:
    '''
    Whether the given command line option means true (i.e. it is not --no-*)
    '''
    return not option.startswith('--no-')


cname = parametrized_fixture(cname='--cname', no_cname='--no-cname')
push = parametrized_fixture(push='--push', no_push='--no-push')
serve_command = parametrized_fixture(serve=['serve'],
                                     freeze_serve=['freeze', '--serve'])
port = parametrized_fixture(8001, 8080)
domain = parametrized_fixture('foo.bar', 'spam.eggs')
protocol = parametrized_fixture('http', 'https')


def run_cmd(cmd, **kwargs):
    """Same as ``subprocess.run``, but with more appropriate defaults"""
    kwargs.setdefault('check', True)
    kwargs.setdefault('timeout', 15)
    kwargs.setdefault('stdout', subprocess.PIPE)
    return subprocess.run(cmd, **kwargs)


class CommandFailed(Exception):
    """Raised when a command fails"""
    # We use a custom exception because subprocess.CalledProcessError can't
    # be raised from a completed Popen object. If that were possible
    # (in a documented way), CalledProcessError would be a better choice.


class ElsaRunner:
    '''
    Class for elsa fixture enabling blocking or background runs

    If there is a local website.py in pwd, uses that one,
    uses the one from fixtures instead.
    '''
    def run(self, *command, script=None):
        print('COMMAND: python website.py', *command)
        try:
            cr = subprocess.run(
                self.create_command(command, script), check=True,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            raise CommandFailed('return code was {}'.format(e.returncode))
        cr.stderr = cr.stderr.decode('utf-8')
        sys.stderr.write(cr.stderr)
        return cr

    @contextmanager
    def run_bg(self, *command, script=None):
        print('COMMAND IN BACKGROUND: python website.py', *command)
        port = self.parse_port(command)
        proc = subprocess.Popen(self.create_command(command, script),
                                stderr=subprocess.PIPE,
                                universal_newlines=True)

        # Wait for the server to start,
        # i.e. wait for the first line on stderr:
        #  * Running on http://127.0.0.1:8003/ (Press CTRL+C to quit)
        sys.stderr.write(proc.stderr.readline())
        # With the serve command, Flask is running in debug and restarts
        # the server, so we'll also wait for next line:
        #  * Restarting with stat
        if command[0] == 'serve':
            sys.stderr.write(proc.stderr.readline())

        yield proc

        try:
            # Shutdown the server via POST request
            url = 'http://localhost:{}/__shutdown__/'.format(port)
            print('Shutting down via', url)
            requests.post(url)
        except Exception as e:
            print(e)

        try:
            _, errs = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            _, errs = proc.communicate()
        sys.stderr.write(errs)

        # werkzeug.server.shutdown does:
        # * 247 on debug
        # * 0 on non-debug
        # * 15 on Windows
        if proc.returncode not in (0, 15, 247):
            raise CommandFailed('return code was {}'.format(proc.returncode))

    def finalize(self):
        self.lax_rmtree(BUILDDIR_FIXTURES)

    @classmethod
    def create_command(cls, command, script):
        script = script or SCRIPT
        if os.path.exists(script):
            script = script
        else:
            script = os.path.join(FIXTURES, script)
        command = tuple(str(item) for item in command)
        return (sys.executable, script) + command

    @classmethod
    def parse_port(cls, command):
        if '--port' in command:
            return int(command[command.index('--port') + 1])
        return 8003

    @classmethod
    def lax_rmtree(cls, path):
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass


@pytest.fixture
def elsa():
    er = ElsaRunner()
    try:
        yield er
    finally:
        er.finalize()


def commit_info():
    cmd = ['git', '--no-pager', 'show', 'gh-pages', '--no-color']
    commit = run_cmd(cmd).stdout.decode('utf-8').strip()
    print(commit)
    return commit


def assert_commit_author(commit):
    assert 'Author: Tester Example <tester@example.org>' in commit


def was_pushed(branch='gh-pages'):
    cmd = ['git', 'rev-parse', branch]
    local = run_cmd(cmd).stdout.decode('utf-8').strip()
    cmd = ['git', 'rev-parse', 'origin/{}'.format(branch)]
    result = run_cmd(cmd, check=False)
    if result.returncode == 128:
        remote = None
    else:
        result.check_returncode()
    remote = result.stdout.decode('utf-8').strip()
    return remote == local


@pytest.fixture
def gitrepo(tmpdir):
    '''
    This fixture creates a git repository with website.py in tmpdir
    '''
    repo = tmpdir.mkdir('repo')
    bare = tmpdir.mkdir('bare')
    script = repo.join(SCRIPT)
    with open(SCRIPT_FIXTURES) as f:
        script.write(f.read())
    with bare.as_cwd():
        run_cmd(['git', 'init', '--bare'])
    with repo.as_cwd():
        run_cmd(['git', 'init'])
        run_cmd(['git', 'add', SCRIPT])
        run_cmd(['git', 'config', 'user.email', 'tester@example.org'])
        run_cmd(['git', 'config', 'user.name', 'Tester Example'])
        run_cmd(['git', 'remote', 'add', 'origin', str(bare)])
        run_cmd(['git', 'commit', '-m', 'Initial commit'])
        yield repo


def test_elsa_fixture_bad_exit_status(elsa):
    with pytest.raises(CommandFailed):
        elsa.run('not', 'a', 'chance')


def test_elsa_fixture_bad_exit_status_bg(elsa):
    with pytest.raises(CommandFailed):
        with elsa.run_bg('not', 'a', 'chance'):
            pass


def test_serve(elsa):
    with elsa.run_bg('serve'):
        assert 'SUCCESS' in requests.get('http://localhost:8003/').text


def test_port(elsa, port, serve_command):
    with elsa.run_bg(*serve_command, '--port', port):
        url = 'http://localhost:{}/'.format(port)
        assert 'SUCCESS' in requests.get(url).text


def test_cname(elsa, cname, serve_command):
    code = 200 if is_true(cname) else 404

    with elsa.run_bg(*serve_command, cname):
        assert requests.get('http://localhost:8003/CNAME').status_code == code


def test_freeze(elsa):
    elsa.run('freeze')
    with open(INDEX_FIXTURES) as f:
        assert 'SUCCESS' in f.read()


def test_freeze_mishmash(elsa):
    with pytest.raises(CommandFailed):
        # This script has a mime type mishmash
        elsa.run('freeze', script='mishmash.py')


def test_freeze_cname(elsa):
    elsa.run('freeze')
    with open(CNAME_FIXTURES) as f:
        assert f.read().strip() == 'example.org'


def test_freeze_no_cname(elsa):
    elsa.run('freeze', '--no-cname')
    assert not os.path.exists(CNAME_FIXTURES)


def test_freeze_base_url(elsa, protocol, domain):
    url = '{}://{}'.format(protocol, domain)
    elsa.run('freeze', '--base-url', url)
    with open(CNAME_FIXTURES) as f:
        assert f.read().strip() == domain


def test_freeze_serve(elsa):
    with elsa.run_bg('freeze', '--serve'), open(INDEX_FIXTURES) as f:
        assert 'SUCCESS' in f.read()
        assert 'SUCCESS' in requests.get('http://localhost:8003/').text


def test_freeze_path(elsa, tmpdir, cname):
    path = tmpdir.join('foo')
    elsa.run('freeze', '--path', path, cname)

    assert path.check(dir=True)
    assert path.join('index.html').check(file=True)
    assert is_true(cname) == path.join('CNAME').check()


def test_deploy_files(elsa, cname, push, gitrepo):
    elsa.run('deploy', cname, push)
    with open(INDEX) as f:
        assert 'SUCCESS' in f.read()
    assert is_true(cname) == os.path.exists(CNAME)


def test_deploy_git(elsa, cname, push, gitrepo):
    elsa.run('deploy', cname, push)
    commit = commit_info()

    assert '.nojekyll' in commit
    assert 'index.html' in commit
    assert 'SUCCESS' in commit
    assert is_true(cname) == ('CNAME' in commit)
    assert_commit_author(commit)
    assert is_true(push) == was_pushed()


def test_deploy_without_explicit_push_switch(elsa, gitrepo):
    completed = elsa.run('deploy')
    assert 'deprecated' in completed.stderr
    assert was_pushed()


@pytest.mark.parametrize('path', ('custom_path', 'default_path'))
def test_freeze_and_deploy(elsa, tmpdir, path, gitrepo):
    freeze_command = ['freeze']
    deploy_command = ['deploy', '--no-push']
    if path == 'custom_path':
        path = tmpdir.join('foo')
        args = ['--path', path]
        freeze_command += args
        deploy_command += args

    elsa.run(*freeze_command)
    elsa.run(*deploy_command)

    commit = commit_info()
    assert 'SUCCESS' in commit
    assert_commit_author(commit)
