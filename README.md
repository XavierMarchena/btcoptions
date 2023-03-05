# Btcoptions

Btcoptions is a Python game.

## Configuration

Clone repository 
```bash
git clone URL
```
Configure environment variables
```bash
/bitcoinbet/back/Settings/settings.cfg
```

## Build and run DEVELOPMENT environment container

```bash
docker-compose -f dev-docker-compose.yml up -d
```

## Build and run PRODUCTION environment container

```bash
docker-compose -f docker-compose.yml up -d
```

## Running frontend DEVELOPMENT server
```bash
ng serve
```
## Building frontend for PRODUCTION 
```bash
ng build --prod --base-href /btcoptions/
```


## Common DEVELOPMENT commands
```bash
docker cp btcoptions_leviathan_bitcoinbet_1:/bitcoinbet/back/Core/Core.celery.logs Core.celery.logs

docker exec -ti  btcoptions_leviathan_mongodb_1 sh
mongo --username btcoptions_user --password --authenticationDatabase admin
```
