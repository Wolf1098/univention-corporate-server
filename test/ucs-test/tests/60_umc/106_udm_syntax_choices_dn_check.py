#!/usr/share/ucs-test/runner python3
## desc: Test that user_may_read filtering is only applied on syntax choices when all IDs are valid LDAP DNs
## bugs: [1815]
## roles:
##  - domaincontroller_master
## packages: [python3-univention-directory-manager, univention-management-console-module-udm]
## exposure: safe

import unittest
import univention.admin.syntax as udm_syntax
from univention.management.console.modules.udm.udm_ldap import read_syntax_choices, set_user_roles
from univention.management.console.ldap import get_admin_connection


class SyntaxWithDNChoices(udm_syntax.select):
    """A test syntax that returns choices with valid LDAP DNs."""

    def __init__(self):
        super().__init__()
        self.name = 'SyntaxWithDNChoices'
        self.udm_module = 'users/user'

    def get_choices(self, ldap_connection, options=None):
        base = ldap_connection.base
        return [
            (f'uid=user1,cn=users,{base}', 'User 1'),
            (f'uid=user2,cn=users,{base}', 'User 2'),
        ]


class SyntaxWithMixedChoices(udm_syntax.select):
    """A test syntax that returns choices with some non-DN values."""

    def __init__(self):
        super().__init__()
        self.name = 'SyntaxWithMixedChoices'
        self.udm_module = 'users/user'

    def get_choices(self, ldap_connection, options=None):
        base = ldap_connection.base
        return [
            (f'uid=user1,cn=users,{base}', 'User 1'),
            ('simple-value', 'Simple Value'),
        ]


class TestSyntaxChoicesDNCheck(unittest.TestCase):
    """Test that user_may_read filtering is only applied when all IDs are valid LDAP DNs."""

    @classmethod
    def setUpClass(cls):
        cls.ldap_connection, cls.ldap_position = get_admin_connection()

        admin_dn = f"uid=Administrator,cn=users,{cls.ldap_connection.base}"
        set_user_roles(admin_dn)

    def test_all_valid_dns_filtered(self):
        """Test that choices are filtered when all IDs are valid LDAP DNs."""
        syntax = SyntaxWithDNChoices()
        choices = read_syntax_choices(syntax, ldap_connection=self.ldap_connection, ldap_position=self.ldap_position)

        for choice in choices:
            assert 'id' in choice
            assert 'label' in choice
            assert 'module_name' in choice

        if choices:
            assert 'module_name' in choices[0]

    def test_mixed_dns_not_filtered(self):
        """Test that choices aren't filtered when some IDs aren't valid LDAP DNs."""
        syntax = SyntaxWithMixedChoices()
        choices = read_syntax_choices(syntax, ldap_connection=self.ldap_connection, ldap_position=self.ldap_position)

        assert len(choices) == 2

        for choice in choices:
            assert 'id' in choice
            assert 'label' in choice

        assert any(choice['id'] == 'simple-value' for choice in choices)


if __name__ == '__main__':
    unittest.main()
