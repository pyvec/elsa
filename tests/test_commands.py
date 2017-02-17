from contextlib import contextmanager
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


def is_cname(option: str) -> bool:
    '''
    Whether the given command line option means the CNAME should be generated
    '''
    return option == '--cname'


cname = parametrized_fixture(cname='--cname', no_cname='--no-cname')
serve_command = parametrized_fixture(serve=['serve'],
                                     freeze_serve=['freeze', '--serve'])
port = parametrized_fixture(8001, 8080)
domain = parametrized_fixture('foo.bar', 'spam.eggs')
protocol = parametrized_fixture('http', 'https')


class ElsaRunner:
    '''
    Class for elsa fixture enabling blocking or background runs

    If there is a local website.py in pwd, uses that one,
    uses the one from fixtures instead.
    '''
    def run(self, *command):
        print('COMMAND: python website.py', *command)
        subprocess.run(self.create_command(command), check=True)

    @contextmanager
    def run_bg(self, *command):
        print('COMMAND IN BACKGROUND: python website.py', *command)
        proc = subprocess.Popen(self.create_command(command))
        time.sleep(1)  # TODO actually check if ready instead
        yield proc
        proc.terminate()
        proc.wait()
        assert (proc.returncode == -signal.SIGTERM or
                proc.returncode == 0)

    def finalize(self):
        self.lax_rmtree(BUILDDIR_FIXTURES)

    @classmethod
    def create_command(cls, command):
        if os.path.exists(SCRIPT):
            script = SCRIPT
        else:
            script = SCRIPT_FIXTURES
        command = tuple(str(item) for item in command)
        return (sys.executable, script) + command

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
    commit = str(sh.git.show('gh-pages', '--no-color', '--name-only'))
    print(commit)
    return commit


def assert_commit_author(commit):
    assert 'Author: Tester Example <tester@example.org>' in commit


@pytest.fixture
def gitrepo(tmpdir):
    '''
    This fixture creates a git repository with website.py in tmpdir
    '''
    repo = tmpdir.mkdir('repo')
    script = repo.join(SCRIPT)
    with open(SCRIPT_FIXTURES) as f:
        script.write(f.read())
    with repo.as_cwd():
        sh.git.init()
        sh.git.add(SCRIPT)
        sh.git.config('user.email', 'tester@example.org')
        sh.git.config('user.name', 'Tester Example')
        sh.git.commit('-m', 'Initial commit')
        yield repo


@pytest.mark.xfail(strict=True)
def test_elsa_fixture_bad_exit_status(elsa):
    elsa.run('not', 'a', 'chance')


@pytest.mark.xfail(strict=True)
def test_elsa_fixture_bad_exit_status_bg(elsa):
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
    code = 200 if is_cname(cname) else 404

    with elsa.run_bg(*serve_command, cname):
        assert requests.get('http://localhost:8003/CNAME').status_code == code


def test_freeze(elsa):
    elsa.run('freeze')
    with open(INDEX_FIXTURES) as f:
        assert 'SUCCESS' in f.read()


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
    assert is_cname(cname) == path.join('CNAME').check()


def test_deploy_no_push_files(elsa, cname, gitrepo):
    elsa.run('deploy', '--no-push', cname)
    with open(INDEX) as f:
        assert 'SUCCESS' in f.read()
    assert is_cname(cname) == os.path.exists(CNAME)


def test_deploy_no_push_git(elsa, cname, gitrepo):
    elsa.run('deploy', '--no-push', cname)
    commit = commit_info()

    assert '.nojekyll' in commit
    assert 'index.html' in commit
    assert is_cname(cname) == ('CNAME' in commit)
    assert_commit_author(commit)


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
    assert 'index.html' in commit
    assert_commit_author(commit)
