import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.text import slugify
from pulp_ansible.app.models import (
    AnsibleDistribution,
    AnsibleRepository,
    CollectionRemote,
)
from pulp_ansible.app.tasks.utils import parse_collections_requirements_file
from rest_framework.serializers import ValidationError

from galaxy_ng.app.constants import COMMUNITY_DOMAINS


class Command(BaseCommand):
    """Django management command for creating new remotes.

    Example:

    $ create-remote rh-certified https://cloud.redhat.com/api/automation-hub/v3/collections

    $ create-remote community https://galaxy.ansible.com -r /tmp/reqs.yaml

    """

    status_messages = []

    def load_requirements_file(self, requirements_file):
        """Loads  and validates the requirements file

        If the requirements_file is an absolute path for a file it is
        opened and read.
        """
        if os.path.exists(requirements_file) and requirements_file.endswith((".yaml", ".yml")):
            with open(requirements_file) as file_obj:
                requirements_file = file_obj.read()

        try:
            parse_collections_requirements_file(requirements_file)
        except ValidationError as e:
            raise CommandError("Error parsing requirements_file {}".format(str(e)))
        else:
            self.status_messages.append("requirements_file loaded and parsed")

        return requirements_file

    def valid_url(self, url):
        if url.endswith("/"):
            raise CommandError("url should not end with '/'")
        return url

    def add_arguments(self, parser):
        # required positional arguments
        parser.add_argument('name', type=slugify, help="Remote Name")
        parser.add_argument(
            "url",
            type=self.valid_url,
            help=(
                "Remote Feed URL, "
                "Should not end with a '/', "
                "should end in v2/collections or v3/collections"
            )
        )

        # optional named arguments
        parser.add_argument("--token", type=str, help="Remote Auth Token")
        parser.add_argument("--policy", type=str, help="Remote Download Policy")
        parser.add_argument("--auth_url", type=str, help="Remote Auth URL")
        parser.add_argument(
            "--repository",
            type=slugify,
            help="Name of a repository to create or associate, defaults to [name]"
        )
        parser.add_argument(
            "--distribution",
            type=slugify,
            help="Name of a distribution to create or associate, defaults to [name]"
        )
        parser.add_argument(
            "-r",
            "--requirements_file",
            type=self.load_requirements_file,
            help="Either an abs path ending in .yaml|.yml to be loaded or the literal YAML string."
        )

    def validate(self, data):
        if not data["requirements_file"] and any(
            [domain in data["url"] for domain in COMMUNITY_DOMAINS]
        ):
            raise CommandError(
                'Syncing content from community domains without specifying a '
                'requirements file is not allowed.'
            )
        return data

    def create_remote(self, data):
        try:
            remote = CollectionRemote.objects.create(
                name=data["name"],
                url=data["url"],
                auth_url=data["auth_url"],
                token=data["token"],
                requirements_file=data["requirements_file"]
            )
        except IntegrityError as e:
            raise CommandError("Cannot create {} remote, error: {}".format(data["name"], str(e)))
        else:
            self.status_messages.append("Created new CollectionRemote {}".format(remote.name))

        return remote

    def create_repository(self, data, remote):
        repository, repo_created = AnsibleRepository.objects.get_or_create(
            name=data["repository"] or data["name"]
        )
        if repository.remote:
            raise CommandError(
                "Repository {} is already associated with a remote {}".format(
                    repository.name, repository.remote.name
                )
            )

        repository.remote = remote
        repository.save()
        self.status_messages.append(
            "{} Repository {}".format(
                "Created new" if repo_created else "Associated existing",
                repository.name,
            )
        )
        return repository

    def create_distribution(self, data, remote, repository):
        distribution, distro_created = AnsibleDistribution.objects.get_or_create(
            name=data["distribution"] or data["name"],
            base_path=data["distribution"] or data["name"],
        )
        if distribution.repository:
            raise CommandError(
                "Distribution {} is already associated with a repository {}".format(
                    distribution.name, distribution.repository.name
                )
            )

        if distribution.remote:
            raise CommandError(
                "Distribution {} is already associated with a remote {}".format(
                    distribution.name, distribution.remote.name
                )
            )

        distribution.repository = repository
        distribution.remote = remote
        distribution.save()
        self.status_messages.append(
            "{} Distribution {}".format(
                "Created new" if distro_created else "Associated existing",
                distribution.name,
            )
        )
        return distribution

    def handle(self, *args, **data):
        data = self.validate(data)

        with transaction.atomic():
            remote = self.create_remote(data)
            repository = self.create_repository(data, remote)
            self.create_distribution(data, remote, repository)

        # only outputs success messages if transaction is succesful
        for message in self.status_messages:
            self.stdout.write(message)
