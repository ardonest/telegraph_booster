import random
import requests
import threading
import time
import os
import socket
import resource
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class TelegraphBooster:
    def __init__(self):
        resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))
        socket.setdefaulttimeout(10)
        self.url = self.get_valid_url()
        self.target_views = self.get_target_views()
        self.dns_servers = ['1.1.1.1', '8.8.8.8', '9.9.9.9', '208.67.222.222', '64.6.64.6', '84.200.69.80', '8.26.56.26', '185.228.168.9', '76.76.19.19', '94.140.14.14']
        self.proxies = self.setup_proxies()
        self.success = 0
        self.failed = 0
        self.lock = threading.Lock()
        self.ua = UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        self.active_threads = 0
        self.max_threads = 500
        self.running = True
        self.user_agents = [self.ua.google, self.ua.firefox, self.ua.safari, self.ua.chrome]

    def get_valid_url(self):
        while True:
            url = input("Введите ссылку на Telegraph статью: ").strip()
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            if 'telegra.ph' in url or 'graph.org' in url:
                return url
            print("Ошибка: неверная ссылка")

    def get_target_views(self):
        while True:
            try:
                views = int(input("Введите количество просмотров: "))
                if views > 0:
                    return views
                print("Число должно быть больше 0")
            except ValueError:
                print("Введите целое число")

    def setup_proxies(self):
        proxy_choice = input("Использовать прокси? (y/t/n): ").lower()
        if proxy_choice == 'n':
            return None
        elif proxy_choice == 't':
            return {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
        elif proxy_choice == 'y':
            return self.setup_custom_proxies()
        else:
            return None

    def setup_custom_proxies(self):
        proxy_type = input("Тип прокси (http/socks4/socks5): ").lower()
        proxy_file = input("Путь к файлу с прокси: ")
        if not os.path.exists(proxy_file):
            raise FileNotFoundError("Файл не найден")
        with open(proxy_file, 'r') as f:
            proxies_list = [line.strip() for line in f if line.strip()]
        proxies = []
        for proxy in proxies_list:
            if proxy_type == 'http':
                proxies.append({'http': f'http://{proxy}', 'https': f'http://{proxy}'})
            elif proxy_type == 'socks4':
                proxies.append({'http': f'socks4://{proxy}', 'https': f'socks4://{proxy}'})
            elif proxy_type == 'socks5':
                proxies.append({'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'})
            else:
                raise ValueError("Неверный тип прокси")
        print(f"Загружено {len(proxies)} прокси")
        return proxies

    def create_session(self):
        session = requests.Session()
        retry = Retry(total=2, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry, pool_connections=500, pool_maxsize=500, pool_block=False)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def get_random_proxy(self):
        if not self.proxies:
            return None
        return random.choice(self.proxies) if isinstance(self.proxies, list) else self.proxies

    def get_random_user_agent(self):
        return random.choice(self.user_agents)

    def make_request(self):
        if not self.running or self.success >= self.target_views:
            return False
        try:
            with self.lock:
                self.active_threads += 1
            session = self.create_session()
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': random.choice(['https://google.com', 'https://yandex.ru', 'https://bing.com']),
                'DNT': str(random.randint(0, 1)),
                'Connection': 'keep-alive'
            }
            time.sleep(random.uniform(0.01, 0.1))
            response = session.get(
                self.url,
                headers=headers,
                proxies=self.get_random_proxy(),
                timeout=5,
                allow_redirects=True
            )
            session.close()
            if response.status_code == 200:
                with self.lock:
                    self.success += 1
                    print(f"\rУспешно: {self.success}/{self.target_views} | Ошибок: {self.failed}", end='', flush=True)
                return True
        except Exception:
            with self.lock:
                self.failed += 1
        finally:
            with self.lock:
                self.active_threads -= 1
        return False

    def start(self):
        print(f"\nЗапуск для: {self.url}")
        print(f"Цель: {self.target_views}")
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = set()
            try:
                while self.success < self.target_views and self.running:
                    while len(futures) < self.max_threads * 3 and self.success < self.target_views:
                        futures.add(executor.submit(self.make_request))
                    completed = {f for f in futures if f.done()}
                    futures -= completed
                    time.sleep(0.01)
                for future in as_completed(futures):
                    pass
            except KeyboardInterrupt:
                self.running = False
                print("\nОстановлено!")
        total_time = time.time() - start_time
        print(f"\n\nУспешно: {self.success}")
        print(f"Ошибок: {self.failed}")
        print(f"Время: {total_time:.2f} сек")
        print(f"Скорость: {self.success/max(1, total_time):.2f} просмотров/сек")

if __name__ == "__main__":
    try:
        booster = TelegraphBooster()
        booster.start()
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        exit(1)
