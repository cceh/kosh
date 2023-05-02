---
layout: default
title: Synchronization
nav_order: 5
---

# Syncing Kosh with GIT remote repositories

{: .no_toc}

If you modify any file part of a Kosh data module (.kosh file, XML files or JSON config file), Kosh per default automatically updates the respective index.
Therefore if you wish to synchronize your local Kosh instance with data from a GIT repository, we present you two alternatives:

1. TOC
{:toc}

## Kosh Sync

You can use <a href="https://www.github.com/cceh/kosh_sync">Kosh Sync</a>, a Docker container, to synchronize local datasets with their
respective cloud repository.

Setup:

1. Clone kosh_sync:

```bash
$ git clone https://github.com/cceh/kosh_sync
```

2. Modify `docker-compose.sync.yml` to your requirements:

```dockerfile
version: '2.3'
services:
 sync:
    build: ../kosh_sync
    networks: ['network']
    volumes: ['ABS_PATH_TO_LOCAL_GIT_REPO:/var/lib/kosh']
    depends_on:
      kosh:
        condition: service_healthy
    environment:
      KOSH_SYNC_BRANCH: master
      KOSH_SYNC_ORIGIN: URL_REPO
      KOSH_SYNC_REPOSE: 1h
      
 ```

`KOSH_SYNC_REPOSE`, the time-interval used to call the external GIT repo, is set here to one hour (1h). You can employ the following values: (s)econds, (m)inutes, (h)ours, or (d)ays.

Deploy Kosh Sync together with Kosh:

 ```bash
$ docker-compose -f docker-compose.yml -f docker-compose.local.yml -f [PATH_TO_KOSH_SYNC]/docker-compose.sync.yml up -d
 ```

## Cron job

In order to automatically check for updates, in Unix-like systems you can create a cron job:

 ```bash
$ crontab -e
 ```

For checking for updates daily at 23:00

```
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command
55 23 * * * cd ABS_PATH_TO_LOCAL_GIT_REPO && git pull
```
