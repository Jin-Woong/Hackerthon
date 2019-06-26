import re
import requests
from bs4 import BeautifulSoup as BS
import time

bus_number = re.findall('\d+-?\d+', '1')
print(bus_number)
print(not bus_number)

# test = {}
# chat_id = 1234
# st_list = ['1','2','3']
#
# test[chat_id] = []
# test[chat_id].append([])
# test[chat_id][0].append('1')
# test[chat_id][0].append('2')
#
# test[chat_id].append([])
# test[chat_id][1].append('ㅁ')
# test[chat_id][1].append('ㄴ')

chat_id = 123
routeid = {}
station_list = {}
user_msg = {}
station_include = {}
routeid[chat_id] = '232000029'
user_msg[chat_id] = '강화'

url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice/station?serviceKey=p7RiOnONfT8hc4MMVfKU8%2BSr2pQ8vwgM3JQA0sap60em7nJZW5QpGUrGcDmQy4nqe%2B1YxAOAwL7F1uRrlk8PkQ%3D%3D&routeId={routeid.get(chat_id)}'
url_result = requests.get(url).text
soup = BS(url_result, 'html.parser')

stations = soup.find('msgbody')  ##
station_list[chat_id] = list(stations)
# print(stations)
# print(station_list.get(chat_id))

# for idx, station in enumerate(station_list.get(chat_id)):  # 정류장리스트에서 입력받은 단어가 포함된 정류장 찾기 ##
#     if user_msg.get(chat_id) in station.find('stationname').contents[0]:
#         print(station.find('stationname').contents[0])

index = 0
            # station_list = list(station_list)
# station_include[chat_id] = []
# for idx, station in enumerate(station_list.get(chat_id)):  # 정류장리스트에서 입력받은 단어가 포함된 정류장 찾기 ##
#     if user_msg.get(chat_id) in station.find('stationname').contents[0]:
#         if idx < len(station_list.get(chat_id)) - 1:
#             station_include[chat_id].append([])
#             station_include[chat_id][index].append(station.find('stationid').contents[0])
#             station_include[chat_id][index].append(station.find('stationname').contents[0])
#             station_include[chat_id][index].append(station_list.get(chat_id)[idx + 1].find('stationname').contents[0])
#             station_include[chat_id][index].append(station.find('stationseq').contents[0])
#         index += 1
# print(station_include)

# if not station_include.get(chat_id):
#     print('없음')
#
# if not station_include.get(chat_id):  # 일치하는 정류장이 하나도 없는 경우
#     msg = '입력한 단어가 포함된 정류장이 없습니다.\n' \
#           '탑승 정류장이 포함된 단어를 입력하세요. \n ' \
#           'ex)시민의숲.양재꽃시장 -> 시민의숲, 양재, 꽃시장'
#     print(msg)
#     # reg_order[chat_id] = 2
#     # user_msg[chat_id] = save_input[chat_id]
#
# else:
#     msg = '탑승 정류장을 선택하세요. ex) 2, 2번\n' \
#           '     탑승 정류장  ->  다음 정류장 (운행방향)'
#     for idx, station in enumerate(station_include.get(chat_id)):
#         msg += f'\n{idx + 1}. {station[1]}  ->  {station[2]}'
#     print(msg)




print(round(time.time()))
print(time.time())