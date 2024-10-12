import requests

bot_token = '7942620159:AAFNJuF4Qb-0AVkzF9N4zKVTBnZV3NSLuWU'
channel_id = '@lootdeal_flipkartamazon'  # Or your Channel ID
message = 'Hello, Telegram!'

url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
data = {'chat_id': channel_id, 'text': message}

response = requests.post(url, data=data)
print(response.json())
