import re

data = ["12.20", "10.02 to 1204.12"]

for val in data:
    print(re.findall(r"\d+\.\d+", val))
