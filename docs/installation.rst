Installation
============

Requirements
------------

- Python 3.10, 3.11, or 3.12
- Git (``git`` executable available on ``PATH``)
- uv (recommended) or pip

.. note::

   Git is a system dependency used for repository commit lookup
   (for example via ``git ls-remote``). It is not managed through
   ``pyproject.toml`` and must be installed separately.

Install from PyPI
-----------------

Using uv (recommended)
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   uv add rsmetacheck-bot

Using pip
~~~~~~~~~

.. code-block:: bash

   pip install rsmetacheck-bot

Optional extras for documentation, tests, and development tooling are exposed
through the package metadata:

.. code-block:: bash

   pip install "rsmetacheck-bot[docs]"
   pip install "rsmetacheck-bot[test]"
   pip install "rsmetacheck-bot[dev]"

From source for contributors
----------------------------

.. code-block:: bash

   git clone https://github.com/SoftwareUnderstanding/rsmetacheck-bot.git
   cd rsmetacheck-bot
   uv sync
   uv run rsmetacheck-bot --help

For local development with the optional dependency sets declared in
``pyproject.toml``:

.. code-block:: bash

   pip install -e ".[dev,test,docs]"
