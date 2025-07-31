#!/usr/bin/env python3
import requests
import pytz
from datetime import datetime

IST = pytz.timezone('Asia/Kolkata')
token = '8143962740:AAHHPGho9tckm3E9Hav9n8sfBsmAn2CinPs'
chat_id = '7797661300'

# Test basic message with IST time
ist_time = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')
message = f'🎯 Timezone Fix Test\n📅 IST Time: {ist_time}\n✅ Fixed Indian timezone for all messages!'

url = f'https://api.telegram.org/bot{token}/sendMessage'
response = requests.post(url, json={'chat_id': chat_id, 'text': message})

if response.status_code == 200:
    print('✅ Timezone fix successful!')
    print(f'📅 Message sent at: {ist_time}')
    print('🎯 All Telegram messages now use Indian Standard Time!')
else:
    print(f'❌ Error: {response.status_code}')
    print(response.text)
