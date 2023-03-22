import requests
from datetime import datetime
# from pyfirmata import Arduino, util
import time
from collections import deque
import json
    
weather_data = {}
def makeRequest():
    global weather_data
    weather_data = requests.get(
        'https://api.openweathermap.org/data/2.5/forecast?lat=63.7467&lon=-68.5170&appid=4f3bab7143c7c65017ab3d5b4bd1191e&units=metric'
        ).json()
    
# getting current windspeed
def getCurrentWind():
    
    weather = weather_data['list']
    weather_index_current = weather[1]
    currentwindspeed = weather_index_current['wind']
    currentwind = currentwindspeed['speed']
    return (currentwind)

# gets forecast for 4 days away
def getWind4Day():
    weather = weather_data['list']
    weather_index_4day = weather[5]
    unixdate4day = weather_index_4day['dt']
    date4day = datetime.fromtimestamp(unixdate4day)
    windspeed = weather_index_4day['wind']
    wind = windspeed['speed']
    return (wind)


##getting temp
def getTemp():
    weather = weather_data['list']
    weather_index_current = weather[1]
    tempurature = weather_index_current['main']
    temp = tempurature['temp']
    return (temp)


##to get weather type
def getWeather():
    weather = weather_data['list']
    weather_index_current = weather[1]
    status = weather_index_current['weather']
    index = status[0]
    desc = index['description']
    return (desc)


def getVis():
    weather = weather_data['list']
    weather_index_current = weather[1]
    vis = weather_index_current['visibility']
    return (vis)


def getBattery():
    battery = 80
    return battery


# getting cloud coverage %
def getCloud():
    weather = weather_data['list']
    weather_index_4day = weather[1]
    cldprcnt = weather_index_4day['clouds']
    cloud = cldprcnt['all']
    return (cloud)


# getting vis
def getVis():
    weather = weather_data['list']
    weather_index_current = weather[1]
    vis = weather_index_current['visibility']
    return (vis)


def sendMessage(SPmessage, Bmessage, Wmessage, FCmessage):
    print(SPmessage)
    print(Bmessage)
    print(Wmessage)
    print(FCmessage)
    return 0


def weatherControl():
    # heating controls
    temp = getTemp()
    weather = getWeather()
    
    if temp < 4 and weather == 'snow':
        SPmessage = "Heat Solar Pannels"
        Bmessage = "Heat Building"
    elif temp < 4 and weather == 'rain':
        SPmessage = "Heat Solar Pannels"
        Bmessage = "Heat Building"
    elif temp > 4 and weather != "snow":
        SPmessage = "Solar Pannel Heat Off"
        Bmessage = "Building Heat Off"
    else:
        SPmessage = weather
        Bmessage = temp
        
    # turbine controls
    wind = getCurrentWind()
    if wind > 90:
        Wmessage = "Wind Turbine Brakes On"
    else:
        wind = wind
        Wmessage = "Wind Turbine Brakes Off", wind
        
    # battery controls based on weather
    if getBattery() < 10 and (getCloud() > 50 or getWind4Day() < 15):
        FCmessage = "Use Diesel Engine"
    else:
        FCmessage = "Use Battery"

    sendMessage(SPmessage, Bmessage, Wmessage, FCmessage)


def processRadar(rad_dist, rad_deg):
    if rad_dist <= 80:
        x = sendLidar(rad_deg)
        return x
    else:
        x = "FAR"
        return x

def sendLidar(li_deg):
    # x = f"L,{li_dist},{li_deg}"
    x = f"L,{li_deg}"
    return x

def sendCamera():
    # threshold seems very low
    if getVis() < 0.1:
        x = False
        return x
    else:
        x = True
        return x




# get weather data
if __name__ == '__main__':
    
    makeRequest()
    
    """def getDate():
        weather_index_current = weather[1]
        unixdatecurrent = weather_index_current['dt']
        datecurrent = datetime.fromtimestamp(unixdatecurrent)
        return(datecurrent)"""
    # print(weather_data)
    JSON = json.dumps(weather_data)
    with open("arduino/weather.json", "w") as outfile:
        outfile.write(JSON)
else:
    
    makeRequest()
    # with open('arduino/weather.json', 'r') as openfile:
    #     # Reading from json file
    #     weather_data = json.load(openfile)
    

# queue = deque()
# lidarCheck = processRadar(radarDistance, radarAngle)
# if lidarCheck == 'FAR':
#     pass
# else:
#     data_list = lidarCheck.split(',')
#     distance = int(data_list[1].strip())
#     angle = int(data_list[2].strip())
#     lidar_array = [distance, angle]
#     queue.append(li_dist, li_deg)


# cameraCheck = sendCamera()
# if cameraCheck == True:
#     pass
#     #send to pi to turn on camera
# else:
#     pass
    #send to pit that vis is bad
    #double check with Lidar???


