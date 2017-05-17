Elsa Quickstart
===============

This document will help you to set up an elsa powered website on your domain.
It assumes you are already familiar with git.

Overview
--------

In this tutorial, we will:

1. create a GitHub repository with a simple `Flask`_ website
2. set up a domain to serve the website from
3. set up `Travis CI`_ to run elsa and deploy the website to `GitHub pages`_


.. _Flask: http://flask.pocoo.org/
.. _Travis CI: https://travis-ci.org/
.. _GitHub pages: https://pages.github.com/


Step 1: Create a repository on GitHub
-------------------------------------

Before you start, you'll need a GitHub repository. Note that elsa is meant to
be run on Travis CI and Travis CI only supports GitHub. Other uses might be
possible but are not covered in this tutorial.

If you already know how to create repositories on GitHub, feel free to skip
this part of the tutorial and continue with the next step.

Follow the `GitHub documentation to set up a new repository
<https://help.github.com/articles/create-a-repo/>`_, then `clone it
<https://help.github.com/articles/cloning-a-repository/>`_.

You can use both *public* and *private* repositories with elsa.
This tutorial assumes a *public* repository, but will give you a heads up if
you use a *private* one.


Step 2: Create a Flask website powered by Elsa
----------------------------------------------

In this tutorial we'll just create a very simple `Flask`_ website that says
hello world. You are of course encouraged to create more sophisticated websites.
Please read the excellent `Flask's own Qucikstart`_ to learn more about
creating websites in this popular Python web framework.

Our simple website will be defined in just one file, although it is of course
possible to have it spread across several files or even create a module.
The name of that file is not important, but it is generally not advised to use
names colliding with stuff you are going to import from Python,
such as ``elsa.py`` or ``flask.py``.
In this tutorial, we'll name it ``website.py``.

Our simple Flask website may look like this:

.. code-block:: python

    from flask import Flask


    app = Flask('website')


    @app.route('/')
    def index():
        return '<html><body>Hello world!</body></html>'

When you'll create more sophisticated websites, read trough the Frozen-Flask
documentation about `finding URLs`_ and `filenames and MIME types`_.

Once you have your Flask-powered website, add elsa at the bottom of that file:

.. code-block:: python

    if __name__ == '__main__':
        from elsa import cli
        cli(app, base_url='http://example.com')

Make sure to add your own base URL instead of ``http://example.com``.
The base URL consists of ``http://`` and your domain name.
(You can use ``https://`` with Elsa as well but it does not work with GitHub
pages out of the box and is not covered by this tutorial.)

To test your new website, you'll need to install elsa. The best way is to use
the Python virtual environment:

.. code-block:: bash

    $ python3 -m venv __env__
    $ . __env__/bin/activate
    (__env__)$ python -m pip install elsa

The above snippet assumes you are running Linux or Mac OS X, consult the
`virtual environment documentation`_ if you happen to use Windows.
If you are not yet familiar with virtual environments, note that they do not
belong in git and make sure you add ``__env__`` to your ``.gitignore`` file.

Now run your website on your own computer like this:

.. code-block:: bash

    (__env__)$ python website.py serve
     * Running on http://0.0.0.0:8003/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger pin code: 237-729-566

You can use your web browser to open http://localhost:8003/ and you should see
your website. You can terminate the local server by pressing ``Ctrl+C`` in the
terminal as said in the output.

If it worked, you can freeze your website and test if it works frozen:

.. code-block:: bash

    (__env__)$ python website.py freeze --serve
    Generating HTML...
     * Running on http://127.0.0.1:8003/ (Press CTRL+C to quit)

The website should be available on http://localhost:8003/ once again, this time
served from static HTML pages. Press ``Ctrl+C`` to terminate the server once
again and you are ready to set up a deployment of the website using
`Travis CI`_.

.. _Flask's own Qucikstart: http://flask.pocoo.org/docs/latest/quickstart/
.. _finding URLs: http://pythonhosted.org/Frozen-Flask/#finding-urls
.. _filenames and MIME types: http://pythonhosted.org/Frozen-Flask/#filenames-and-mime-types
.. _virtual environment documentation: https://docs.python.org/3/library/venv.html


Step 3: Change your DNS settings
--------------------------------

In order to host your website on `GitHub pages`_ on your own domain, you'll
need to change your DNS settings. GitHub pages documentation covers that for:

- `apex domain`_ (such as ``example.com``)
- `www subdomain`_ (such as ``www.example.com``)
- `custom subdomain`_ (such as ``blog.example.com``)

Note that the documentation talks about adding a custom domain to your GitHub
Pages site and about a ``CNAME`` file. You don't have to worry about either,
elsa will do that for you.

*It should be possible to use elsa without a custom domain, but it is not
covered by this tutorial.*


.. _apex domain: https://help.github.com/articles/setting-up-an-apex-domain/
.. _www subdomain: https://help.github.com/articles/setting-up-a-www-subdomain/
.. _custom subdomain: https://help.github.com/articles/setting-up-a-custom-subdomain/


Step 4: Setting up Travis CI
----------------------------

If you have never used `Travis CI`_ before, head in there and log in with your
GitHub account. If your GitHub repo is private, you have to use the paid
version on `travis-ci.com`_, otherwise use `travis-ci.org`_ for free.
This tutorial assumes your repo is public and will use `travis-ci.org`_.

Go to your `profile page`_ and enable Travis CI for your
repository.

Create a ``.travis.yml`` file in the repository with the following content:

.. code-block:: yaml

    language: python
    python:
    - 3.6
    script:
    - python website.py freeze
    deploy:
      provider: script
      skip_cleanup: true
      script: python website.py deploy --no-freeze --push
      on:
        branch: master
        repo: username/reponame

Change ``username/reponame`` for your own repository slug, for example
``anna/mywebsite``. Also change all occurrences of ``website.py`` with your
own filename if named differently.

This file tells Travis CI what to do. Let's describe it a little bit more
so you know what it does. If you are familiar enough with Travis CI, feel free
to skip this part (ended by the first horizontal rule).
If you want to know more about ``.travis.yml``, read the `documentation
<https://docs.travis-ci.com/user/customizing-the-build>`_.

.. code-block:: yaml

    language: python
    python:
    - 3.6

This part makes sure we'll have Python 3.6 available on Travis CI.
Travis CI allows to run different version of Python at the same time, but that
would bring us no benefit in this situation. Elsa currently supports both
Python 3.5 and Python 3.6, so we'll use the never version, but 3.5 would be
fine as well.

.. code-block:: yaml

    script:
    - python website.py freeze

The ``script`` section tells Travis CI what to run. This section will be run
from all branches and also Pull Requests, so we let elsa freeze the website to
see if it works. If it does not, Travis will indicate that in the Pull Request
or next to a commit message in the list of commits on GitHub. You'll also get
notified by e-mail.

.. code-block:: yaml

    deploy:
      provider: script
      skip_cleanup: true
      script: python website.py deploy --no-freeze --push
      on:
        branch: master
        repo: username/reponame

The ``deploy`` section is only run when the ``script`` section succeeds.
We also limit it to master branch and your own repo to make sure only the right
version of the website gets deployed. The ``skip_cleanup`` tells Travis CI
not to clean the repository before deploying, so we can use the ``--no-freeze``
flag (Elsa already froze the website in the ``script`` section).

----------

We've not used the ``python website.py deploy`` command in this tutorial yet,
but you could run it locally to deploy your site as well. It pushes the frozen
website to ``gh-pages`` branch of your repo, thus publishing it on GitHub pages.

On your own machine, you can push to the repository as usual, but Travis CI
cannot, it does not have write access. In order to provide one, you'll have to
`create a personal access token on GitHub
<https://help.github.com/articles/creating-an-access-token-for-command-line-use/>`_
(repo scope needed) and provide it to Travis CI.

You cannot just add the token to ``.travis.yml``, as anyone could read it,
so you'll add it encrypted. Don't worry, it's not complicated,
the easiest way is to use the ``travis`` command line tool that can be
installed by ``gem install travis``:

.. code-block:: bash

    travis encrypt GITHUB_TOKEN=YOUR_TOKEN_GOES_HERE --add

Travis CI will not decrypt the token when running on different repositories
(for example forks) or when running on Pull Requests. If you want to know more,
read the documentation about `encrypted environment variables`_.

The ``.travis.yml`` should now look similarly to this:


.. code-block:: yaml

    language: python
    python:
    - 3.6
    script:
    - python website.py freeze
    deploy:
      provider: script
      skip_cleanup: true
      script: python website.py deploy --no-freeze --push
      on:
        branch: master
        repo: username/reponame
    env:
      global:
        secure: IvsctOgRA/...snip.../moJ5qM=

----------

On your machine you've installed elsa. You need to get it installed on Travis
CI as well. To do that, add elsa to a file called ``requirements.txt`` in the
root directory of your repository:

.. code-block::

    elsa

If you happen to have more dependencies, add them on separate lines. You don't
need to add Flask, because elsa already depends on it, but if you add it, it
will work as well.

Now you can push to the ``master`` branch. Note that at least the following
files should be in git, but it is not necessary to push them all at once:

- ``website.py`` (or your equivalent) and any other files needed for your Flask
  app
- ``requirements.txt`` with ``elsa`` in it
- ``.travis.yml``

When you push, you can go to ``https://travis-ci.org/username/reponame``
(replacing the ``username`` and ``reponame`` with your own) to see how the
build goes. If everything goes right, your website should be alive on your
domain.
And it will be updated anytime you push changes to the ``master`` branch.

Feel free to open an `issue`_ if something goes wrong or if you have questions.

.. _travis-ci.com: https://travis-ci.com/
.. _travis-ci.org: https://travis-ci.org/
.. _profile page: https://travis-ci.org/profile
.. _encrypted environment variables: https://docs.travis-ci.com/user/environment-variables/#Defining-encrypted-variables-in-.travis.yml
.. _issue: https://github.com/pyvec/elsa/issues

