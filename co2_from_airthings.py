import csv

data = []
with open("data/mh270_new.csv", "r") as csvfile:
    reader = csv.reader(csvfile)
    for lines in reader:
        data.append(lines)
data = data[1 : len(data)]

date = []
time = []
co2 = []
humidity = []

sample_data = [["2024-11-11T21:30:00;;;250;;;;;"]]
for row in data:
    inx_sc = []
    time_sep = 0
    r = row[0]
    for i, char in enumerate(r):
        if char == "T":
            time_sep = i
        if char == ";":
            inx_sc.append(i)
    # for other readings, use this code block (the list and the if statement) and adjust accordingly
    # the order for which inx_sc to use is:
    # Radon ; PM2.5 ; Co2 ; Humidity ; Temp ; VOC ; Pressure ; PM1.0
    co2_reading = r[inx_sc[2] + 1 : inx_sc[3]]
    humidity_reading = r[inx_sc[3] + 1 : inx_sc[4]]
    if (
        co2_reading != "" or humidity_reading != ""
    ):  # the more variables you add, the more gaps in data you will get, change the or to and if you want cleaner (but less) data
        date.append(r[0:time_sep])
        time.append(r[time_sep + 1 : inx_sc[0]])
        co2.append(co2_reading)
        humidity.append(humidity_reading)


print(f"date:{date} time:{time} co2:{co2} humidity{humidity}")

with open("mh270_cleaned.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Write the header row
    writer.writerow(["Date", "Time", "CO2", "Humidity"])

    # Write the data rows
    for dates, times, co2s, humidities in zip(date, time, co2, humidity):
        writer.writerow([dates, times, co2s, humidities])
