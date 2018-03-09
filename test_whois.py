from whois import parse_mikrotik_data, last_seen_to_timestamp
from datetime import datetime
# import sqlite3

# class mock_db():
#     """docstring for mock_db"""
#     def __init__(self):
#         pass

#     def __enter__(self):
#         self.db = sqlite3.connect('tmpdb.db')
#         c = self.db.cursor()
#         c.execute('''CREATE TABLE device
#              (lastseen text, mac text, hostname text, claim)''')
#         self.db.commit()

#         return self.db

#     def __exit__(self, type, value, traceback):
#         self.db.close()




# def test_mock_insert():
#     with mock_db() as conn:
#         c = conn.cursor()
#         c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")
#         conn.commit()

#     conn.close()


# @freeze_time("2012-01-01")
def test_last_seen_to_timestamp():
    dt_now = datetime(2017, 2, 10, 20, 15, 30)
    assert last_seen_to_timestamp(dt_now, "1w") == datetime(2017, 2, 3, 20, 15, 30).timestamp()
    assert last_seen_to_timestamp(dt_now, "6d12h") == datetime(2017, 2, 4, 8, 15, 30).timestamp()
    assert last_seen_to_timestamp(dt_now, "30m10s") == datetime(2017, 2, 10, 19, 45, 20).timestamp()
    assert last_seen_to_timestamp(dt_now, "1w2d13h1m15s") == datetime(2017, 2, 1, 7, 14, 15).timestamp()


def test_parse_mikrotik_data():

    data = [{"mac":"11:22:33:44:55:66","name":"Dom","last":"50w6d16h1m10s","status":"waiting"},{"mac":"AA:BB:CC:DD:EE:FF","name":"HS","last":"4d1h58m8s","status":"bound"}]
    result = parse_mikrotik_data(data)

    print(list(result))

    assert result == [("11:22:33:44:55:66", )]
