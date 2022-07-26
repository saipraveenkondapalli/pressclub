import requests

url = "https://dnaber-languagetool.p.rapidapi.com/v2/check"
payload = "language=en-US&text=" + "I am a student"
headers = {
	"content-type": "application/x-www-form-urlencoded",
	"X-RapidAPI-Key": "f207bf137bmshcb3d1d7cd29b679p15cb47jsn9514fc0f36ba",
	"X-RapidAPI-Host": "dnaber-languagetool.p.rapidapi.com"
}

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)