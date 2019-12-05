#!/bin/bash

echo "start dajngo runserver"
nohup python3 /home/ubuntu/telegram_alarm/telegram-django/manage.py runserver &
echo "start ngrok"
nohup ngrok http 8000 &
echo "set webhook"
python3 /home/ubuntu/telegram_alarm/telegram-django/bus/check_ngrok_webhook.py
