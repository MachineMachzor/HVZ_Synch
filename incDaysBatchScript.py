import requests



url = "http://127.0.0.1:8000/incDaysEveryday"
payload = {
	"webPass": "t2]9k4%,AyW$k}fU"
}
resp = requests.post(url, json=payload)
print(resp.text)