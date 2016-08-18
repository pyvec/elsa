elsa
====

Elsa will help you build your `Frozen-Flask <http://pythonhosted.org/Frozen-Flask/>`_ based website and deploy it to GitHub pages.
It's based on scripts from `PyLadies.cz repo <https://github.com/PyLadiesCZ/pyladies.cz>`_ and is distributed under the terms of MIT license, see LICENSE (does not apply for the image below). It requires Python 3.

.. figure:: http://cartoonbros.com/wp-content/uploads/2015/11/Elsa-21.jpg
   :alt: elsa

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
        cli(app)

Then you can run your script like this:

.. code-block:: bash

    python foo.py serve  # serves the site, no freezing
    python foo.py freeze  # freeze the site, i.e. make a HTML snapshot
    python foo.py deploy  # deploy the frozen site to GitHub pages

See more options with ``--help``.

Travis CI based deployment
--------------------------

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
