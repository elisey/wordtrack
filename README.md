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
task test
tasl all
```

