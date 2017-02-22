import os
import random
import subprocess

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
    return subprocess.run(cmd, **kwargs)


def get_last_commit_info(format):
    cmd = ['git', '--no-pager', 'show', '--format=' + format, '--no-patch']
    process = run(cmd, stdout=subprocess.PIPE)
    return process.stdout.strip()


def deploy(html_dir, *, push):
    """Deploy to GitHub pages, expects to be already frozen"""
    if os.environ.get('TRAVIS'):  # Travis CI
        print('Setting up git...')
        run(['git', 'config', 'user.name', get_last_commit_info('%cN')])
        run(['git', 'config', 'user.email', get_last_commit_info('%cE')])

        github_token = os.environ.get('GITHUB_TOKEN')  # from .travis.yml
        repo_slug = os.environ.get('TRAVIS_REPO_SLUG')
        origin = 'https://{}@github.com/{}.git'.format(github_token, repo_slug)
        run(['git', 'remote', 'set-url', 'origin', origin])

    print('Rewriting gh-pages branch...')
    run(['git', 'branch', '-D', 'gh-pages'], check=False,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    commit_message = 'Deploying {}'.format(random.choice(COMMIT_EMOJIS))
    run([
        'ghp-import',
        '-n',  # .nojekyll file
        '-m', commit_message,
        html_dir
    ])

    if push:
        print('Pushing to GitHub...')
        run(['git', 'push', 'origin', 'gh-pages:gh-pages', '--force'])
