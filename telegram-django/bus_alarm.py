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
station_order= ''

# minute = sys.argv[2]
# chat_id = context['chat_id']
if direction == 'go':
    busgo = BusGo.objects.filter(chat_id=chat_id).last()
    if busgo is None:
        msg = '출근 버스를 등록하세요.\n' \
              'ex) 출근 버스 등록'
        requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
    else:
        station_id = busgo.go_station_id
        route_id = busgo.go_route_id
        station_order = busgo.go_station_order

else:  # direction == 'out'
    busout = BusOut.objects.filter(chat_id=chat_id).last()
    if busout is None:
        msg = '퇴근 버스를 등록하세요.\n' \
              'ex) 퇴근 버스 등록'
        requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

    else:
        station_id = busout.out_station_id
        route_id = busout.out_route_id
        station_order = busout.out_station_order

if station_id is not None:
    # url = 'http://openapi.gbis.go.kr/ws/rest/busarrivalservice?serviceKey=p7RiOnONfT8hc4MMVfKU8%2BSr2pQ8vwgM3JQA0sap60em7nJZW5QpGUrGcDmQy4nqe%2B1YxAOAwL7F1uRrlk8PkQ%3D%3D&stationId=121000921&routeId=200000110&staOrder=39'
    url = f'http://openapi.gbis.go.kr/ws/rest/busarrivalservice?serviceKey={bus_key}&stationId={station_id}&routeId={route_id}&staOrder={station_order}'
    request = requests.get(url).text
    soup = BS(request, 'html.parser')
    # 되기는 하지만 너무 길다..
    # test = soup.select_one('response > msgBody > busArrivalItem > locationNo1').contents[0]
    predict1 = soup.find('predicttime1').contents[0]
    location1 = soup.find('locationno1').contents[0]
    seat1 = soup.find('remainseatcnt1').contents[0]

    predict2 = soup.find('predicttime2').contents[0]
    location2 = soup.find('locationno2').contents[0]
    seat2 = soup.find('remainseatcnt2').contents[0]

    if int(predict1) <= int(minute):
        msg = f'직전 버스 {predict1}분 ({location1}정류장) [{seat1}좌석]\n' \
            f'다음 버스 {predict2}분 ({location2}정류장) [{seat2}좌석]\n' \
            f'(알림 정지방법) "정지" "종료" 등을 입력'
        requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

    # else:
    #     msg = f'test predict={predict1}, minute={minute}'
    #     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

# if __name__ == '__main__':
#     path = os.path.dirname(__file__)
#     from .models import BusGo, BusOut