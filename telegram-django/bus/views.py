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

# 사용자마다 각각 id로 채팅내용을 구별하기 위해 자료형을 딕셔너리로 설정
reg_order = {}
routeid_list = {}
save_input = {}
bus_len = {}
routeid = {}
station_include = {}
user_msg = {}
station_list = {}
bus_list = {}
bus_numbers = {}
bus_number = {}
go_or_out = {}
region = {}


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
    global region
    global bus_numbers

    message = json.loads(request.body).get('message')

    # user_msg[chat_id] = message.get('text')
    # if message is not None:
    if message is not None:
        chat_id = message.get('from').get('id') # 사용자 id
        user_msg[chat_id] = message.get('text') # 사용자 id : 채팅내용 형태로 딕셔너리 저장
        # p = re.compile('[종료|정지|중지|그만|멈춰]')  # 종료, 정지 등의 단어가 포함되는지 확인
        print('0 order=', reg_order.get(chat_id), 'save=', save_input.get(chat_id))

        # 10초가 지난 메세지들은 무시, webhook에 딜레이가 생길 경우 대화 단계가 꼬일 수 있다.
        if (round(time.time())-message.get('date')) > 10:
            print('ignore msg,time=', message.get('text'),(round(time.time())-message.get('date')))
            return JsonResponse({})

        # 채팅내용이 없는 경우
        elif not user_msg.get(chat_id):
            return JsonResponse({})

        # 채팅 내용에 정지 관련 단어가 있는 경우
        elif len(user_msg.get(chat_id)) > 1 and user_msg.get(chat_id) in ['그만', '종료', '정지', '멈춰', '중지']:
            cron = f'sudo crontab -u {chat_id} -r'  # 해당 계정의 크론탭을 삭제 후
            user = f'sudo userdel -f {chat_id}'  # 계정을 삭제, 계정 먼저 삭제 시 크론탭 삭제 불가능
            os.system(cron)
            os.system(user)
            send_msg(chat_id, '버스 알림을 종료합니다.')
            # msg = '버스 알림을 종료합니다.'
            # requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')

        # 채팅 내용 뒤의 두 글자가 등록인 경우
        elif user_msg.get(chat_id)[-2:] == '등록':
            if reg_order.get(chat_id) is not None:  # 기존의 대화단계가 존재할 경우 삭제
                del reg_order[chat_id]
            if user_msg.get(chat_id)[:2] == '출근':  # 등록을 입력 후 처음 메세지
                msg = '지역(서울, 경기)과 버스 번호를 입력하세요 \n' \
                      f'sudo useradd -d /home/ubuntu -u 1000 경기 88-1, 서울 420'
                send_msg(chat_id, msg)

                reg_order[chat_id] = 1  # 등록 1단계 버스 번호 입력 받기
                save_input[chat_id] = user_msg.get(chat_id)
                go_or_out[chat_id] = 'go'
                print('1 order=', reg_order.get(chat_id), 'save=', save_input.get(chat_id))

            elif user_msg.get(chat_id)[:2] == '퇴근':
                msg = '지역(서울, 경기)과 버스 번호를 입력하세요 \n' \
                      f'sudo useradd -d /home/ubuntu -u 1000 경기 88-1, 서울 420'
                send_msg(chat_id, msg)

                reg_order[chat_id] = 1  # 등록 1단계 버스 번호 입력 받기
                save_input[chat_id] = user_msg.get(chat_id)
                go_or_out[chat_id] = 'out'
                print('1 order=', reg_order.get(chat_id), 'save=', save_input.get(chat_id))

                # elif input_text[:2] == '퇴근':
                #     msg = '버스 번호를 입력하세요 f'sudo useradd -d /home/ubuntu -u 1000 88-1'
                #     requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
                #     reg_order[chat_id] = 1  # 등록 1단계 버스 번호 입력 받기
            
        elif reg_order.get(chat_id) == 1 and save_input.get(chat_id) != user_msg.get(chat_id):  # 버스 번호 입력 받은 후 버스 리스트 출력
            # bus_number = re.findall('\d+-?\d+', input_text)[0]
            
            # 정규식 활용 버스 번호 추출  xxx-x, xxx 형태
            # bus_number[chat_id] = re.findall(r'\d+-?\d+', user_msg.get(chat_id))  # 메세지에서 숫자 또는 정수-정수 추출
            # if not bus_number[chat_id]:
            #     bus_number[chat_id] = re.findall('\d+', user_msg.get(chat_id))  # 한 자리 정수 추출, 위의 d+형태는 두 자리 이상 정수만 추출되어 보완
            # 기존 정수 추출 정규식에서 모든 문자 추출로 변경, 예시) 강남, 강남1-1과 같은버스가 존재하므로
            bus_number[chat_id] = re.findall(r'\S+',user_msg.get(chat_id)[2:])

            # 메세지가 2글자 이하인 경우 지역 또는 버스번호 입력 안한 것으로 판단
            if len(user_msg.get(chat_id)) < 2:
                msg = '지역(서울, 경기)과 버스 번호를 입력하세요 \n' \
                      '예시) 경기 88-1, 서울 420'
                send_msg(chat_id, msg)
                return JsonResponse({})

            # 메세지에 서울, 경기가 아닌 다른 단어를 입력한 경우
            elif user_msg.get(chat_id)[:2] != '경기' and user_msg.get(chat_id)[:2] != '서울':
                msg = '서울, 경기 지역을 선택해주세요.\n' \
                      '지역(서울, 경기)과 버스 번호를 입력하세요 \n' \
                      '예시) 경기 88-1, 서울 420'
                send_msg(chat_id, msg)
                return JsonResponse({})

            # 메세지에 버스 번호가 없는 경우
            elif not bus_number.get(chat_id):
                msg = '버스 번호와 함께 입력해주세요.\n' \
                      '지역(서울, 경기)과 버스 번호를 입력하세요 \n' \
                      '예시) 경기 88-1, 서울 420'
                send_msg(chat_id, msg)
                return JsonResponse({})

            else:
                if user_msg.get(chat_id)[:2] == '경기':
                    region[chat_id] = 'gyeonggi'
                else:
                    region[chat_id] = 'seoul'
                bus_number[chat_id] = bus_number[chat_id][0]    # 버스번호추출 하는 과정에서 할 경우 버스번호가 없을 때 인덱스에러가 발생할 수 있다.
                print('지역=',region.get(chat_id),'버스넘버:', bus_number.get(chat_id))
                if region.get(chat_id) == 'gyeonggi':
                    url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice?serviceKey={bus_key}&keyword={bus_number.get(chat_id)}'
                else: # region.get(chat_id) == 'seoul'
                    url = f'http://ws.bus.go.kr/api/rest/busRouteInfo/getBusRouteList?serviceKey={bus_key}&strSrch={bus_number.get(chat_id)}'
                url_result = requests.get(url).text
                soup = BS(url_result, 'html.parser')
                bus_list[chat_id] = soup.find('msgbody')

                if not bus_list.get(chat_id) or str(bus_list.get(chat_id)) == '<msgbody></msgbody>':
                    msg = '해당하는 버스가 없습니다.\n' \
                          '지역(서울, 경기)과 버스 번호를 입력하세요 \n' \
                          '예시) 경기 88-1, 서울 420'
                    send_msg(chat_id, msg)
                    
                else:
                    msg = '버스를 선택하세요. 예시) 1, 1번'
                    # requests.get(api_url + f'/sendMessage?chat_id={chat_id}&text={msg}')
                    routeid_list[chat_id] = []
                    bus_numbers[chat_id] = []
                    if region.get(chat_id) == 'gyeonggi':
                        if len(bus_number.get(chat_id)) < 2:    # 버스 번호가 한자리인 경우 완전히 일치하는 버스만 출력, 한자리가 포함된 버스가 수백건이라서..
                            idx = 0 # 조건에 맞는 버스 출력이므로 enumerate 사용 시 index가 순차적으로 출력되지 않는다.
                            for bus in bus_list.get(chat_id):
                                if bus.find("routename").contents[0] == bus_number.get(chat_id):
                                    msg += f'\n{idx + 1}. 버스 : {bus.find("routename").contents[0]} / 지역: {bus.find("regionname").contents[0]}'
                                    routeid_list[chat_id].append(bus.find('routeid').contents[0])
                                    bus_numbers[chat_id].append(bus.find("routename").contents[0])
                                    idx += 1
                        else: # 버스 번호가 두자리 이상인 경우 해당 번호가 포함되는 모든 버스 출력
                            for idx, bus in enumerate(bus_list.get(chat_id)):
                                msg += f'\n{idx + 1}. 버스 : {bus.find("routename").contents[0]} / 지역: {bus.find("regionname").contents[0]}'
                                routeid_list[chat_id].append(bus.find('routeid').contents[0])
                                bus_numbers[chat_id].append(bus.find("routename").contents[0])

                    else:  # region.get(chat_id) == 'seoul'
                        if len(bus_number.get(chat_id)) < 2:
                            idx = 0
                            for bus in bus_list.get(chat_id):
                                if bus.find("busroutenm").contents[0] == bus_number.get(chat_id) or \
                                        bus.find("busroutenm").contents[0] == '0' + bus_number.get(chat_id):
                                    msg += f'\n{idx + 1}. 버스 : {bus.find("busroutenm").contents[0]} / {bus.find("ststationnm").contents[0]}<->{bus.find("edstationnm").contents[0]}'
                                    routeid_list[chat_id].append(bus.find('busrouteid').contents[0])
                                    bus_numbers[chat_id].append(bus.find("busroutenm").contents[0])
                                    idx += 1

                        else:
                            for idx, bus in enumerate(bus_list.get(chat_id)):
                                msg += f'\n{idx + 1}. 버스 : {bus.find("busroutenm").contents[0]} / {bus.find("ststationnm").contents[0]}<->{bus.find("edstationnm").contents[0]}'
                                routeid_list[chat_id].append(bus.find('busrouteid').contents[0])
                                bus_numbers[chat_id].append(bus.find("busroutenm").contents[0])
                    send_msg(chat_id, msg)

                    # bus_len[chat_id] = len(bus_list.get(chat_id))  # 불필요한듯..
                    reg_order[chat_id] = 2
                    save_input[chat_id] = user_msg.get(chat_id)
                    print('2 order=', reg_order.get(chat_id), 'save=', save_input.get(chat_id), 'user_msg=',
                          user_msg.get(chat_id))

        elif reg_order.get(chat_id) == 2 and save_input.get(chat_id) != user_msg.get(chat_id):  # 버스 선택 후 탑승지 입력 받기
            # idx = int(re.findall('\d+', input_text)[0])
            if re.findall('\d+', user_msg.get(chat_id)):
                idx = int(re.findall('\d+', user_msg.get(chat_id))[0]) - 1
                if idx < len(routeid_list.get(chat_id)):
                    routeid[chat_id] = routeid_list.get(chat_id)[idx]
                    bus_number[chat_id] = bus_numbers.get(chat_id)[idx]
                    msg = '탑승할 정류장에 포함된 단어를 입력하세요. \n ' \
                          '  예시) 관악우체국 -> 관악, 우체국'
                    send_msg(chat_id, msg)

                    reg_order[chat_id] = 3
                    save_input[chat_id] = user_msg.get(chat_id)
                    print('3 order=', reg_order.get(chat_id), 'save=', save_input, 'user_msg=', user_msg.get(chat_id))
                else:
                    msg = f'1~{len(routeid_list[chat_id])} 사이의 번호를 입력하세요'
                    send_msg(chat_id, msg)

            else:
                msg = f'1~{len(routeid_list[chat_id])} 사이의 번호를 입력하세요'
                send_msg(chat_id, msg)

        elif reg_order.get(chat_id) == 3 and save_input.get(chat_id) != user_msg.get(chat_id):  # 입력받은 탑승지로 정류장 검색
            if region.get(chat_id) == 'gyeonggi':
                url = f'http://openapi.gbis.go.kr/ws/rest/busrouteservice/station?serviceKey={bus_key}&routeId={routeid.get(chat_id)}'
            else:  # region.get(chat_id)=='seoul':
                url = f'http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute?serviceKey={bus_key}&busRouteId={routeid.get(chat_id)}'
            url_result = requests.get(url).text
            soup = BS(url_result, 'html.parser')

            stations = soup.find('msgbody') ##
            station_list[chat_id] = list(stations)

            index = 0
            station_include[chat_id] = []
            if region.get(chat_id) == 'gyeonggi':
                for idx, station in enumerate(station_list.get(chat_id)):  # 정류장리스트에서 입력받은 단어가 포함된 정류장 찾기 ##
                    if user_msg.get(chat_id) in station.find('stationname').contents[0]:
                        if idx < len(station_list.get(chat_id)) - 1:
                            station_include[chat_id].append([])
                            station_include[chat_id][index].append(station.find('stationid').contents[0])
                            station_include[chat_id][index].append(station.find('stationname').contents[0])
                            station_include[chat_id][index].append(station_list.get(chat_id)[idx + 1].find('stationname').contents[0])
                            station_include[chat_id][index].append(station.find('stationseq').contents[0])
                            index += 1
            else:  # region.get(chat_id) == 'seoul':
                for idx, station in enumerate(station_list.get(chat_id)):  # 정류장리스트에서 입력받은 단어가 포함된 정류장 찾기 ##
                    if user_msg.get(chat_id) in station.find('stationnm').contents[0]:
                        if idx < len(station_list.get(chat_id)) - 1:
                            station_include[chat_id].append([])
                            station_include[chat_id][index].append(station.find('station').contents[0])
                            station_include[chat_id][index].append(station.find('stationnm').contents[0])
                            station_include[chat_id][index].append(
                                station_list.get(chat_id)[idx + 1].find('stationnm').contents[0])
                            station_include[chat_id][index].append(station.find('seq').contents[0])
                            index += 1

            print(station_include[chat_id])

            if not station_include.get(chat_id):  # 일치하는 정류장이 하나도 없는 경우
                msg = '입력한 단어가 포함된 정류장이 없습니다.\n' \
                      '탑승할 정류장에 포함된 단어를 입력하세요. \n ' \
                      '  예시) 관악우체국 -> 관악, 우체국'
                send_msg(chat_id, msg)
                # reg_order[chat_id] = 2
                # user_msg[chat_id] = save_input[chat_id]
                # save_input[chat_id] = None

            else:
                msg = '탑승 정류장을 선택하세요. 예시) 2, 2번\n' \
                      '**탑승 정류장 -> 다음 정류장 (운행방향)**'
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
            if not re.findall('\d+', user_msg.get(chat_id)):
                msg = f'1~{len(station_include.get(chat_id))}의 번호를 입력하세요'
                send_msg(chat_id, msg)
            elif re.findall('\d+', user_msg.get(chat_id)):
                bus_stop = int(re.findall('\d+', user_msg.get(chat_id))[0]) - 1  # 1부터 출력했으므로 -1
                if bus_stop >= len(station_include.get(chat_id)):
                    msg = f'1~{len(station_include.get(chat_id))}의 번호를 입력하세요'
                    send_msg(chat_id, msg)
                # save_input[chat_id] = None
                else:  # if bus_stop < len(station_include.get(chat_id)):

                    if go_or_out.get(chat_id) == 'go':

                        busgo = BusGo()
                        busgo.chat_id = chat_id
                        busgo.go_bus_number = bus_number.get(chat_id)
                        busgo.go_station_id = station_include.get(chat_id)[bus_stop][0]
                        busgo.go_route_id = routeid.get(chat_id)
                        busgo.go_station_order = station_include.get(chat_id)[bus_stop][3]
                        busgo.go_region = region.get(chat_id)
                        busgo.save()
                        msg = '출근버스 '

                    elif go_or_out.get(chat_id) == 'out':
                        busout = BusOut()
                        busout.chat_id = chat_id
                        busout.out_bus_number = bus_number.get(chat_id)
                        busout.out_station_id = station_include.get(chat_id)[bus_stop][0]
                        busout.out_route_id = routeid.get(chat_id)
                        busout.out_station_order = station_include.get(chat_id)[bus_stop][3]
                        busout.out_region = region.get(chat_id)
                        busout.save()
                        msg = '퇴근버스 '

                    msg += '등록이 완료 되었습니다.\n' \
                            '-----------------------------------------------\n'\
                            '알림 예시 : 출근 버스 10분전 알림\n' \
                            '                 퇴근버스 10분전에 알려줘\n' \
                            '                 퇴근버스 3분마다 알려줘\n' \
                            '  **위의 예시와 유사하게 입력하세요**  '
                    send_msg(chat_id, msg)

                    if reg_order.get(chat_id):
                        del reg_order[chat_id]
                    if routeid_list.get(chat_id):
                        del routeid_list[chat_id]
                    if save_input.get(chat_id):
                        del save_input[chat_id]
                    if bus_len.get(chat_id):
                        del bus_len[chat_id]
                    if routeid.get(chat_id):
                        del routeid[chat_id]
                    if station_include.get(chat_id):
                        del station_include[chat_id]
                    if user_msg.get(chat_id):
                        del user_msg[chat_id]
                    if station_list.get(chat_id):
                        del station_list[chat_id]
                    if bus_list.get(chat_id):
                        del bus_list[chat_id]
                    if bus_number.get(chat_id):
                        del bus_number[chat_id]
                    if bus_numbers.get(chat_id):
                        del bus_numbers[chat_id]
                    if region.get(chat_id):
                        del region[chat_id]
                    if go_or_out.get(chat_id):
                        del go_or_out[chat_id]
                    print('delete bus info')

        elif user_msg.get(chat_id)[:2] == '출근' and user_msg.get(chat_id)[-2:] != '등록' and re.findall('\d+', user_msg.get(chat_id)):
                minute = re.findall('\d+', user_msg.get(chat_id))
                if '전' in user_msg.get(chat_id):
                    busgo = BusGo.objects.filter(chat_id=chat_id).last()
                    if not busgo:
                        msg = '먼저 출근 버스를 등록하세요.\n' \
                            '예시) 출근 버스 등록'
                        send_msg(chat_id, msg)
                    else:
                        # 계정 추가 시 pip로 library 설치한 계정과 같은 uid를 가져야한다.
                        # OS마다 다르다.. ubuntu의 ubuntu는 1000, amazon linux의 ec2-user는 500
                        user = f'sudo useradd -d /home/ubuntu -u 1000 -o {chat_id}'  # ubuntu 와 같은 uid 를 갖도록 계정 생성
                        # 크론탭 시간 1분은 좀 긴거 같고 30초 간격으로 수정해야할듯..
                        cron = f'(crontab -l 2>/dev/null; echo "*/1 * * * * python3 /home/ubuntu/telegram_alarm/telegram-django/bus_alarm.py {chat_id} {minute[0]} go") | sudo crontab -u {chat_id} -'
                        os.system(user)
                        os.system(cron)
                        msg = f'{busgo.go_bus_number}번 버스 도착 {minute[0]}분 전 알림\n'\
                            f'종료, 정지 등을 입력하면 종료합니다.'
                        send_msg(chat_id,msg)
                    print('end')
                elif '마다' in user_msg.get(chat_id):
                    busgo = BusGo.objects.filter(chat_id=chat_id).last()
                    if not busgo:
                        msg = '먼저 출근 버스를 등록하세요.\n' \
                              '예시) 출근 버스 등록'
                        send_msg(chat_id, msg)
                    else:
                        user = f'sudo useradd -d /home/ubuntu -u 1000 -o {chat_id}'  # ubuntu 와 같은 uid 를 갖도록 계정 생성
                        # 크론탭 시간 1분은 좀 긴거 같고 30초 간격으로 수정해야할듯..
                        cron = f'(crontab -l 2>/dev/null; echo "*/{minute[0]} * * * * python3 /home/ubuntu/telegram_alarm/telegram-django/bus_alarm.py {chat_id} 300 go") | sudo crontab -u {chat_id} -'
                        os.system(user)
                        os.system(cron)
                        msg = f'{busgo.go_bus_number}번 버스 도착 {minute[0]}분 마다 알림\n' \
                            f'종료, 정지 등을 입력하면 종료합니다.'
                        send_msg(chat_id, msg)
                    print('end')
                    
        elif user_msg.get(chat_id)[:2] == '퇴근' and user_msg.get(chat_id)[-2:] != '등록' and re.findall('\d+', user_msg.get(chat_id)):
            minute = re.findall('\d+', user_msg.get(chat_id))
            if '전' in user_msg.get(chat_id):
                busout = BusOut.objects.filter(chat_id=chat_id).last()
                if not busout:
                    msg = '먼저 퇴근 버스를 등록하세요.\n' \
                        '예시) 퇴근 버스 등록'
                    send_msg(chat_id, msg)
                else:
                    user = f'sudo useradd -d /home/ubuntu -u 1000 -o {chat_id}'  # ubuntu 와 같은 uid 를 갖도록 계정 생성
                    # 크론탭 시간 1분은 좀 긴거 같고 30초 간격으로 수정해야할듯..
                    cron = f'(crontab -l 2>/dev/null; echo "*/1 * * * * python3 /home/ubuntu/telegram_alarm/telegram-django/bus_alarm.py {chat_id} {minute[0]} out") | sudo crontab -u {chat_id} -'
                    print(cron)
                    os.system(user)
                    os.system(cron)
                    msg = f'{busout.out_bus_number}번 버스 도착 {minute[0]}분 전 알림\n'\
                        f'종료, 정지 등을 입력하면 종료합니다.'
                    send_msg(chat_id, msg)
                    print('end')
            elif '마다' in user_msg.get(chat_id):
                busout = BusOut.objects.filter(chat_id=chat_id).last()
                if not busout:
                    msg = '먼저 퇴근 버스를 등록하세요.\n' \
                          '예시) 퇴근 버스 등록'
                    send_msg(chat_id, msg)
                else:
                    user = f'sudo useradd -d /home/ubuntu -u 1000 -o {chat_id}'  # ubuntu 와 같은 uid 를 갖도록 계정 생성
                    cron = f'(crontab -l 2>/dev/null; echo "*/{minute[0]} * * * * python3 /home/ubuntu/telegram_alarm/telegram-django/bus_alarm.py {chat_id} 300 out") | sudo crontab -u {chat_id} -'
                    os.system(user)
                    os.system(cron)
                    msg = f'{busout.out_bus_number}번 버스 도착 {minute[0]}분 마다 알림\n' \
                        f'종료, 정지 등을 입력하면 종료합니다.'
                    send_msg(chat_id, msg)
                print('end')

        elif user_msg.get(chat_id) in ['/start', '안녕', '메뉴', '김비서', '하이']:
            msg = '''버스도착알림 서비스입니다 :D
원하는 알림을 아래와 같이 설정해보세요.
- (등록 방법) “출근/퇴근 버스 등록” 입력 
- (등록 후) “출근/퇴근 xx분 전/마다 알림” 입력
- (알림정지방법) "정지" 또는 "종료" 입력'''
            send_msg(chat_id, msg)
        else:
            msg = '등록 예시 : "출근 버스 등록"\n' \
                '                "퇴근 버스 등록"\n' \
                '알림 예시 : "출근 버스 10분전 알림"\n' \
                '                "출근버스 3분마다 알려줘"\n' \
                '                "퇴근버스 10분전에 알려줘"\n' \
                '정지 예시 : "정지" "종료" 등 입력\n' \
                '   **위의 예시와 유사하게 입력하세요** '
            send_msg(chat_id, msg)
    return JsonResponse({})
