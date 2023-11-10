# Word track

Service for learning foreign words

## How to deploy

```shell
cp data/.env.example data/.env
vim data/.env
task build
task start
```

See logs

```shell
task logs
```

Remove containers

```shell
task remove
```

### Create User

```shell
docker compose run wordtrack_app python manage.py createsuperuser
```

## Develop

```shell
task format
task lint
task tests
tasl all
```

## Backup

open crontab

```bash
sudo vim /etc/crontab
```

Add this to run backup every night at 00:00

```bash
0  0    * * *   www     /home/www/deploy/wordtrack/backup.sh >> /home/www/wordtrack_backup_cron.log 2>&1
```
