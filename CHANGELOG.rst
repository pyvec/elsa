Changes
=======

0.1 (unreleased)
----------------

* Add a test suite
* Treat Frozen-Flask warnings as errors
* **Important:** It is now recommended to run ``freeze`` in ``.travis.yml``
  ``script`` section to catch problems in Pull Requests etc.


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
