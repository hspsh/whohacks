# Development

## Migrations

If you make changes to the database schema, you need to generate a new migration.
To do this you need to install [atlas](https://atlasgo.io/).

```shell
atlas migrate diff --env=local <migration name>
```
