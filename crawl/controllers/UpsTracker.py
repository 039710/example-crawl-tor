import gzip
import json
import random
import time
from selenium import webdriver
from seleniumwire import webdriver as wiredriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Tor import Tor
from fake_useragent import UserAgent
import undetected_chromedriver as uc
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class UPSTracker:
    def __init__(self,trackingNumber):
        self.trackingNumber = trackingNumber
        self.trackingInfo = {}
        self.tracking_url = "https://www.ups.com/track?loc=en_US&requester=ST/"
        self.tor = Tor(tor_control_port=9051)
        self.driver = self.initDriver()

    def initDriver(self):
        time.sleep(random.randint(0,1))
        options = uc.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--proxy-server=socks5://127.0.0.1:9050")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-features=NetworkService")
        # disable image loading
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--disable-features=VizDisplayCompositor"
                              ",OptimizeImageLoading,NetworkService"
                              ",NetworkServiceInProcess")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        # enable cookies
        options.add_argument("--enable-cookies")

        driver = uc.Chrome(options=options)
        driver.header_overrides = {
            'User-Agent': UserAgent().random
        }
        driver.scopes = [
            '.*ups.com.*',
        ]
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(60)
        driver.implicitly_wait(60)

        self.driver = driver
        return driver

    def restartDriver(self):
        self.tor.restart_tor_windows()
        self.driver.quit()
        self.driver = self.initDriver()
        self.getTrackingInfo()

    def getResponse(self):
        try:
            cookies = self.driver.get_cookies()
            # convert to dict
            cookies = {cookie["name"]: cookie["value"] for cookie in cookies}
            X_XSRF_TOKEN = cookies["X-XSRF-TOKEN-ST"]
            string_cookies = "; ".join([f"{key}={value}" for key, value in cookies.items()])
            # remove multiple quotes
            string_cookies = string_cookies.replace('"', "")
            data = {
                "locale": "en_US",
                "TrackingNumber": [self.trackingNumber],
            }
            # send xhr request
            # send xhr request
            script = f"""
                return new Promise(function(resolve, reject) {{
                    var xhr = new XMLHttpRequest();
                    xhr.open("POST", "https://www.ups.com/track/api/Track/GetStatus?loc=en_US", true);
                    xhr.setRequestHeader("Content-Type", "application/json");
                    xhr.setRequestHeader("Accept", "application/json, text/javascript, */*; q=0.01");
                    xhr.setRequestHeader("Accept-Language", "en-US,en;q=0.5");
                    xhr.setRequestHeader("Accept-Encoding", "gzip, deflate, br");
                    xhr.setRequestHeader("Host", "www.ups.com");
                    xhr.setRequestHeader("Content-Length", "58");
                    xhr.setRequestHeader("Referer", "https://www.ups.com/track?loc=en_US&requester=ST/");
                    xhr.setRequestHeader("Origin", "https://www.ups.com");
                    xhr.setRequestHeader("x-xsrf-token", "{X_XSRF_TOKEN}");
                    xhr.setRequestHeader("Cookie", "{string_cookies}");
                    xhr.onreadystatechange = function() {{
                        if (this.readyState == 4) {{
                            if (this.status == 200) {{
                                resolve(this.responseText);
                            }} else {{
                                reject(this.status);
                            }}
                        }}
                    }}
                    xhr.send(JSON.stringify({json.dumps(data)}));
                }});
            """
       
            response = self.driver.execute_script(script)
            response = json.loads(response)
            if (response['statusCode'] == 403):
                print("Forbidden")
                self.restartDriver()
                return
            else:
                self.trackingInfo = response
            return response
        except Exception as e:
            print("Blocked")
            print(e)
            self.restartDriver()
            self.getTrackingInfo()

    def getTrackingInfo(self):
        try:
            self.driver.get(self.tracking_url)
            # Wait for the tracking number input field to be visible
            trackingNumberInput = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "stApp_trackingNumber"))
            )
            if trackingNumberInput is None:
                print("Tracking number input field not found")
                self.restartDriver()
            else:
                response = self.getResponse()
                return response
        except Exception as e:
            print("Timeout")
            self.restartDriver()
            return self.getTrackingInfo()
          

if __name__ == "__main__":
    tracker = UPSTracker("1Z03A61V0469573563")
    response = tracker.getTrackingInfo()
    print(response['statusCode'])
    time.sleep(random.randint(0,1))
    iter = 0
    while(True):
        response = tracker.getTrackingInfo()
        if response:
           print(iter, response['statusCode'])
        else:
            print(iter, "Blocked" , response)
        iter += 1
        time.sleep(random.randint(1,2))
