import requests
from bs4 import BeautifulSoup
import time
import os
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

# File paths to store processed URLs and texts
processed_urls_file = 'processed_urls.txt'
processed_texts_file = 'processed_texts.txt'

# Initialize sets and queues
processed_urls = set()
processed_texts = set()
url_queue = Queue()

# Load processed data from files
def load_processed_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return set(f.read().splitlines())
    return set()

processed_urls = load_processed_data(processed_urls_file)
processed_texts = load_processed_data(processed_texts_file)

# Function to write processed data to a file
def write_to_file(file_path, data):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"{data}\n")

# Telegram configuration
bot_token = '7942620159:AAFNJuF4Qb-0AVkzF9N4zKVTBnZV3NSLuWU'
channel_id = '@lootdeal_flipkartamazon'

# Headers for HTTP requests
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'X-user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 FKUA/website/41/website/Desktop',
    'Referer': 'https://www.flipkart.com/sellers?pid=HSAFFJWT2WUYHHX',
    'Content-Type': 'application/json',
    'Origin': 'https://www.flipkart.com',
    'Host': 'www.flipkart.com',
    'Pragma': 'no-cache'
}

# Function to shorten URL using is.gd
def shorten_url(long_url):
    try:
        response = requests.get(f"https://is.gd/create.php?format=simple&url={long_url}")
        if response.status_code == 200:
            return response.text.strip()
        else:
            print(f"Failed to shorten URL: {long_url}")
            return long_url
    except Exception as e:
        print(f"Error shortening URL: {e}")
        return long_url

# Function to send a message to Telegram
def send_telegram_message(message):
    telegram_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {'chat_id': channel_id, 'text': message}

    try:
        response = requests.post(telegram_url, data=data)
        print(f"Sent message: {message}, Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")

# Function to process a single URL
def process_url(url, line, request_count):
    global processed_urls

    if url in processed_urls:
        print(f"Skipping already processed URL: {url}")
        return
    processed_urls.add(url)
    write_to_file(processed_urls_file, url)

    try:
        response = requests.get(url, headers=headers, timeout=40)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Process page content
        obj = soup.find_all(attrs={"data-id": True})
        records = []

        for result in obj:
            try:
                name = result.find(attrs={'class': 'yiggsN O5Fpg8'})
                if name:
                    sale = name.text
                    if sale in ['Top Discount of the Sale']:
                        link = result.find(attrs={"rel": True}).get('href', "")
                        text_temp = link.split('/')
                        text = text_temp[1].replace("-", " ") if len(text_temp) > 1 else "N/A"
                        rate = result.find(attrs={'class': 'hl05eU'}).text.split('₹')[1] if result.find(attrs={'class': 'hl05eU'}) else "N/A"
                        discount = result.find(attrs={'class': 'UkUFwK'}).text.replace("% off", "") if result.find(attrs={'class': 'UkUFwK'}) else "N/A"

                        # Final message
                        long_url = f"https://www.flipkart.com{link}"
                        #short_url = shorten_url(long_url)
                        message = f"{text} at ₹{rate}\n{long_url}"
                        #print(link)
                        if text in processed_texts:
                            print(f"Skipping duplicate text: {text}")
                            continue
                        processed_texts.add(text)
                        write_to_file(processed_texts_file, text)

                        records.append(message)

            except Exception as e:
                print(f"Error processing result: {e}")

        # Send messages to Telegram
        for record in records:
            send_telegram_message(record)
            request_count += 1
            if request_count % 20 == 0:
                time.sleep(40)  # Rate-limiting

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")

# Function to load URLs into the queue
def load_urls_from_sitemap(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            for page in range(1, 10):  # Example: pages 1 to 9
                url = f"https://www.flipkart.com/search?q={line}&page={page}"
                print(url)
                if url not in processed_urls:
                    url_queue.put((url, line))
                    print(f"URL added to queue: {url}")

# Worker function to process URLs from the queue
def url_worker(request_count):
    while not url_queue.empty():
        url, line = url_queue.get()
        process_url(url, line, request_count)
        url_queue.task_done()

# Main function to process sitemap
def process_sitemap():
    load_urls_from_sitemap('sitemap.txt')

    # Process URLs using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:
        for _ in range(10):  # Number of workers
            executor.submit(url_worker, 0)

# Start processing
process_sitemap()
