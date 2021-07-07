# Neptune administrative utils
A collection of scripts designed to programmatically administrate organizations and users in https://neptune.ai/

## Installation
To install required packages in your environment (Python>=3.6):
```
pip install -r requirements.txt
```

## Available commands

### Invite a member into an organization
```
./manage_users.py invite <ORGANIZATION-NAME> --invitee-email <EMAIL> --admin-api-token <TOKEN>
```

### Remove member from an organization
```
./manage_users.py remove <ORGANIZATION-NAME> --removed-username <USERNAME> --admin-api-token <TOKEN>
```
