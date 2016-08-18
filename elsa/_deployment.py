import os
import random
from sh import git, ghp_import

COMMIT_EMOJIS = [
    ':sunglasses:', ':two_hearts:', ':sparkles:', ':star2:', ':star:',
    ':blue_heart: :yellow_heart:', ':raised_hands:', ':ok_hand:', ':ok_woman:',
    ':dancer:', ':raising_hand:', ':woman:', ':girl:', ':princess:', ':sunny:',
    ':cat:', ':koala:', ':snake:', ':paw_prints:', ':four_leaf_clover:',
    ':octocat:', ':gift_heart:', ':tada:', ':balloon:', ':cake:', ':rocket:',
]


def deploy(html_dir, *, push):
    """Deploy to GitHub pages, expects to be already frozen"""
    if os.environ.get('TRAVIS'):  # Travis CI
        print('Setting up git...')
        git.config(
            'user.name',
            git('show', format='%cN', s=True, _tty_out=False).strip()
        )
        git.config(
            'user.email',
            git('show', format='%cE', s=True, _tty_out=False).strip()
        )

        github_token = os.environ.get('GITHUB_TOKEN')  # from .travis.yml
        repo_slug = os.environ.get('TRAVIS_REPO_SLUG')
        origin = 'https://{}@github.com/{}.git'.format(github_token, repo_slug)
        git.remote('set-url', 'origin', origin)

    print('Rewriting gh-pages branch...')
    commit_message = 'Deploying {}'.format(random.choice(COMMIT_EMOJIS))
    ghp_import('-n', '-m', commit_message, html_dir)  # -n for .nojekyll file

    if push:
        print('Pushing to GitHub...')
        git.push('origin', 'gh-pages:gh-pages', force=True)
