data "external_schema" "peewee" {
  program = [
    "helpers/db_schema.sh"
  ]
}

env "local" {
  src = data.external_schema.peewee.url
  dev = "sqlite://dev?mode=memory"
  url = "sqlite://whoisdevices.db"

  migration {
    dir = "file://migrations"
  }

  format {
    migrate {
      diff = format("{{ sql .  \" \" }}")
    }
  }
}
