import os
import re
import json
import time

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# from django.shortcuts import render

import requests
from decouple import config
from bs4 import BeautifulSoup as BS

from .send_message import send_msg
from .models import BusGo, BusOut

token = config('TOKEN')
bus_key = config('BUS_KEY')
api_url = f'https://api.telegram.org/bot{token}'

reg_order = {}
routeid_list = {}
save_input = {}
bus_len = {}
routeid = {}
station_include = {}
user_msg = {}
station_list = {}
bus_list = {}
bus_number = {}
go_or_out = {}


@require_POST
@csrf_exempt
def tel(request):
    print('views tel')
    print('request=', request.body)
    global reg_order
    global routeid_list
    global save_input
    global bus_len
    global routeid
    global station_include
    global user_msg
    global bus_list
    global station_list
    global bus_number
    global go_or_out

    message = json.loads(request.body).get('message')

    # user_msg[chat_id] = message.get('text')
    # if message is not None:
    if message is not None:
        chat_id = message.get('from').get('id')
        user_msg[chat_id] = message.get('text')
        p = re.compile('[종료|정지|중지|그만|멈춰].+')  # 종료, 정지 등의 단어가 포함되는지 확인
        print('0 order=', reg_order.get(chat_id), 'save=', save_input.get(chat_id))

        if (round(time.time())-message.get('date')) > 10:
            print('time=', (round(time.time())-message.get('date')))
            return JsonResponse({})

        elif not user_msg.get(chat_id):
            return JsonResponse({})

        elif p.match(user_msg.get(chat_id)):
            cron = f'sudo crontab -u {chat_id} -r'  # 해당 계정의 크론탭을 삭제 후
            user = f'sudo userdel -f {chat_id}'  # 계정을 삭제, 계정 먼저 삭제 시 크론탭 삭제 불가능
            os.system(cron)
            os.system(user)
            send_msg(chat_id, '버스 알림을 종료합니다.')
            # msg = '버스 알림을 종료합니다.'
            # requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

        elif user_msg.get(chat_id)[-2:] == '등록':
            if reg_order.get(chat_id) is not None:
                del reg_order[chat_id]
            if user_msg.get(chat_id)[:2] == '출근':  # 등록을 입력 후 처음 메세지
                send_msg(chat_id, '버스 번호를 입력하세요 ex) 88-1, 88-1번')

                reg_order[chat_id] = 1  # 등록 1단계 버스 번호 입력 받기
                save_input[chat_id] = user_msg.get(chat_id)
                go_or_out[chat_id] = 'go'
                print('1 order=', reg_order.get(chat_id), 'save=', save_input.get(chat_id))
            elif user_msg.get(chat_id)[:2] == '퇴근':
                send_msg(chat_id, '버스 번호를 입력하세요 ex) 88-1, 88-1번')

                reg_order[chat_id] = 1  # 등록 1단계 버스 번호 입력 받기
                save_input[chat_id] = user_msg.get(chat_id)
                go_or_out[chat_id] = 'out'
                print('1 order=', reg_order.get(chat_id), 'save=', save_input.get(chat_id))

            # elif input_text[:2] == '퇴근':
            #     msg = '버스 번호를 입력하세요 ex) 88-1'
            #     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
            #     reg_order[chat_id] = 1  # 등록 1단계 버스 번호 입력 받기
        elif reg_order.get(chat_id) == 1 and save_input.get(chat_id) != user_msg.get(chat_id):  # 버스 번호 입력 받은 후 버스 선택
            # bus_number = re.findall('\d+-?\d+', input_text)[0]
            bus_number[chat_id] = re.findall('\d+-?\d+', user_msg.get(chat_id))  # 메세지에서 숫자 또는 숫자-숫자만 추출
            if not bus_number.get(chat_id):
                bus_number[chat_id] = re.findall('\d+', user_msg.get(chat_id))
            if not bus_number.get(chat_id):
                msg = '숫자를 포함해서 입력해주세요.\n' \
                      '버스 번호를 입력하세요 ex) 88-1, 88-1번'
                send_msg(chat_id, msg)

            else:
                bus_number[chat_id] = bus_number[chat_id][0]
                print('입력받은 버스넘버:', bus_number)
                url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice?serviceKey={bus_key}&keyword={bus_number.get(chat_id)}'
                url_result = requests.get(url).text
                soup = BS(url_result, 'html.parser')
                bus_list[chat_id] = soup.find('msgbody')

                if not bus_list.get(chat_id):
                    msg = '해당하는 버스가 없습니다.\n' \
                          '경기도를 경유하는 버스만 가능합니다.\n' \
                          '버스 번호를 입력하세요 ex) 88-1, 88-1번'
                    send_msg(chat_id, msg)
                    
                else:
                    msg = '버스를 선택하세요. ex) 1, 1번'
                    # requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
                    routeid_list[chat_id] = []
                    if len(bus_number.get(chat_id)) < 2:
                        idx = 0
                        for bus in bus_list.get(chat_id):
                            if bus.find("routename").contents[0] == bus_number.get(chat_id):
                                msg += f'\n{idx + 1}. 지역: {bus.find("regionname").contents[0]} / 번호: {bus.find("routename").contents[0]}'
                                routeid_list[chat_id].append(bus.find('routeid').contents[0])
                                idx += 1

                    else:
                        for idx, bus in enumerate(bus_list.get(chat_id)):
                            msg += f'\n{idx + 1}. 지역: {bus.find("regionname").contents[0]} / 번호: {bus.find("routename").contents[0]}'
                            routeid_list[chat_id].append(bus.find('routeid').contents[0])
                    send_msg(chat_id, msg)
                    bus_len[chat_id] = len(bus_list.get(chat_id))  # 불필요한듯..
                    reg_order[chat_id] = 2
                    save_input[chat_id] = user_msg.get(chat_id)
                    print('2 order=', reg_order.get(chat_id), 'save=', save_input.get(chat_id), 'user_msg=',
                          user_msg.get(chat_id))

        elif reg_order.get(chat_id) == 2 and save_input.get(chat_id) != user_msg.get(chat_id):  # 버스 선택 후 탑승지 입력 받기
            # idx = int(re.findall('\d+', input_text)[0])
            idx = int(re.findall('\d+', user_msg.get(chat_id))[0])-1
            if idx < len(routeid_list.get(chat_id)):
                routeid[chat_id] = routeid_list.get(chat_id)[idx]
                msg = '탑승 정류장이 포함된 단어를 입력하세요. \n ' \
                      'ex)시민의숲.양재꽃시장 -> 시민의숲, 양재, 꽃시장'
                send_msg(chat_id, msg)

                reg_order[chat_id] = 3
                save_input[chat_id] = user_msg.get(chat_id)
                print('3 order=', reg_order.get(chat_id), 'save=', save_input, 'user_msg=', user_msg.get(chat_id))
            else:
                msg = f'1~{len(routeid_list[chat_id])}의 번호를 입력하세요'
                send_msg(chat_id, msg)

        elif reg_order.get(chat_id) == 3 and save_input.get(chat_id) != user_msg.get(chat_id):  # 입력받은 탑승지로 정류장 검색
            url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice/station?serviceKey={bus_key}&routeId={routeid.get(chat_id)}'
            url_result = requests.get(url).text
            soup = BS(url_result, 'html.parser')

            stations = soup.find('msgbody') ##
            station_list[chat_id] = list(stations)

            index = 0
            # station_list = list(station_list)
            station_include[chat_id] = []
            for idx, station in enumerate(station_list.get(chat_id)):  # 정류장리스트에서 입력받은 단어가 포함된 정류장 찾기 ##
                if user_msg.get(chat_id) in station.find('stationname').contents[0]:
                    if idx < len(station_list.get(chat_id)) - 1:
                        station_include[chat_id].append([])
                        station_include[chat_id][index].append(station.find('stationid').contents[0])
                        station_include[chat_id][index].append(station.find('stationname').contents[0])
                        station_include[chat_id][index].append(station_list.get(chat_id)[idx + 1].find('stationname').contents[0])
                        station_include[chat_id][index].append(station.find('stationseq').contents[0])
                    index += 1
            print(station_include[chat_id])

            if not station_include.get(chat_id):  # 일치하는 정류장이 하나도 없는 경우
                msg = '입력한 단어가 포함된 정류장이 없습니다.\n' \
                      '탑승 정류장이 포함된 단어를 입력하세요. \n ' \
                      'ex)시민의숲.양재꽃시장 -> 시민의숲, 양재, 꽃시장'
                send_msg(chat_id, msg)
                # reg_order[chat_id] = 2
                # user_msg[chat_id] = save_input[chat_id]
                save_input[chat_id] = None

            else:
                msg = '탑승 정류장을 선택하세요. ex) 2, 2번\n' \
                      '     탑승 정류장  ->  다음 정류장 (운행방향)'
                for idx, station in enumerate(station_include.get(chat_id)):
                    # if idx < len(station_include.get(chat_id)):
                    msg += f'\n{idx + 1}. {station[1]}  ->  {station[2]}'
                send_msg(chat_id, msg)
                reg_order[chat_id] = 4
                save_input[chat_id] = user_msg.get(chat_id)
            print('4 order=', reg_order.get(chat_id), 'save=', save_input.get(chat_id), 'user_msg=',
                  user_msg.get(chat_id))

        elif reg_order.get(chat_id) == 4 and save_input.get(chat_id) != user_msg.get(chat_id):
            # bus_stop = int(re.findall('\d+', input_text)[0])-1  # 1부터 출력했으므로 -1
            bus_stop = int(re.findall('\d+', user_msg.get(chat_id))[0]) - 1  # 1부터 출력했으므로 -1
            if bus_stop < len(station_include.get(chat_id)):
                # go_station_id = station_include[bus_stop][0]
                # go_route_id = routeid
                # go_station_order = station_include[bus_stop][3]
                # print(go_station_id, go_route_id, go_station_order)
                if go_or_out.get(chat_id) == 'go':
                    busgo = BusGo()
                    busgo.chat_id = chat_id
                    busgo.go_bus_number = bus_number.get(chat_id)
                    busgo.go_station_id = station_include.get(chat_id)[bus_stop][0]
                    busgo.go_route_id = routeid.get(chat_id)
                    busgo.go_station_order = station_include.get(chat_id)[bus_stop][3]
                    busgo.save()
                # DB insert문 추가하기
                elif go_or_out.get(chat_id) == 'out':
                    busout = BusOut()
                    busout.chat_id = chat_id
                    busout.out_bus_number = bus_number.get(chat_id)
                    busout.out_station_id = station_include.get(chat_id)[bus_stop][0]
                    busout.out_route_id = routeid.get(chat_id)
                    busout.out_station_order = station_include.get(chat_id)[bus_stop][3]
                    busout.save()
                msg = '등록이 완료 되었습니다.\n' \
                      '--------------------------------\n'\
                        '알림 예시 : 출근 버스 10분전 알림\n' \
                '               퇴근버스 10분전에 알려줘\n' \
                '  위의 예시와 유사하게 입력하세요  '
                send_msg(chat_id, msg)

                if reg_order.get(chat_id):
                    del reg_order[chat_id]
                    print('del 1')
                if routeid_list.get(chat_id):
                    del routeid_list[chat_id]
                    print('del 2')
                if save_input.get(chat_id):
                    del save_input[chat_id]
                    print('del 3')
                if bus_len.get(chat_id):
                    del bus_len[chat_id]
                    print('del 4')
                if routeid.get(chat_id):
                    del routeid[chat_id]
                    print('del 5')
                if station_include.get(chat_id):
                    del station_include[chat_id]
                    print('del 6')
                if user_msg.get(chat_id):
                    del user_msg[chat_id]
                    print('del 7')
                if station_list.get(chat_id):
                    del station_list[chat_id]
                    print('del 8')
                if bus_list.get(chat_id):
                    del bus_list[chat_id]
                    print('del 9')
                if bus_number.get(chat_id):
                    del bus_number[chat_id]
                    print('del 10')

            else:
                msg = f'1~{len(station_include.get(chat_id))}의 번호를 입력하세요'
                send_msg(chat_id, msg)
                # save_input[chat_id] = None

        elif user_msg.get(chat_id)[:2] == '출근':
            if user_msg.get(chat_id)[-2:] != '등록':
                minute = re.findall('\d+', user_msg.get(chat_id))
                if not minute:
                    pass
                else:
                    busgo = BusGo.objects.filter(chat_id=chat_id).last()
                    if not busgo:
                        msg = '출근 버스를 등록하세요.\n' \
                            'ex) 출근 버스 등록'
                        send_msg(chat_id, msg)
                    else:
                        user = f'sudo useradd -d /home/ec2-user -u 500 -o {chat_id}'  # ec2-user 와 같은 uid 를 갖도록 계정 생성
                        # 크론탭 시간 1분은 좀 긴거 같고 30초 간격으로 수정해야할듯..
                        cron = f'(crontab -l 2>/dev/null; echo "*/1 * * * * python3 /home/ec2-user/telegram-django/bus_alarm.py {chat_id} {minute[0]} go") | sudo crontab -u {chat_id} -'
                        os.system(user)
                        os.system(cron)
                        msg = f'출근버스 ({busgo.go_bus_number}) 도착 {minute[0]}분 전 알림\n'\
                            f'종료, 정지 등을 입력하면 종료합니다.'
                        send_msg(chat_id,msg)
                    print('end')
                    
        elif user_msg.get(chat_id)[:2] == '퇴근':
            if user_msg.get(chat_id)[-2:] != '등록':
                minute = re.findall('\d+', user_msg.get(chat_id))
                if not minute:
                    pass
                else:
                    busout = BusOut.objects.filter(chat_id=chat_id).last()
                    if not busout:
                        msg = '퇴근 버스를 등록하세요.\n' \
                            'ex) 퇴근 버스 등록'
                        send_msg(chat_id, msg)
                    else:
                        user = f'sudo useradd -d /home/ec2-user -u 500 -o {chat_id}'  # ec2-user 와 같은 uid 를 갖도록 계정 생성
                        # 크론탭 시간 1분은 좀 긴거 같고 30초 간격으로 수정해야할듯..
                        cron = f'(crontab -l 2>/dev/null; echo "*/1 * * * * python3 /home/ec2-user/telegram-django/bus_alarm.py {chat_id} {minute[0]} out") | sudo crontab -u {chat_id} -'
                        print(cron)
                        os.system(user)
                        os.system(cron)
                        msg = f'{busout.out_bus_number}번 버스 도착 {minute[0]}분 전 알림\n'\
                            f'종료, 정지 등을 입력하면 종료합니다.'
                        send_msg(chat_id, msg)
                        print('end')
        elif user_msg.get(chat_id) in ['/start', '안녕', '메뉴', '김비서', '하이']:
            msg = '''안녕하세요. 김비서입니다 :D
원하는 알림을 아래와 같이 설정해보세요.
예) 교통정보알림 설정 방법
- (등록 방법) “출근/퇴근 버스 등록” 입력 
- (등록 후) “출근/퇴근 xx분 전 알림” 입력
- (알림정지방법) "정지" 또는 "종료" 입력'''
            send_msg(chat_id, msg)
        else:
            msg = '등록 예시 : 출근 버스 등록\n' \
                '               퇴근 버스 등록\n' \
                '알림 예시 : 출근 버스 10분전 알림\n' \
                '               퇴근버스 10분전에 알려줘\n' \
                '위의 예시와 유사하게 입력하세요'
            send_msg(chat_id, msg)
    return JsonResponse({})
