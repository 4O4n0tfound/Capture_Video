import requests,time
from basic_function import Basic_Function


proxy = {
    "https:":"https://218.60.8.83:3129"
}

args = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0"
}
class API_Function():

    #对指定的url发送会话请求,返回response text
    def http_request(self,url):
        session = requests.session()
        time.sleep(3)
        response = session.get(url,timeout=60,proxies=proxy,params=args)
        Basic_Function().assert_equal_function('200',str(response.status_code))
        return response.text

    #用来计算一共有多少集
    def count(self,url):
        response_text = self.http_request(url)
        Basic_Function().count_xpath_times(response_text)


