Changes
=======

0.1.4
-----

* Add ``invoke_cli`` option for the ``cli`` function.
  If set to ``False``, it only returns the cli for further extending. (`#45`_)
* Don't remove the remote tracking branch when ``--no-push`` is used (fixes `#41`_)
* Improve handling of ``FrozenFlaskWarning`` (`#37`_)
* Add the ``--show-git-push-stderr`` option to make deploy more verbose,
  this can help debug problems, but is potentially dangerous, hence the output
  of ``git push`` is hidden by default. (`#37`_)

.. _#37: https://github.com/pyvec/elsa/pull/37
.. _#41: https://github.com/pyvec/elsa/issues/41
.. _#45: https://github.com/pyvec/elsa/pull/45

0.1.3
-----

* Only treat Frozen-Flask warnings as errors, not other warnings (`#34`_)
* Add a ``--remote`` option for ``deploy`` to use a custom git remote
* Be consistent on local vs Travis CI deployment, always erase the history
  of the ``gh-pages`` branch (actually fixes `#14`_)

.. _#14: https://github.com/pyvec/elsa/issues/14
.. _#34: https://github.com/pyvec/elsa/pull/34


0.1.2
-----

* **Security:** Do not display the remote URL when pushing gh-pages branch.
  If you used Elsa 0.1 or 0.1.1 on Travis CI, revoke your GitHub
  token, it was probably leaked in the log. (`#25`_)

.. _#25: https://github.com/pyvec/elsa/issues/25


0.1.1
-----

* Fix a problem with Travis CI based deployment


0.1
---

* Add a test suite
* Treat Frozen-Flask warnings as errors
* **Important:** It is now recommended to run ``freeze`` in ``.travis.yml``
  ``script`` section to catch problems in Pull Requests etc.
* **Important:**  This version of Elsa will warn if you use the ``deploy``
  command without specifying ``--push`` or ``--no-push`` explicitly.
  In a future release, it will switch to *not* pushing the built pages by
  default.
* Remove the dependency on ``sh`` to improve compatibility with Windows
* Supports Linux, Mac OS X and Windows
* The ``gh-branch`` is purged before the deploying commit (`#14`_)
* It is possible to shutdown the server via a special POST request (`#21`_)

.. _#14: https://github.com/pyvec/elsa/issues/14
.. _#21: https://github.com/pyvec/elsa/pull/21


0.1.dev4
--------

* Set template auto_reload flag directly in serve mode (`#8`_)

.. _#8: https://github.com/pyvec/elsa/issues/8


0.1.dev3
--------

* Set TEMPLATES_AUTO_RELOAD by default (`#5`_)
* Suppress a bogus warning about CNAME mime type (`#7`_)

.. _#5: https://github.com/pyvec/elsa/issues/5
.. _#7: https://github.com/pyvec/elsa/issues/7


0.1.dev2
--------

* The CNAME route is now created automatically


0.1.dev1
--------

* Initial implementation from
  `PyLadies.cz <https://github.com/PyLadiesCZ/pyladies.cz>`_
