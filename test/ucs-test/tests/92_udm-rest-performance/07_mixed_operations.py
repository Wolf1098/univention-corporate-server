#!/usr/share/ucs-test/runner /usr/share/ucs-test/locust-docker MixedOperationsTest
# /usr/share/ucs-test/runner /usr/share/ucs-test/locust --spawn-rate 20 -u 20 -t 2m --csv MixedOperations --html MixedOperations.html MixedOperationsTest
## desc: "UDM REST API performance test for mixed operations"
## exposure: safe
## tags: [producttest, SKIP]
## roles: [domaincontroller_master,domaincontroller_backup,domaincontroller_slave,memberserver]
## env:
##   LOCUST_SPAWN_RATE: "20"
##   LOCUST_RUN_TIME: "2m"
##   LOCUST_USERS: "20"
##   LOCUST_USER_CLASSES: MixedOperationsTest
##   WAIT_MIN: "0"
##   WAIT_MAX: "0"
##   TIMEOUT: "300"

import random
import time

from locust import HttpUser, between, task
from rest_utils import (
    UDMRestClient, UDMTestDataGenerator, add_created_group, add_created_user, get_config, get_ldap_containers,
    get_ldap_filter, get_random_created_group, get_random_created_user, setup_logging,
)


# Configuration
WAIT_MIN = get_config('WAIT_MIN', 0)
WAIT_MAX = get_config('WAIT_MAX', 0)

# Setup logging
log = setup_logging()


class MixedOperationsTest(HttpUser):
    wait_time = between(WAIT_MIN, WAIT_MAX)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.udm_client = None
        self.data_generator = None
        self.containers = None

    def on_start(self):
        """Initialize session with UDM client and data generator."""
        self.udm_client = UDMRestClient(self.client)
        self.data_generator = UDMTestDataGenerator(prefix='mixed')
        self.containers = get_ldap_containers()
        log.info('Mixed operations test started')

    def on_stop(self):
        """Clean up created objects."""
        if self.udm_client:
            self.udm_client.cleanup_created_objects()
        log.info('Mixed operations test stopped')

    @task(8)
    def create_search_modify_user(self):
        """Create a user, search for it, then modify it."""
        # Create user
        user_data = self.data_generator.next_user_data(password='Univention.123')
        success, user_dn = self.udm_client.create_user(
            username=user_data['username'],
            lastname=user_data['lastname'],
            password=user_data['password'],
            description=user_data['description'],
        )

        if success and user_dn:
            add_created_user(user_dn)
            log.debug(f'Created user for mixed ops: {user_data["username"]}')

            # Search for the created user
            success, count = self.udm_client.search_objects(
                object_type='users/user',
                position=self.containers['users'],
                filter_expr=f'(uid={user_data["username"]})',
                name='mixed_search_created_user',
            )

            if success:
                log.debug(f'Found created user in search: {count} results')

            # Modify the user
            modifications = {
                'description': f'Modified in mixed ops at {int(time.time())}',
            }

            success = self.udm_client.modify_object(
                object_type='users/user',
                object_dn=user_dn,
                modifications=modifications,
                name='mixed_modify_user',
            )

            if success:
                log.debug(f'Modified user in mixed ops: {user_dn}')

    @task(8)
    def create_search_modify_group(self):
        """Create a group, search for it, then modify it."""
        # Create group
        group_data = self.data_generator.next_group_data()
        success, group_dn = self.udm_client.create_group(
            groupname=group_data['name'],
            description=group_data['description'],
        )

        if success and group_dn:
            add_created_group(group_dn)
            log.debug(f'Created group for mixed ops: {group_data["name"]}')

            # Search for the created group
            success, count = self.udm_client.search_objects(
                object_type='groups/group',
                position=self.containers['groups'],
                filter_expr=f'(cn={group_data["name"]})',
                name='mixed_search_created_group',
            )

            if success:
                log.debug(f'Found created group in search: {count} results')

            # Modify the group
            modifications = {
                'description': f'Modified in mixed ops at {int(time.time())}',
            }

            success = self.udm_client.modify_object(
                object_type='groups/group',
                object_dn=group_dn,
                modifications=modifications,
                name='mixed_modify_group',
            )

            if success:
                log.debug(f'Modified group in mixed ops: {group_dn}')

    @task(6)
    def search_and_retrieve_users(self):
        """Search for users then retrieve specific ones."""
        # Search for users
        success, results = self.udm_client.search_objects(
            object_type='users/user',
            position=self.containers['users'],
            filter_expr=get_ldap_filter('mixed_users'),
            limit=5,
            name='mixed_search_users',
        )

        if success and results:
            # Pick a random user from results and retrieve full details
            user_result = random.choice(results)
            user_dn = user_result.get('dn')

            if user_dn:
                success, _user_data = self.udm_client.get_object(
                    object_type='users/user',
                    object_dn=user_dn,
                    name='mixed_retrieve_user',
                )

                if success:
                    log.debug(f'Retrieved user from search results: {user_dn}')

    @task(6)
    def search_and_retrieve_groups(self):
        """Search for groups then retrieve specific ones."""
        # Search for groups
        success, results = self.udm_client.search_objects(
            object_type='groups/group',
            position=self.containers['groups'],
            filter_expr=get_ldap_filter('mixed_groups'),
            limit=5,
            name='mixed_search_groups',
        )

        if success and results:
            # Pick a random group from results and retrieve full details
            group_result = random.choice(results)
            group_dn = group_result.get('dn')

            if group_dn:
                success, _group_data = self.udm_client.get_object(
                    object_type='groups/group',
                    object_dn=group_dn,
                    name='mixed_retrieve_group',
                )

                if success:
                    log.debug(f'Retrieved group from search results: {group_dn}')

    @task(5)
    def bulk_operations_workflow(self):
        """Perform a series of bulk operations."""
        # Create multiple users quickly
        created_users = []
        for i in range(2):
            user_data = self.data_generator.next_user_data(password='Univention.123')
            success, user_dn = self.udm_client.create_user(
                username=user_data['username'],
                lastname=user_data['lastname'],
                password=user_data['password'],
                description=f'Bulk user {i + 1}',
            )

            if success and user_dn:
                add_created_user(user_dn)
                created_users.append(user_dn)

        # Search for all created users
        if created_users:
            success, count = self.udm_client.search_objects(
                object_type='users/user',
                position=self.containers['users'],
                filter_expr='(uid=mixed*)',
                name='mixed_bulk_search',
            )

            log.debug(f'Bulk search found {count} mixed users')

    @task(4)
    def concurrent_user_group_ops(self):
        """Perform user and group operations concurrently."""
        # Create user and group simultaneously (simulated)
        user_data = self.data_generator.next_user_data(password='Univention.123')
        group_data = self.data_generator.next_group_data()

        # Create user
        success_user, user_dn = self.udm_client.create_user(
            username=user_data['username'],
            lastname=user_data['lastname'],
            password=user_data['password'],
            description='Concurrent ops user',
        )

        # Create group
        success_group, group_dn = self.udm_client.create_group(
            groupname=group_data['name'],
            description='Concurrent ops group',
        )

        if success_user and user_dn:
            add_created_user(user_dn)
            log.debug(f'Created user in concurrent ops: {user_data["username"]}')

        if success_group and group_dn:
            add_created_group(group_dn)
            log.debug(f'Created group in concurrent ops: {group_data["name"]}')

    @task(3)
    def modify_and_retrieve_workflow(self):
        """Modify an object then immediately retrieve it."""
        user_dn = get_random_created_user()
        if user_dn:
            # Modify user
            timestamp = int(time.time())
            modifications = {
                'description': f'Modified then retrieved at {timestamp}',
            }

            success = self.udm_client.modify_object(
                object_type='users/user',
                object_dn=user_dn,
                modifications=modifications,
                name='mixed_modify_before_retrieve',
            )

            if success:
                # Immediately retrieve to verify modification
                success, _user_data = self.udm_client.get_object(
                    object_type='users/user',
                    object_dn=user_dn,
                    name='mixed_retrieve_after_modify',
                )

                if success:
                    log.debug(f'Modified and retrieved user: {user_dn}')

    @task(2)
    def cross_reference_operations(self):
        """Perform operations that cross-reference users and groups."""
        user_dn = get_random_created_user()
        group_dn = get_random_created_group()

        if user_dn and group_dn:
            # Get user details
            success, _user_data = self.udm_client.get_object(
                object_type='users/user',
                object_dn=user_dn,
                name='mixed_get_user_for_xref',
            )

            # Get group details
            success, _group_data = self.udm_client.get_object(
                object_type='groups/group',
                object_dn=group_dn,
                name='mixed_get_group_for_xref',
            )

            if success:
                log.debug(f'Cross-referenced user {user_dn} and group {group_dn}')

    @task(1)
    def error_handling_workflow(self):
        """Test error handling in mixed operations."""
        fake_dn = f'uid=nonexistent-{random.randint(1000, 9999)},cn=users,dc=test'

        # Try to get non-existent object
        _success, _user_data = self.udm_client.get_object(
            object_type='users/user',
            object_dn=fake_dn,
            name='mixed_error_get',
        )

        # Try to modify non-existent object
        self.udm_client.modify_object(
            object_type='users/user',
            object_dn=fake_dn,
            modifications={'description': 'Should fail'},
            name='mixed_error_modify',
        )

        log.debug('Completed error handling workflow')


if __name__ == '__main__':
    print('This script should be run with the Locust command:')
    print('locust -f 92_udm-rest-performance/07_mixed_operations.py --host https://master.ucs.test')
    print('\nOr for a quick test:')
    print('locust -f 92_udm-rest-performance/07_mixed_operations.py --host https://master.ucs.test -u 1 -t 30s --headless')
