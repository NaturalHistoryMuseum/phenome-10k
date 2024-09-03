## v2.6.1 (2024-09-03)

### Fix

- update node-sass to v9

### Build System(s)

- remove -get from apt-get update

## v2.6.0 (2024-09-02)

### Feature

- compress rpc json payload

### Performance

- display taxonomy tree to family level
- reduce scans per page to 50
- also cache the tag tree, but only for 1 day at a time

### Build System(s)

- update mmonit version
- update to node v20

### Chores/Misc

- ignore dist files

## v2.5.0 (2024-08-20)

### Feature

- add command to clear cache

### Performance

- add flask-caching and cache taxonomy tree output
- use 9 workers, remove threads

### Build System(s)

- add logrotate config to ansible

## v2.4.2 (2024-07-30)

### Fix

- use safe_join from werkzeug
- add catch for broken images
- make height an int too

### Build System(s)

- remove obsolete docker compose version specifier

### Chores/Misc

- ignore logs generated during development

## v2.4.1 (2024-07-29)

### Fix

- make default log level configurable

### Build System(s)

- increase timeout for gunicorn
- adjust threads for gunicorn

## v2.4.0 (2024-07-26)

### Feature

- configure flask logging to file

## v2.3.1 (2024-05-02)

### Fix

- fix reference to scan object in feed template

### Build System(s)

- update some python deps
- update minor versions of node deps and rebuild lock file

## v2.3.0 (2024-04-25)

### Feature

- add robots.txt
- add config to block certain useragents

### Fix

- remove file that never actually got used

### Chores/Misc

- remove standard comments and unused sections from nginx config

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
