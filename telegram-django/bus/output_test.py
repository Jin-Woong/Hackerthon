import re

print("start")
msg = '서울 33'
output = re.findall(r'\d+-?\d+', msg)  # 메세지에서 숫자 또는 정수-정수 추출
# output = re.findall(r'\d+', msg)  # 정수 추출
print('test')
if output==[]:
    print('blank')
else:
    print('not blank')
print(output)

# if not bus_number[chat_id]:
#     bus_number[chat_id] = re.findall('\d+', user_msg.get(chat_id))  # 정수 추출