import requests
from basic_function import Basic_Function


class API_Function():

    #对指定的url发送会话请求,返回response text
    def http_request(self,url):
        session = requests.session()
        response = session.get(url,timeout=600000)
        Basic_Function().assert_equal_function('200',str(response.status_code))
        return response.text

    #用来计算一共有多少集
    def count(self,url):
        response_text = self.http_request(url)
        Basic_Function().count_xpath_times(response_text)


