from decouple import config
import requests
import sys
import os
import django
from bs4 import BeautifulSoup as BS

if __name__ == '__main__':
    path = os.path.dirname(__file__)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'telegram.settings'
    django.setup()
    from bus.models import BusGo, BusOut

token = config('TOKEN')
bus_key = config('BUS_KEY')
api_url = f'https://api.telegram.org/bot{token}'

chat_id = sys.argv[1]
minute = sys.argv[2]
direction = sys.argv[3]

station_id = ''
route_id = ''
station_order = ''
region = ''

# minute = sys.argv[2]
# chat_id = context['chat_id']
if direction == 'go':
    busgo = BusGo.objects.filter(chat_id=chat_id).last()
    if busgo is None:
        msg = '출근 버스를 등록하세요.\n' \
              'f'sudo useradd -d /home/ubuntu -u 1000 출근 버스 등록'
        requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
    else:
        station_id = busgo.go_station_id
        route_id = busgo.go_route_id
        station_order = busgo.go_station_order
        region = busgo.go_region

else:  # direction == 'out'
    busout = BusOut.objects.filter(chat_id=chat_id).last()
    if busout is None:
        msg = '퇴근 버스를 등록하세요.\n' \
              'f'sudo useradd -d /home/ubuntu -u 1000 퇴근 버스 등록'
        requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

    else:
        station_id = busout.out_station_id
        route_id = busout.out_route_id
        station_order = busout.out_station_order
        region = busout.out_region

if station_id is not None:
    if region == 'gyeonggi':
        url = f'http://openapi.gbis.go.kr/ws/rest/busarrivalservice?serviceKey={bus_key}&stationId={station_id}&routeId={route_id}&staOrder={station_order}'
        request = requests.get(url).text
        soup = BS(request, 'html.parser')
        # 되기는 하지만 너무 길다..
        # test = soup.select_one('response > msgBody > busArrivalItem > locationNo1').contents[0]
        if not soup.find('predicttime1'):
            msg = '버스API 점검, 운행 종료 등의 사유로\n' \
                  '버스 확인이 불가능합니다'
            requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
        else:
            predict1 = soup.find('predicttime1').contents[0]
            location1 = soup.find('locationno1').contents[0]
            seat1 = soup.find('remainseatcnt1').contents[0]

            predict2 = soup.find('predicttime2').contents[0]
            location2 = soup.find('locationno2').contents[0]
            seat2 = soup.find('remainseatcnt2').contents[0]

            msg += f'직전 버스: {predict1}분 ({location1}정류장) [{seat1}좌석]\n' \
                   f'다음 버스: {predict2}분 ({location2}정류장) [{seat2}좌석]\n' \
                   f'알림 정지: "정지", "종료" 입력'

            if int(minute) == 300:
                requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

            elif int(predict1) <= int(minute):
                requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

    else:  # region == 'seoul'
        url = f'http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?serviceKey={bus_key}&stId={station_id}&busRouteId={route_id}&ord={station_order}'
        request = requests.get(url).text
        soup = BS(request, 'html.parser')

        bus1 = soup.find('arrmsg1').contents[0]
        bus2 = soup.find('arrmsg2').contents[0]
        if bus1.find('분') != -1:
            bus1_minute = bus1[:bus1.find('분')]
            bus1_location = bus1[bus1.find('[') + 1:bus1.find('번')]
            msg = f'직전 버스: {bus1_minute}분 ({bus1_location}정류장)\n'
        else:  # 곧 도착, 운행 종료 등
            bus1_minute = 0
            msg = f'직전 버스: {bus1}\n'

        if bus1.find('분') != -1:
            bus2_minute = bus2[:bus2.find('분')]
            bus2_location = bus2[bus2.find('[') + 1:bus2.find('번')]
            msg += f'다음 버스: {bus2_minute}분 ({bus2_location}정류장)'
        else:
            msg += f'다음 버스: {bus2}'

        if int(minute) == 300:
            requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

        elif int(bus1_minute) <= int(minute):
            requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
else:
    msg = 'DB 읽는 도중 에러가 발생했습니다.\n' \
          '버스를 다시 등록해주세요.'
    requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
    # else:
    #     msg = f'test predict={predict1}, minute={minute}'
    #     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

# if __name__ == '__main__':
#     path = os.path.dirname(__file__)
#     from .models import BusGo, BusOut
