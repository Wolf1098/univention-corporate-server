#!/usr/share/ucs-test/runner /usr/share/ucs-test/locust-docker GroupCreationTest
# /usr/share/ucs-test/runner /usr/share/ucs-test/locust --spawn-rate 20 -u 20 -t 2m --csv GroupCreation --html GroupCreation.html GroupCreationTest
## desc: "UDM REST API performance test for group creation operations"
## exposure: safe
## tags: [producttest, SKIP]
## roles: [domaincontroller_master,domaincontroller_backup,domaincontroller_slave,memberserver]
## env:
##   LOCUST_SPAWN_RATE: "20"
##   LOCUST_RUN_TIME: "2m"
##   LOCUST_USERS: "20"
##   LOCUST_USER_CLASSES: GroupCreationTest
##   WAIT_MIN: "0"
##   WAIT_MAX: "0"
##   TIMEOUT: "300"

from locust import HttpUser, between, task
from rest_utils import (
    UDMRestClient, UDMTestDataGenerator, add_created_group, get_config, get_ldap_containers, setup_logging,
)


# Configuration
WAIT_MIN = get_config('WAIT_MIN', 1)
WAIT_MAX = get_config('WAIT_MAX', 3)

# Setup logging
log = setup_logging()


class GroupCreationTest(HttpUser):
    wait_time = between(WAIT_MIN, WAIT_MAX)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.udm_client = None
        self.data_generator = None
        self.containers = None

    def on_start(self):
        """Initialize session with UDM client and data generator."""
        self.udm_client = UDMRestClient(self.client)
        self.data_generator = UDMTestDataGenerator(prefix='groupcreation')
        self.containers = get_ldap_containers()
        log.info('Group creation test started')

    def on_stop(self):
        """Clean up created objects."""
        if self.udm_client:
            self.udm_client.cleanup_created_objects()
        log.info('Group creation test stopped')

    @task(10)
    def create_group(self):
        """Create a new group."""
        group_data = self.data_generator.next_group_data()

        success, group_dn = self.udm_client.create_group(
            groupname=group_data['name'],
            description=group_data['description'],
        )

        if success and group_dn:
            add_created_group(group_dn)
            log.info(f'Created group: {group_data["name"]}')

    @task(2)
    def create_bulk_groups(self):
        """Create multiple groups in quick succession."""
        for i in range(3):
            group_data = self.data_generator.next_group_data()

            success, group_dn = self.udm_client.create_group(
                groupname=group_data['name'],
                description=f'Bulk group {i + 1} - {group_data["description"]}',
            )

            if success and group_dn:
                add_created_group(group_dn)
                log.debug(f'Created bulk group {i + 1}: {group_data["name"]}')


if __name__ == '__main__':
    print('This script should be run with the Locust command:')
    print('locust -f 92_udm-rest-performance/02_group_creation.py --host https://master.ucs.test')
    print('\nOr for a quick test:')
    print('locust -f 92_udm-rest-performance/02_group_creation.py --host https://master.ucs.test -u 1 -t 30s --headless')
