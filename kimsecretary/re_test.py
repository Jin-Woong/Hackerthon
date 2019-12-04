import re
import requests
from bs4 import BeautifulSoup as BS

p = re.compile(r'\d+[-]\d+')
# m = p.search('88번')
num = '3007번'
m = re.findall('\d+-?\d+', num)[0]
print(int(m))

# url = 'http://openapi.gbis.go.kr/ws/rest/busrouteservice?serviceKey=p7RiOnONfT8hc4MMVfKU8%2BSr2pQ8vwgM3JQA0sap60em7nJZW5QpGUrGcDmQy4nqe%2B1YxAOAwL7F1uRrlk8PkQ%3D%3D&keyword=3100'
# request = requests.get(url).text
# soup = BS(request, 'html.parser')
# bus_list = soup.find('msgbody')
#
# reg_order = {}
# reg_order['tempid'] = 1
# routeid_list = []
# print('버스를 선택하세요. f'sudo useradd -d /home/ubuntu -u 1000 1, 1번')
# for idx, bus in enumerate(bus_list):
#     print(idx + 1)
#     print('운행지역:' + bus.find('regionname').contents[0])
#     print('버스번호:' + bus.find('routename').contents[0])
#     print('버스종류:' + bus.find('routetypename').contents[0])
#     routeid_list.append(bus.find('routeid').contents[0])

reg_order = {}
user_input = 2
reg_order['tempid'] = 2

# bus = bus_list[1]
# print(routeid_list[2-1])
print('tempid=', reg_order.get('tempid') == 2)
del reg_order['tempid']
print('1', reg_order)
reg_order['test'] = 3
if reg_order.get('test') is not None:
    print('3', reg_order)
    del reg_order['test']
print('2', reg_order)
# print(result)
# input_text='3100번 버스'
# bus_number = re.findall('\d+-?\d+', input_text)[0]
# print('bus=',bus_number)
# url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice?serviceKey=p7RiOnONfT8hc4MMVfKU8%2BSr2pQ8vwgM3JQA0sap60em7nJZW5QpGUrGcDmQy4nqe%2B1YxAOAwL7F1uRrlk8PkQ%3D%3D&keyword={bus_number}'
# url_result = requests.get(url).text
# soup = BS(url_result, 'html.parser')
# bus_list = soup.find('msgbody')
# print(bus_list)

# routeid_list = []
# msg = '버스를 선택하세요. f'sudo useradd -d /home/ubuntu -u 1000 1, 1번'
# requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
# print(msg)
# for idx, bus in enumerate(bus_list):
#     msg = f'{idx + 1}. 지역 : {bus.find("regionname").contents[0]}\n' \
#                     f'   번호:{bus.find("routename").contents[0]}'
#     routeid_list.append(bus.find('routeid').contents[0])
#     print(msg)
#     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')


input_text = '2'
if input_text[-5:] != '등록':
    print('이프문')

# routeid = 200000110
# url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice/station?serviceKey=p7RiOnONfT8hc4MMVfKU8%2BSr2pQ8vwgM3JQA0sap60em7nJZW5QpGUrGcDmQy4nqe%2B1YxAOAwL7F1uRrlk8PkQ%3D%3D&routeId={routeid}'
# url_result = requests.get(url).text
# soup = BS(url_result, 'html.parser')
# station_list = soup.find('msgbody')
#
# station_include = []
# input_text = '양재'
#
# index = 0
#
# station_list = list(station_list)
# #print(station_list)
# print(type(station_list))
# for idx, station in enumerate(station_list):
#     if input_text in station.find('stationname').contents[0]:
#         if idx <= len(station_list):
#             station_include.append([])
#             station_include[index].append(station.find('stationid').contents[0])
#             station_include[index].append(station.find('stationname').contents[0])
#             station_include[index].append(station_list[idx+1].find('stationname').contents[0])
#             station_include[index].append(station.find('stationseq').contents[0])
#         index += 1
#
# print('   ** 탑승 정류장 -> 다음 정류장 **  ')
# for idx, station in enumerate(station_include):
#     print(f'{idx+1}. {station[1]}  ->  {station[2]}')


station_include = []
# print(station_include)
input_text = '듣도보도 못한 이름'
routeid = '200000110'
# if reg_order.get(chat_id) == 3 and save_input != input_text:
url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice/station?serviceKey=p7RiOnONfT8hc4MMVfKU8%2BSr2pQ8vwgM3JQA0sap60em7nJZW5QpGUrGcDmQy4nqe%2B1YxAOAwL7F1uRrlk8PkQ%3D%3D&routeId={routeid}'
url_result = requests.get(url).text
soup = BS(url_result, 'html.parser')
station_list = soup.find('msgbody')

index = 0
station_list = list(station_list)
for idx, station in enumerate(station_list):
    if input_text in station.find('stationname').contents[0]:
        if idx <= len(station_list):
            station_include.append([])
            station_include[index].append(station.find('stationid').contents[0])
            station_include[index].append(station.find('stationname').contents[0])
            station_include[index].append(station_list[idx + 1].find('stationname').contents[0])
            station_include[index].append(station.find('stationseq').contents[0])
        index += 1
a = None
b = 'test'
if not station_include:
    msg = '입력한 단어가 포함된 정류장이 없습니다.'
    print(a == b, a != b)
    print(msg)

else:
    msg = '탑승 정류장을 선택하세요.\n' \
          '     탑승 정류장  ->  다음 정류장 (운행방향)'
    for idx, station in enumerate(station_include):
        msg += f'\n{idx + 1}. {station[1]}  ->  {station[2]}'
    print(msg)

# test = '2'
# print(re.findall('\d+', test)[0])
# print(type(re.findall('\d+', test)[0]))
#
# print(station_include[0])
# bus_stop = int(re.findall('\d+', test)[0]) - 1
# station_id = station_include[bus_stop][0]
# print(station_id)
# msg = '탑승 정류장을 선택하세요.\n' \
#       '     탑승 정류장  ->  다음 정류장 (운행방향)'
# for idx, station in enumerate(station_include):
#     msg += f'\n{idx + 1}. {station[1]}  ->  {station[2]}'


def test(abc):
    print(abc.get('chat_id'))
    print(abc.get('minute'))

tt='없음'
if not re.findall('\d+', tt):
    print('not')
context = {
    'chat_id': '1234',
    'minute': '10'
}
test(context)



