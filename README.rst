\ :mushroom: Hacktoberfest limits :mushroom:
============================================

This repository is attracting many `spam pull requests`_ during `Hacktoberfest`_ 2020.

Due to the overwhelming number of PRs, we have limited interaction with this
repository to existing contributors.
If you have a pull request, please request a pull the old-fashioned way:
send the URL of your fork, and the branch name, to `encukou@gmail.com`_.
I'll merge manually or open a PR on your behalf.

If you found an issue, or want to do anything else we're disallowing this month,
please e-mail the same address.

.. _spam pull requests: https://github.com/pyvec/elsa/pulls?q=is%3Apr+is%3Aclosed
.. _Hacktoberfest: https://hacktoberfest.digitalocean.com/
.. _encukou@gmail.com: mailto:encukou@gmail.com

(And if we forget to take the message down at the end of the month,
please let us know as well!)


elsa
====

Elsa will help you build your `Frozen-Flask <http://pythonhosted.org/Frozen-Flask/>`_ based website and deploy it to GitHub pages.
It's based on scripts from `PyLadies.cz repo <https://github.com/PyLadiesCZ/pyladies.cz>`_ and is distributed under the terms of the MIT license, see LICENSE (does not apply for the image below). It requires Python 3.

.. figure:: https://raw.githubusercontent.com/pyvec/elsa/master/logo/elsa.png
   :alt: Elsa


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

Follow the `quickstart tutorial
<https://github.com/pyvec/elsa/blob/master/QUICKSTART.rst>`_
for more information.

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
        - '3.6'
    script:
        - 'python foo.py freeze'
    env:
      global:
        - secure: "blahblah"  # gem install travis; travis encrypt GITHUB_TOKEN=xyz --add
    deploy:
        provider: script
        skip_cleanup: true
        script: 'python foo.py deploy --no-freeze --push'
        on:
            branch: master
            repo: only/yours

Testing
-------

To run the test suite, install `tox <http://tox.readthedocs.io/>`_ and run it::

    tox

Elsa uses pytest, so if you are familiar with it, feel free to run  it directly.



Further notes
-------------

URLs
~~~~

When you use URLs without trailing slash (e.g. ``https://example.com/foobar``), GitHub pages would serve the pages with bad Content-Type header
(``application/octet-stream`` instead of ``text/html``) and the browser would attempt to download it.
That's why Elsa will not allow such thing and will treat ``MimetypeMismatchWarning`` from Frozen-Flask as error.
Make sure to use URLs with trailing slash (e.g. ``https://example.com/foobar/``) instead, so Frozen-Flask will create ``index.html`` in a folder and GitHub pages will use proper content type.
