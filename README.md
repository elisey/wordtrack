# Word track

Service for learning foreigh words


```shell
docker compose run wordtrack_app python manage.py createsuperuser
```

### Backup

open crontab

```bash
sudo vim /etc/crontab
```

Add this to run backup every night at 00:00

```bash
0  0    * * *   www     /home/www/deploy/wordtrack/backup.sh >> /home/www/wordtrack_backup_cron.log 2>&1
```
