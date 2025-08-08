#
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# SPDX-FileCopyrightText: 2004-2025 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

"""|UDM| module for the external account objects"""

from __future__ import annotations

import univention.admin
import univention.admin.allocators
import univention.admin.filter
import univention.admin.handlers
import univention.admin.localization
import univention.admin.mapping
import univention.admin.password
import univention.admin.syntax
import univention.admin.uexceptions
from univention.admin.guardian_roles import GuardianBase, register_role_mapping, role_layout, role_properties
from univention.admin.layout import Group, Tab


translation = univention.admin.localization.translation('univention.admin.handlers.users')
_ = translation.translate

module = 'users/external_account'
operations = ['add', 'edit', 'remove', 'search']

childs = False
short_description = _('External account')
object_name = _('External account')
object_name_plural = _('External accounts')
long_description = _('This object represents a external management account. It is intended for functional purposes and is not counted as user object in the license.')

options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'univentionExternalAccount'],
    ),
}
property_descriptions = {
    'uuid': univention.admin.property(
        short_description=_('UUID of the external account'),
        long_description='',
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
        required=True,
        may_change=False,
        identifies=True,
    ),
    'preferred_username': univention.admin.property(
        short_description=_('Display name'),
        long_description='',
        syntax=univention.admin.syntax.TwoThirdsString,
        include_in_default_search=True,
        required=False,
        copyable=True,
    ),
    'description': univention.admin.property(
        short_description=_('Description'),
        long_description='',
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
        copyable=True,
    ),
}
property_descriptions.update(role_properties())

layout = [
    Tab(_('General'), _('Basic settings'), layout=[
        Group(_('External account'), layout=[
            ['uuid', 'description'],
            ['preferred_username'],
        ]),
    ]),
]
layout.append(role_layout())


mapping = univention.admin.mapping.mapping()
mapping.register('uuid', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('preferred_username', 'univentionPreferredUsername', None, univention.admin.mapping.ListToString)
mapping.register('description', 'description', None, univention.admin.mapping.ListToString)
register_role_mapping(mapping)


class object(univention.admin.handlers.simpleLdap, GuardianBase):
    module = module

    @classmethod
    def identify(cls, dn: str, attr: univention.admin.handlers._Attributes, canonical: bool = False) -> bool:
        return b'univentionExternalAccount' in attr.get('objectClass', [])

    def _ldap_pre_create(self) -> None:
        super()._ldap_pre_create()
        self.info['univentionObjectIdentifier'] = self.info['uuid']


lookup_filter = object.lookup_filter
lookup = object.lookup
identify = object.identify
