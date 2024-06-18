import httpx
import json

openweahtermap = "https://api.openweathermap.org/data/2.5/weather?"
location = "lat=&lon=&" #lat and lon of your home 
key = "appid=" #your own key
weather_addr = f"{openweahtermap}{location}{key}"

class httpClient():

    def __init__(self):
        pass

    def post_wled_json(self, addr="http://192.168.100.128/json", data=None):
        json_data = json.loads(data)
        httpx.post(addr, json=json_data)
    
    def get_wled_json(self, addr="http://192.168.100.128/json/state"):
        r = httpx.get(addr)
        return r.json()
    
    def get_weather(self, addr=weather_addr):
        r = httpx.get(addr)
        return r.json()