from datetime import datetime, timedelta

now = datetime.today()
day = now.weekday()
startDate = datetime.strptime(now.strftime("%Y-%m-%d"), "%Y-%m-%d")
weekDate = []
if (day != 0):
    startDate = startDate - timedelta(days=day)

for i in range(0, 7):
    date = startDate + timedelta(days=i)
    weekDate.append(date)


def dateToStr (date, pattern) :
    stringified = date.strftime(pattern)
    return stringified

print(dateToStr(now, "%Y-%m-%d"))