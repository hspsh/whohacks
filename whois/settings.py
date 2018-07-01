# mikrtotik ip, or other reporting devices
name = "at.hs3.pl"
whitelist = ["192.168.88.1"]
host = "0.0.0.0"
user_flags = {1: "hidden", 2: "name_anonymous"}
device_flags = {1: "hidden", 2: "new", 4: "infrastructure", 8: "esp", 16: "laptop"}

recent_time = {"minutes": 20}
log_frequency_time = {"hours": 1, "minutes": 0, "seconds": 0}

# production
ip_mask = "192.168.88.1-255"
# TODO: better way for handling dev env
# ip_mask = "127.0.0.1"
