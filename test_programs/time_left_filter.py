import re

data = ["3d 4h", "2h 42m", "7h", "6d", "50m"]
output_data = []

for val in data:
    time_left = 0.00
    times = re.findall(r"\d+[mdh]", val)
    for time in times:
        if time[-1] == 'd':
            time_left += int(time[:-1])*24
        if time[-1] == 'h':
            time_left += int(time[:-1])
        if time[-1] == 'm':
            time_left += int(time[:-1])/60
    time_left = round(time_left, 2)
    output_data.append(time_left)

print(output_data)

