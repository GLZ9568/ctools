.. _dev_releasing_devel:

Incrementing the development version
====================================

As last step you have to increment the version number to the next
development release number. Before doing that you should make sure that you
have merged the released software version into the devel branch. You do this
by typing:

.. code-block:: bash

   $ git checkout devel
   $ git merge master

Now you launch again the release manager to update the version number:

.. code-block:: bash

   $ dev/release.py
   ctools release manager
   ======================

   [1] Make a new release
   [2] Set the package version in current branch
   [3] Set the libtool version in current branch
   [4] Commit changes in current branch
   [5] Create tarball from current branch
   [6] Check tarball
   [q] Quit
   Enter your choice:

Select ``2`` and enter the new version number:

.. code-block:: bash

   Current ctools version is '1.2.0'. Please enter new ctools version: 1.3.0.dev1
   Change version to '1.3.0.dev1'? (y/n): y
   ctools version changed to '1.3.0.dev1'

   [1] Make a new release
   [2] Set the package version in current branch
   [3] Set the libtool version in current branch
   [4] Commit changes in current branch
   [5] Create tarball from current branch
   [6] Check tarball
   [q] Quit
   Enter your choice:

Now commit the changes by chosing ``4``:

.. code-block:: bash

  The following files have been changed:
   M README.md
   M configure.ac
   M ctools.pc.in
   M doc/Doxyfile
   M doc/source/conf.py
   M sonar-project.properties
   Commit all changes? (y/n): y
   Please enter a commit message: Update to release version 1.3.0.dev1
   [devel d38bbdc] Update to release version 1.3.0.dev1
    6 files changed, 8 insertions(+), 8 deletions(-)

   [1] Make a new release
   [2] Set the package version in current branch
   [3] Set the libtool version in current branch
   [4] Commit changes in current branch
   [5] Create tarball from current branch
   [6] Check tarball
   [q] Quit
   Enter your choice:

Quit the release manager by chosing ``q`` and push the modifications into
the repository:

.. code-block:: bash

   $ git push origin

Congratulations, you are done!
