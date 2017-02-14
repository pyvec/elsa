import os
import signal
import shutil
import subprocess
import sys
import time

import pytest
import requests
import sh


FIXTURES = 'tests/fixtures'
WEBSITE = os.path.join(FIXTURES, 'website.py')
BUILDDIR = os.path.join(FIXTURES, '_build')
INDEX = os.path.join(BUILDDIR, 'index.html')
CNAME = os.path.join(BUILDDIR, 'CNAME')


def parametrized_fixture(*args, **kwargs):
    @pytest.fixture(scope='module', params=args + tuple(kwargs.keys()))
    def fixture(request):
        if request.param in kwargs:
            return kwargs[request.param]
        return request.param
    return fixture


class Cname(str):
    '''
    Helper class that is str, but has different truthfulness
    '''
    def __bool__(self):
        return self == ' --cname'


cname = parametrized_fixture(cname=Cname(' --cname'),
                             no_cname=Cname(' --no-cname'))
serve_command = parametrized_fixture('serve', freeze_serve='freeze --serve')
port = parametrized_fixture(8001, 8080)
domain = parametrized_fixture('foo.bar', 'spam.eggs')
protocol = parametrized_fixture('http', 'https')


class ElsaRunner:
    '''
    Class for elsa fixture enabling multiple runs and exit status check
    '''
    def __init__(self):
        self.runs = []

    def run(self, command):
        print('COMMAND: python website.py', command)
        proc = subprocess.Popen([sys.executable, WEBSITE] + command.split())
        if 'serve' in command:
            time.sleep(1)
        else:
            proc.communicate()
        self.runs.append((proc, command))

    def finalize(self):
        try:
            for proc, command in self.runs:
                proc.terminate()
                if 'serve' in command:
                    proc.communicate()
                assert (proc.returncode == 0 or
                        proc.returncode == -signal.SIGTERM)
        finally:
            self.lax_rmtree(BUILDDIR)
            self.lax_rmbranch('gh-pages')

    @classmethod
    def lax_rmtree(cls, path):
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass

    @classmethod
    def lax_rmbranch(cls, branch):
        try:
            sh.git.branch('-D', branch)
        except sh.ErrorReturnCode_1:
            pass


@pytest.fixture
def elsa():
    er = ElsaRunner()
    try:
        yield er.run
    finally:
        er.finalize()


def commit_info():
    commit = str(sh.git.show('gh-pages', '--no-color', '--name-only'))
    print(commit)
    return commit


def test_serve(elsa):
    elsa('serve')
    assert 'SUCCESS' in requests.get('http://localhost:8003/').text


def test_port(elsa, port, serve_command):
    elsa(serve_command + ' --port {}'.format(port))
    assert 'SUCCESS' in requests.get('http://localhost:{}/'.format(port)).text


def test_cname(elsa, cname, serve_command):
    code = 200 if cname else 404

    elsa(serve_command + cname)
    assert requests.get('http://localhost:8003/CNAME').status_code == code


def test_freeze(elsa):
    elsa('freeze')
    with open(INDEX) as f:
        assert 'SUCCESS' in f.read()


def test_freeze_cname(elsa):
    elsa('freeze')
    with open(CNAME) as f:
        assert f.read().strip() == 'example.org'


def test_freeze_no_cname(elsa):
    elsa('freeze --no-cname')
    assert not os.path.exists(CNAME)


def test_freeze_base_url(elsa, protocol, domain):
    elsa('freeze --base-url {}://{}'.format(protocol, domain))
    with open(CNAME) as f:
        assert f.read().strip() == domain


def test_freeze_serve(elsa):
    elsa('freeze --serve')
    with open(INDEX) as f:
        assert 'SUCCESS' in f.read()
        assert 'SUCCESS' in requests.get('http://localhost:8003/').text


def test_freeze_path(elsa, tmpdir, cname):
    path = tmpdir.join('foo')
    elsa('freeze --path {}{}'.format(path, cname))

    assert path.check(dir=True)
    assert path.join('index.html').check(file=True)
    assert bool(cname) == path.join('CNAME').check()


def test_deploy_no_push_files(elsa, cname):
    elsa('deploy --no-push' + cname)
    with open(INDEX) as f:
        assert 'SUCCESS' in f.read()
        assert bool(cname) == os.path.exists(CNAME)


def test_deploy_no_push_git(elsa, cname):
    elsa('deploy --no-push' + cname)
    commit = commit_info()

    assert '.nojekyll' in commit
    assert 'index.html' in commit
    assert bool(cname) == ('CNAME' in commit)


@pytest.mark.parametrize('path', ('custom_path', 'default_path'))
def test_freeze_and_deploy(elsa, tmpdir, path):
    args = ''
    if path == 'custom_path':
        path = tmpdir.join('foo')
        args = ' --path {}'.format(path)
    freeze_command = 'freeze' + args
    deploy_command = 'deploy --no-push' + args

    elsa(freeze_command)
    elsa(deploy_command)

    commit = commit_info()
    assert 'index.html' in commit
