import peewee
from playhouse.reflection import print_table_sql

from whois.database import Device, User


def print_schema():
    for model in [Device, User]:
        print_table_sql(model)
        print(";")


if __name__ == "__main__":
    print_schema()
