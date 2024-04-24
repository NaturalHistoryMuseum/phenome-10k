## v2.2.0 (2024-04-24)

### Feature

- self signed certificates, letsencrypt updates, etc

## v2.1.1 (2024-04-09)

### Fix

- set existing columns to 1 not 't'

## v2.1.0 (2024-04-09)

### Feature

- update the gbif taxonomy script

### Build System(s)

- add letsencrypt tasks
- update virtual ip
- add maintenance page
- add .well-known folder
- align nginx configs
- add root mysql config earlier

### Chores/Misc

- fix versions

## v2.0.0 (2024-04-04)

### Fix

- fix subnet address on docker config
- use a compatible version of node-sass

### Docs

- update readme

### Style

- reformat ansible yaml
- unignore and reformat build scripts
- run pre-commit on ansible files
- run pre-commit on frontend files
- run pre-commit on api files

### Build System(s)

- get server ips from vault
- update production servers
- switch server OS to ubuntu
- remove separate install of flower
- explicitly add nginx user to lb image
- add data migration to upsert tag data
- use p10k cli script name
- move requirements into separate file again
- update node docker image
- add cli script to pyproject.toml
- move commitizen config to root
- add black args to pc config
- use mariadb and jammy for db docker
- use jammy for lb docker
- add pre-commit
- migrate to pyproject.toml
- update python images

### Chores/Misc

- add workflow files (bump and sync)
- delete some old files

## v1.0.0 (2023-04-26)

### Fix

- add password salt env var
- add phpass to security config

### Build System(s)

- increase monit disk space check to 90GB
