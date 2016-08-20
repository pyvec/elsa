elsa
====

Elsa will help you build your `Frozen-Flask <http://pythonhosted.org/Frozen-Flask/>`_ based website and deploy it to GitHub pages.
It's based on scripts from `PyLadies.cz repo <https://github.com/PyLadiesCZ/pyladies.cz>`_ and is distributed under the terms of the MIT license, see LICENSE (does not apply for the image below). It requires Python 3.

.. figure:: http://cartoonbros.com/wp-content/uploads/2015/11/Elsa-21.jpg
   :alt: Elsa

   Image linked from `cartoonbros.com <http://cartoonbros.com/elsa/>`_, not stored in the repo, so the repo remains free.

Basic usage
-----------

Create you Flask app and give it to ``elsa.cli()``:

.. code-block:: python

    from flask import Flask

    app = Flask(...)

    # do stuff with app

    if __name__ == '__main__':
        from elsa import cli
        cli(app, base_url='https://example.com')

This will add command line interface to the script, enabling you to use it like this:

.. code-block:: bash

    python foo.py serve  # serves the site, no freezing, so you can check it quickly
    python foo.py freeze  # freezes the site, i.e. makes a HTML snapshot
    python foo.py deploy  # deploys the frozen site to GitHub pages

See more options with ``--help``.

Travis CI based deployment
--------------------------

Travis CI is (in this context) a tool, that allows you to deploy the site automatically to GitHub pages after every push.
All you have to do is tell Travis to run Elsa and provide a GitHub token.
Elsa on Travis will freeze the site and deploy it frozen to GitHub pages.
Elsa knows it's being run on Travis and will use the provided GitHub token to gain push permissions.
Elsa will push force to ``gh-pages`` branch in a single commit rewriting the history and all manual changes of that branch.

Here is an example ``.travis.yml`` file for automatic deployment. It assumes elsa and other requirements are in ``requirements.txt`` and that you are familiar with Travis CI (so it's not very verbose):

.. code-block:: yaml

    language: python
    python:
        - '3.5'
    script:
        - "echo 'No linters, no tests...'"
    env:
      global:
        - secure: "blahblah"  # gem install travis; travis encrypt GITHUB_TOKEN=xyz --add
    deploy:
        provider: script
        script: 'python foo.py deploy'
        on:
            branch: master
            repo: only/yours

Further notes
-------------

URLs
~~~~

When you use URLs without trailing slash (e.g. ``https://example.com/foobar``), GitHub pages will serve the pages with bad Content-Type header
(``application/octet-stream`` instead of ``text/html``) and the browser will attempt to download it.
Make sure to use URLs with trailing slash (e.g. ``https://example.com/foobar/``) instead, so Frozen-Flask will create ``index.html`` in a folder and GitHub pages will use proper content type.
