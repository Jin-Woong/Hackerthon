import os
import json
import requests
from decouple import config

# def get_ngrok_url():
url = "http://localhost:4040/api/tunnels/"
res = requests.get(url)
res_unicode = res.content.decode("utf-8")
res_json = json.loads(res_unicode)
ngrok_url = ''
for i in res_json["tunnels"]:
    if i['name'] == 'command_line':
        print(i['public_url'])
        ngrok_url = i['public_url']

token = config('TOKEN')
<<<<<<< HEAD
api_url = f'https://api.telegram.org/bot{token}//setWebhook?url={ngrok_url}/{token}'
print('curl '+api_url)
=======
api_url = f'https://api.telegram.org/bot{token}/setWebhook?url={ngrok_url}/{token}'
>>>>>>> 9cda920631906439c1fe8ce3cba03dc4802721e9
os.system('curl '+api_url)
