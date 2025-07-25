#!/usr/share/ucs-test/runner /usr/share/ucs-test/locust-docker GroupSearchTest
# /usr/share/ucs-test/runner /usr/share/ucs-test/locust --spawn-rate 20 -u 20 -t 2m --csv GroupSearch --html GroupSearch.html GroupSearchTest
## desc: "UDM REST API performance test for group search operations"
## exposure: safe
## tags: [producttest, SKIP]
## roles: [domaincontroller_master,domaincontroller_backup,domaincontroller_slave,memberserver]
## env:
##   LOCUST_SPAWN_RATE: "20"
##   LOCUST_RUN_TIME: "2m"
##   LOCUST_USERS: "20"
##   LOCUST_USER_CLASSES: GroupSearchTest
##   WAIT_MIN: "0"
##   WAIT_MAX: "0"
##   TIMEOUT: "300"

import random

from locust import HttpUser, between, task
from rest_utils import (
    UDMRestClient, UDMTestDataGenerator, get_config, get_ldap_containers, get_ldap_filter, setup_logging,
)


# Configuration
WAIT_MIN = get_config('WAIT_MIN', 1)
WAIT_MAX = get_config('WAIT_MAX', 3)

# Setup logging
log = setup_logging()


class GroupSearchTest(HttpUser):
    wait_time = between(WAIT_MIN, WAIT_MAX)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.udm_client = None
        self.data_generator = None
        self.containers = None

    def on_start(self):
        """Initialize session with UDM client and data generator."""
        self.udm_client = UDMRestClient(self.client)
        self.data_generator = UDMTestDataGenerator(prefix='groupsearch')
        self.containers = get_ldap_containers()
        log.info('Group search test started')

    def on_stop(self):
        """Clean up created objects."""
        if self.udm_client:
            self.udm_client.cleanup_created_objects()
        log.info('Group search test stopped')

    @task(15)
    def search_all_groups(self):
        """Search for all groups."""
        success, count = self.udm_client.search_objects(
            object_type='groups/group',
            position=self.containers['groups'],
            filter_expr=get_ldap_filter('all_groups'),
            name='search_all_groups',
        )

        if success:
            log.debug(f'Found {count} groups')

    @task(10)
    def search_groups_with_limit(self):
        """Search for groups with limit."""
        limit = random.choice([10, 20, 50])
        success, count = self.udm_client.search_objects(
            object_type='groups/group',
            position=self.containers['groups'],
            filter_expr=get_ldap_filter('all_groups'),
            limit=limit,
            name='search_groups_with_limit',
        )

        if success:
            log.debug(f'Found {count} groups (limit: {limit})')

    @task(8)
    def search_groups_filtered(self):
        """Search for groups with filter."""
        success, count = self.udm_client.search_objects(
            object_type='groups/group',
            position=self.containers['groups'],
            filter_expr=get_ldap_filter('perftest_groups'),
            limit=20,
            name='search_groups_filtered',
        )

        if success:
            log.debug(f'Found {count} filtered groups')

    @task(6)
    def search_groups_by_name_pattern(self):
        """Search for groups by name pattern."""
        patterns = ['admin*', '*users*', 'test*', '*service*']
        pattern = random.choice(patterns)

        success, count = self.udm_client.search_objects(
            object_type='groups/group',
            position=self.containers['groups'],
            filter_expr=f'(cn={pattern})',
            name='search_groups_by_pattern',
        )

        if success:
            log.debug(f'Found {count} groups matching pattern: {pattern}')

    @task(5)
    def bulk_search_groups(self):
        """Search for many groups with pagination."""
        success, count = self.udm_client.search_objects(
            object_type='groups/group',
            position=self.containers['groups'],
            filter_expr=get_ldap_filter('all_groups'),
            limit=100,
            name='bulk_search_groups',
        )

        if success:
            log.debug(f'Bulk search found {count} groups')

    @task(4)
    def search_security_groups(self):
        """Search for security groups."""
        success, count = self.udm_client.search_objects(
            object_type='groups/group',
            position=self.containers['groups'],
            filter_expr='(sambaGroupType=2)',
            name='search_security_groups',
        )

        if success:
            log.debug(f'Found {count} security groups')

    @task(3)
    def search_groups_with_members(self):
        """Search for groups that have members."""
        success, count = self.udm_client.search_objects(
            object_type='groups/group',
            position=self.containers['groups'],
            filter_expr='(member=*)',
            name='search_groups_with_members',
        )

        if success:
            log.debug(f'Found {count} groups with members')

    @task(2)
    def search_recently_created_groups(self):
        """Search for recently created groups."""
        success, count = self.udm_client.search_objects(
            object_type='groups/group',
            position=self.containers['groups'],
            filter_expr='(&(cn=groupsearch*)(createTimestamp>=20240101000000Z))',
            name='search_recent_groups',
        )

        if success:
            log.debug(f'Found {count} recently created groups')

    @task(1)
    def search_distribution_groups(self):
        """Search for distribution groups."""
        success, count = self.udm_client.search_objects(
            object_type='groups/group',
            position=self.containers['groups'],
            filter_expr='(sambaGroupType=8)',
            name='search_distribution_groups',
        )

        if success:
            log.debug(f'Found {count} distribution groups')


if __name__ == '__main__':
    print('This script should be run with the Locust command:')
    print('locust -f 92_udm-rest-performance/04_group_search.py --host https://master.ucs.test')
    print('\nOr for a quick test:')
    print('locust -f 92_udm-rest-performance/04_group_search.py --host https://master.ucs.test -u 1 -t 30s --headless')
