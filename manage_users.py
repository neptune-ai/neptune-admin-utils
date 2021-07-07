#!/usr/bin/env python3

import uuid
from typing import List

import click
import backoff
from bravado.exception import HTTPConflict, HTTPError

from neptune.new.internal.backends.hosted_neptune_backend import HostedNeptuneBackend
from neptune.new.internal.credentials import Credentials


class Invitation:
    def __init__(self, _uuid: uuid.UUID, invitee: str):
        self.uuid = _uuid
        self.invitee = invitee


@backoff.on_exception(backoff.expo, HTTPError, max_tries=5)
def invite_member(backend, organization, invitee) -> List[Invitation]:
    payload = {
        "organizationIdentifier": organization,
        "invitationsEntries": [
            {
                "invitee": invitee,
                "invitationType": "emailRecipient",
                "roleGrant": "member",
                "addToAllProjects": False
            }
        ]
    }

    try:
        response = backend.backend_client.api.createOrganizationInvitations(
            newOrganizationInvitations=payload,
            **backend.DEFAULT_REQUEST_KWARGS)\
            .response()
    except HTTPConflict:
        click.echo(f"ERROR: Pending invitation for '{invitee}'")
        return []

    return list(map(lambda r: Invitation(_uuid=r.id, invitee=r.invitee), response.result.invitations or []))


@backoff.on_exception(backoff.expo, HTTPError, max_tries=5)
def remove_member(backend: HostedNeptuneBackend, organization: str, username: str):
    backend.backend_client.api.deleteOrganizationMember(
        organizationIdentifier=organization,
        userId=username,
        **backend.DEFAULT_REQUEST_KWARGS)\
        .response()

    click.echo(f"Removed '{username}' from organization '{organization}'")


@click.group()
def cli():
    pass


@cli.command()
@click.argument('organization')
@click.option('--invitee-email', 'email', help='Email to invite')
@click.option('--admin-api-token', envvar='NEPTUNE_API_TOKEN', help='API Token for organization Admin')
def invite(admin_api_token, email, organization):
    credentials = Credentials(api_token=admin_api_token)
    config_api_url = credentials.api_url_opt or credentials.token_origin_address
    backend = HostedNeptuneBackend(credentials=credentials)

    invitations = invite_member(backend=backend, organization=organization, invitee=email)

    for invitation in invitations:
        click.echo(f"{config_api_url}/-/invitations/organization/{invitation.uuid}")


@cli.command()
@click.argument('organization')
@click.option('--removed-username', 'username', help='User to removal')
@click.option('--admin-api-token', envvar='NEPTUNE_API_TOKEN', help='API Token for organization Admin')
def remove(admin_api_token, username, organization):
    credentials = Credentials(api_token=admin_api_token)
    backend = HostedNeptuneBackend(credentials=credentials)

    remove_member(backend=backend, organization=organization, username=username)


if __name__ == '__main__':
    cli()
