import sys
sys.path.insert(0, "/C:/Users/woong/PycharmProjects/Telegram_alarm/telegram-django/bus/models.py")
from __init__.models import BusGo
# from .bus.models import BusOut

chat_id= '884070245'
bus_number = {}  # 사용자의 입력에서 추출된 버스 번호
station_include = {}  # 입력한 단어가 포함된 정류장 목록, 0:정류장id, 1:정류장이름, 2:다음정류장이름, 3:버스의 정류장순서
routeid = {}  # 선택한 버스의 고유 id
region = {}  # 지역 (서울 or 경기)

bus_number[chat_id] = '누리2'
bus_stop=0
station_include[chat_id].append([])
station_include[chat_id][0] = '204000265'
station_include[chat_id][3] = '48'

busgo = BusGo()

busgo.chat_id = chat_id
busgo.go_bus_number = bus_number.get(chat_id)
busgo.go_station_id = station_include.get(chat_id)[bus_stop][0] #
busgo.go_route_id = routeid.get(chat_id)
busgo.go_station_order = station_include.get(chat_id)[bus_stop][3]
busgo.go_region = region.get(chat_id)
busgo.save()

import sys
print(sys.path)