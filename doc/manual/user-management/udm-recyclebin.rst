.. SPDX-FileCopyrightText: 2021-2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _udm-recyclebin:

UDM Recycle Bin
===============

.. index::
   single: directory manager; recycle bin
   single: recycle bin; UDM objects

The UDM recycle bin feature provides a way to temporarily store deleted objects
before they are permanently removed from the LDAP directory. When enabled
through policy configuration, deleted UDM objects are moved to a special
recycle bin container instead of being immediately removed from LDAP. The
original object data is preserved along with metadata about the deletion.

The recycle bin feature consists of several components:

* **Recycle Bin Policy** (``policies/recyclebin``): Configures which objects should be recycled
* **Deleted Object Handler** (``recyclebin/deletedobject``): Manages objects in the recycle bin
* **LDAP Schema**: Defines attributes for recycle bin functionality
* **UDM Integration**: Hooks into object deletion process

Policy configuration
---------------------

The recycle bin behavior is controlled by the ``policies/recyclebin`` policy,
which can be applied to containers and objects. The policy defines:

``enabled``
   Whether recycle bin is active for objects in scope.

``udm_modules``
   List of UDM module types to recycle (e.g., ``users/user``, ``groups/group``).

``properties``
   Specific object properties to preserve (empty = all properties).

``retention_time``
   How long to keep objects in recycle bin (days, 0 = indefinite).

Limitations
-----------

.. warning::

   The recycle bin feature has several important limitations that must be considered.

Hardcoded module support
~~~~~~~~~~~~~~~~~~~~~~~~

The recycle bin policy can only be applied to a predefined list of UDM module
types defined in the ``policy_apply_to`` list in ``policies/recyclebin.py``:

* ``container/ou``, ``container/cn``
* ``users/user``
* ``groups/group``
* ``computers/*`` (all computer types: domaincontroller_master, domaincontroller_backup, domaincontroller_slave, memberserver, windows, linux, ubuntu, macos)

If customers need recycle bin functionality for other UDM module types (e.g.,
custom modules, shares, printers, etc.), the ``policy_apply_to`` list must be
manually extended by developers.

Module integration requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a UDM module to support recycle bin functionality:

1. The module must be listed in ``policy_apply_to``
2. The module's deletion process must call the recycle bin hooks
3. The module must handle policy evaluation correctly
4. Object restoration must work correctly with the module's constraints

Object deletion flow
--------------------

1. User initiates object deletion via UDM
2. UDM checks for applicable recycle bin policies
3. If recycling is enabled and module is supported:

   a. Original object attributes are collected
   b. Object references are identified
   c. Object is moved to ``cn=recyclebin,cn=internal`` with preserved data
   d. Original object is removed from its location

4. If recycling is disabled or unsupported, normal deletion occurs

Object restoration
------------------

1. Deleted object is retrieved from recycle bin
2. Original location is checked for conflicts
3. Object attributes are restored to original DN
4. Object is removed from recycle bin

Storage format
--------------

Deleted objects are stored with:

* **objectClass**: ``extensibleObject``, ``univentionRecycleBinObject``
* **Original data**: All non-operational LDAP attributes preserved
* **Metadata**: Deletion timestamp, user who deleted, original DN, object type
* **References**: Objects that referenced the deleted object

Extending support
-----------------

To add recycle bin support for a new UDM module:

1. Update the policy configuration in ``modules/univention/admin/handlers/policies/recyclebin.py``:

   .. code-block:: python

      policy_apply_to = [
          # ... existing modules ...
          'your/new_module',  # Add your module here
      ]

2. Test that deletion and restoration work correctly
3. Update this documentation to include the new module
4. Ensure any module-specific constraints are handled