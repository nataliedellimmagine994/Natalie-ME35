import urequests
url = "https://worldtimeapi.org/api/timezone/America/New_York"
reply = urequests.get(url)
print(reply.json()['datetime'])