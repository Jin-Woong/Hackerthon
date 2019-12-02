import re
import requests
from bs4 import BeautifulSoup as BS
from decouple import config

print("start")
msg = '경기 3'
# output = re.findall(r'\d+-?\d+', msg)  # 메세지에서 숫자 또는 정수-정수 추출
output = re.findall(r'\S+', msg[2:])  # 메세지에서 숫자 또는 정수-정수 추출
print(output)
print(msg[2:])
# if output[0][-1]=='번':
#     output[0] = output[0][:-1]


# output = re.findall(r'\d+', msg)  # 정수 추출
print('test')
if output == []:
    print('blank')
else:
    print('not blank')
print(output)

## 버스리스트 출력
print("but list")
bus_list = {};
routeid_list = {};
bus_numbers = {};
bus_number={};
chat_id = '123123'
bus_key = config("BUS_KEY")
bus_number[chat_id] = '누리1'

url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice?serviceKey={bus_key}&keyword={bus_number.get(chat_id)}'
url_result = requests.get(url).text
soup = BS(url_result, 'html.parser')
bus_list[chat_id] = soup.find('msgbody')

if not bus_list.get(chat_id) or str(bus_list.get(chat_id)) == '<msgbody></msgbody>':
    msg = '해당하는 버스가 없습니다.\n' \
          '지역(서울, 경기)과 버스 번호를 입력하세요 \n' \
          'ex) 경기 88-1, 서울 420'
    # send_msg(chat_id, msg)
    print(msg)

else:
    msg = '버스를 선택하세요. ex) 1, 1번'
    # requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
    routeid_list[chat_id] = []
    bus_numbers[chat_id] = []
    if len(bus_number.get(chat_id)) < 0:  # 버스 번호가 한자리인 경우 완전히 일치하는 버스만 출력
        idx = 0
        for idx, bus in enumerate(bus_list.get(chat_id)):
            # 강남3
            if bus.find("routename").contents[0] == bus_number.get(chat_id):
                msg += f'\n{idx}. 버스 : {bus.find("routename").contents[0]} / 지역: {bus.find("regionname").contents[0]}'
                routeid_list[chat_id].append(bus.find('routeid').contents[0])
                bus_numbers[chat_id].append(bus.find("routename").contents[0])
                idx += 1
    else:  # 버스 번호가 두자리 이상인 경우 해당 번호가 포함되는 모든 버스 출력
        for idx, bus in enumerate(bus_list.get(chat_id)):
            msg += f'\n{idx + 1}. 버스 : {bus.find("routename").contents[0]} / 지역: {bus.find("regionname").contents[0]}'
            routeid_list[chat_id].append(bus.find('routeid').contents[0])
            bus_numbers[chat_id].append(bus.find("routename").contents[0])

print(msg)

# if not bus_number[chat_id]:
#     bus_number[chat_id] = re.findall('\d+', user_msg.get(chat_id))  # 정수 추출
