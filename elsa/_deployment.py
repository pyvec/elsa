import os
import random
import subprocess
import sys

COMMIT_EMOJIS = [
    ':sunglasses:', ':two_hearts:', ':sparkles:', ':star2:', ':star:',
    ':blue_heart: :yellow_heart:', ':raised_hands:', ':ok_hand:', ':ok_woman:',
    ':dancer:', ':raising_hand:', ':woman:', ':girl:', ':princess:', ':sunny:',
    ':cat:', ':koala:', ':snake:', ':paw_prints:', ':four_leaf_clover:',
    ':octocat:', ':gift_heart:', ':tada:', ':balloon:', ':cake:', ':rocket:',
]


def run(cmd, **kwargs):
    """Same as ``subprocess.run``, but checks the result by default"""
    kwargs.setdefault('check', True)
    if 'quiet' in kwargs:
        if kwargs['quiet']:
            kwargs['stdout'] = subprocess.DEVNULL
            kwargs['stderr'] = subprocess.DEVNULL
        del kwargs['quiet']
    return subprocess.run(cmd, **kwargs)


def get_last_commit_info(format):
    cmd = ['git', '--no-pager', 'show', '--format=' + format, '--no-patch']
    process = run(cmd, stdout=subprocess.PIPE)
    return process.stdout.strip()


def get_git_toplevel():
    cmd = ['git', 'rev-parse', '--show-toplevel']
    process = run(cmd, stdout=subprocess.PIPE)
    return process.stdout.strip().decode('utf-8')


def deploy(html_dir, *, remote, push, show_err):
    """Deploy to GitHub pages, expects to be already frozen"""
    if os.environ.get('TRAVIS'):  # Travis CI
        print('Setting up git...')
        run(['git', 'config', 'user.name', get_last_commit_info('%cN')])
        run(['git', 'config', 'user.email', get_last_commit_info('%cE')])

        github_token = os.environ.get('GITHUB_TOKEN')  # from .travis.yml
        repo_slug = os.environ.get('TRAVIS_REPO_SLUG')
        rurl = 'https://{}@github.com/{}.git'.format(github_token, repo_slug)
        run(['git', 'remote', 'set-url', remote, rurl])

    print('Rewriting gh-pages branch...')
    run(['git', 'branch', '-D', 'gh-pages'], check=False, quiet=True)
    ref = '.git/refs/remotes/{}/gh-pages'.format(remote)
    ref = os.path.join(get_git_toplevel(), ref)
    if os.path.exists(ref):
        os.remove(ref)
    commit_message = 'Deploying {}'.format(random.choice(COMMIT_EMOJIS))
    run([
        'ghp-import',
        '-n',  # .nojekyll file
        '-m', commit_message,
        '-r', remote,
        html_dir
    ])

    if push:
        print('Pushing to GitHub...')
        try:
            run(['git', 'push', remote, 'gh-pages:gh-pages', '--force'],
                quiet=not show_err)
        except subprocess.CalledProcessError as e:
            msg = 'Error: git push failed (exit status {}).'
            if not show_err:
                msg += ('\nNote: Due to security constraints, Elsa does not '
                        'show the error message from git, as it may include '
                        'sensitive information and this could be logged. Use '
                        'the --show-git-push-stderr switch to change this '
                        'behavior.')
            print(msg.format(e.returncode), file=sys.stderr)
            sys.exit(e.returncode)
