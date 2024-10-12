import requests
from bs4 import BeautifulSoup
import json
import time
request_count=1
bot_token = '7942620159:AAFNJuF4Qb-0AVkzF9N4zKVTBnZV3NSLuWU'
channel_id = '@lootdeal_flipkartamazon'  # Or your Channel ID

headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 FKUA/website/41/website/Desktop',
            'Referer' :   'https://www.flipkart.com/sellers?pid=HSAFFJWT2WUYHHX',
            'Content-Type': 'application/json',
            'Origin': 'https://www.flipkart.com',
            'Host': 'www.flipkart.com',
            'Pragma': 'no-cache'
            }
with open('sitemap.txt', 'r') as file:
 for line in file:
  line=line.strip() 
  for i in range(1,10):
    
    url = "https://www.flipkart.com/search?q="+str(line)+"&page=" + str(i)
    print(url)
    filename="files/"+line+".txt"
    f = open(filename, "a",encoding="utf-8")
#payLoad = {"requestContext":{"productId":"HSAFFJWT2WUYHHHX"},"locationContext":{"pincode":"001195"}}
    response = requests.get(url,headers = headers)
#print(response.status_code,response.reason)
    soup = BeautifulSoup(response.content, "html.parser")

 #obj = soup.find_all(attrs={"class": "_75nlfW"})
    obj = soup.find_all(attrs={"data-id": True })
    records = []  
    for result in obj:  
    
     if(result):
       name = result.find(attrs={'class':'yiggsN O5Fpg8'} )
       names=str(name)
       
       if (names != "None"):
             sale=name.text
             if (sale == 'Top Discount of the Sale') or (sale == 'Lowest price in the year') or (sale == 'Lowest price since launch'):
                 link = result.find(attrs={"rel": True}).get('href')
                 text_TEMP =  link.split('/');
                 text= text_TEMP[1].replace("-", " ")
                 rate= result.find(attrs={'class':'hl05eU'}).text.split('₹')[1]
                 discount= result.find(attrs={'class':'UkUFwK'}).text
                 discount_percentage=discount.replace("% off","")
                 #text =  result.find(attrs={"rel": True}).text[14:50]
                 temp= text + ' at  ₹' + rate + '\nhttps://www.flipkart.com' + link
                 #temp=discount
                 records.append((temp))
    
    for i in records:
 
     print(i)
     print('\n')
     message = i
     url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
     data = {'chat_id': channel_id, 'text': message} 
     
     request_count=request_count+1
     #print(request_count)
     if(request_count%20 == 0):
          time.sleep(40)
     response = requests.post(url, data=data)
     print(response.json())
     f.write(i+'\n')
f.close()






#obj_price= BeautifulSoup(obj,'lxml')
#obj2= obj.text
#print (obj_price)
#price= obj.find_all(attrs={"class": "yiggsN O5Fpg8"})
#print(price)


#for entry in obj:
   # print(entry.text)
#print(response.request.headers) 