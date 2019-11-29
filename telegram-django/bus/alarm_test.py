import re
import requests
from bs4 import BeautifulSoup as BS
from decouple import config

bus_key = config('BUS_KEY')

chat_id = '1234'
bus_list = {}
bus_number = {}
routeid_list = {}
routeid = {}
station_include = {}
user_msg = {}
station_list = {}

# 버스 번호입력 하세요
bus_number[chat_id] = '72'

url = f'http://ws.bus.go.kr/api/rest/busRouteInfo/getBusRouteList?serviceKey={bus_key}&strSrch={bus_number.get(chat_id)}'
url_result = requests.get(url).text
soup = BS(url_result, 'html.parser')
bus_list[chat_id] = soup.find('msgbody')
print('bus_list=', str(bus_list.get(chat_id)))
if str(bus_list.get(chat_id)) == '<msgbody></msgbody>':
    print('tttttt')


# 버스 리스트 출력
msg = '버스를 선택하세요'
routeid_list[chat_id] = []
if len(bus_number.get(chat_id)) < 2:
    idx = 0
    for bus in bus_list.get(chat_id):
        if bus.find("busroutenm").contents[0] == bus_number.get(chat_id) or bus.find("busroutenm").contents[0] == '0'+bus_number.get(chat_id):
            msg += f'\n{idx + 1}. 버스 : {bus.find("busroutenm").contents[0]} / {bus.find("ststationnm").contents[0]}<->{bus.find("edstationnm").contents[0]}'
            routeid_list[chat_id].append(bus.find('busrouteid').contents[0])
            idx += 1

else:
    for idx, bus in enumerate(bus_list.get(chat_id)):
        msg += f'\n{idx + 1}. 버스 : {bus.find("busroutenm").contents[0]} / {bus.find("ststationnm").contents[0]}<->{bus.find("edstationnm").contents[0]}'
        routeid_list[chat_id].append(bus.find('busrouteid').contents[0])
print(msg)
print(routeid_list)

# 버스 선택
idx = 0
routeid[chat_id] = routeid_list[chat_id][idx]

# 탑승 정류장 입력
user_msg[chat_id] = '사'
station_include[chat_id] = []

url = f'http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute?serviceKey={bus_key}&busRouteId={routeid.get(chat_id)}'
url_result = requests.get(url).text
soup = BS(url_result, 'html.parser')

stations = soup.find('msgbody') ##
station_list[chat_id] = list(stations)

index = 0

for idx, station in enumerate(station_list.get(chat_id)):  # 정류장리스트에서 입력받은 단어가 포함된 정류장 찾기 ##
    if user_msg.get(chat_id) in station.find('stationnm').contents[0]:
        if idx < len(station_list.get(chat_id)) - 1:
            station_include[chat_id].append([])
            station_include[chat_id][index].append(station.find('station').contents[0])
            station_include[chat_id][index].append(station.find('stationnm').contents[0])
            station_include[chat_id][index].append(station_list.get(chat_id)[idx + 1].find('stationnm').contents[0])
            station_include[chat_id][index].append(station.find('seq').contents[0])
            index += 1


print(station_include[chat_id])
msg = '정류장을 선택하세요'
for idx, station in enumerate(station_include.get(chat_id)):
    # if idx < len(station_include.get(chat_id)):
    msg += f'\n{idx + 1}. {station[1]}  ->  {station[2]}'

print(msg)

## 버스 알림 테스트해보기
station_id = station_include[chat_id][0][0]
route_id = routeid[chat_id]
station_order = station_include[chat_id][0][3]

print(station_id, route_id, station_order)

url = f'http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={bus_key}&stId={station_id}&busRouteId={route_id}&ord={station_order}'
request = requests.get(url).text
soup = BS(request, 'html.parser')

bus1 = soup.find('arrmsg1').contents[0]
bus2 = soup.find('arrmsg2').contents[0]

bus1 = '28분11초후[13번째 전]'
# bus1 = '곧 도착'
if bus1.find('분') != -1:
    bus1_minute = bus1[:bus1.find('분')]
    bus1_location = bus1[bus1.find('[')+1:bus1.find('번')]
print(bus1)
print(type(bus1_minute))
print(bus1_location)



test1 = '출근 버스 10분전에 알려줘'
test2 = '출근 버스 3분마다 알려줘'
print(('전' in test1))
print(('마다' in test2))
if '전' in test1:
    print('전')
if '마다' in test2:
    print('마다')
