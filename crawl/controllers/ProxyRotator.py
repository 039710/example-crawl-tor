
import random
import requests
import os
from dotenv import load_dotenv
load_dotenv()
class ProxyRotator:
    def __init__(self):
        self.proxy_list = []
        self.proxy_index = 0
        # read env file_path from root directory use join path root + env file path
        self.file_path  = os.getenv("PROXY_FILE_PATH")

    def get_proxy_list(self):
        proxy_list = requests.get("https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=responseTime&sort_type=asc").json()
        proxy_list = proxy_list["data"]
        # sort by responseTime first then by upTime
        proxy_list = sorted(proxy_list, key=lambda k: (k['responseTime'], k['upTime']))
        for proxy in proxy_list:
            proxy["proxy"] = proxy["protocols"][0] + "://" + proxy["ip"] + ":" + str(proxy["port"])
            # append proxy to list
            self.add_proxy(proxy["proxy"])
        return self.proxy_list
    

    def load_proxies(self):
        # check if file exists use absolute path
        if os.path.exists(self.file_path):
            with open(self.file_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.proxy_list.append(line)
        else:
            print("File does not exist")


    
    def add_proxy(self, proxy):
        self.proxy_list.append(proxy)

    def get_proxy(self):
        if self.proxy_index >= len(self.proxy_list):
            self.proxy_index = 0
        if (len(self.proxy_list) == 0):
            print("Fetching proxies...")
            self.get_proxy_list()
            return self.get_proxy()
        proxy = self.proxy_list[self.proxy_index]
        self.proxy_index += 1
        if self.test_proxy(proxy):
            return proxy
        else:
            # if not working remove from list and get next proxy
            self.proxy_list.remove(proxy)
            return self.get_proxy()
    

    def get_random_proxy(self):
        if (len(self.proxy_list) == 0):
            print("Fetching proxies...")
            self.get_proxy_list()
            return self.get_random_proxy()
        proxy = self.proxy_list[random.randint(0, len(self.proxy_list) - 1)]
        if self.test_proxy(proxy):
            return proxy
        else:
            # if not working remove from list and get next proxy
            self.proxy_list.remove(proxy)
            return self.get_random_proxy()
    def test_proxy(self, proxy):
        try:
            proxy_type = proxy.split("://")[0]
            proxy_ip = proxy.split("://")[1]
            requests.get("https://www.google.com", proxies={proxy_type: proxy_ip}, timeout=5)
            print("Proxy working: ", proxy)
            return True
        except:
            print("Proxy not working: ", proxy)
            return False
    def check_ip(self, proxy):
        try:
            proxy_type = proxy.split("://")[0]
            proxy_ip = proxy.split("://")[1]
            ip = requests.get("https://api.ipify.org?format=json", proxies={proxy_type: proxy_ip}, timeout=5).json()
            print("IP: ", ip)
            return True
        except:
            print("Proxy not working: ", proxy)
            return False
    
        

