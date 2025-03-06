#一些基础的功能，被其他的类进行调用
import os,re
from lxml import etree
import requests,time
#MX动漫网页，指定来到“名侦探柯南“页面
url = 'https://mxdm0.com/index.php/vod/detail/id/143.html'

url_1 = 'https://mxdm0.com/index.php/vod/play/id/143/sid/1/nid/6.html'
url_2 = 'https://mxdm0.com/index.php/vod/play/id/143/sid/1/nid/5.html'
movie_total_number = '/html/body/div[2]/div[2]/div/div/div[2]/div/div[1]/div[2]/div[2]/div/div/ul/li'


class Basic_Function():

    #用来进行判断、比较
    def assert_equal_function(self,expected_value,actual_value):
        try:
            assert expected_value == actual_value,'Customize ERROR:!!!!   expected_value is {},but actual_value is {}.'.format(expected_value,actual_value)
        except ValueError as e:
            print(e)

    #对传入的html文件进行xpath的过滤，找到对应xpath出现的次数
    def count_xpath_times(self, content):
        self.capture_each_movie_number_name(content,movie_total_number)

    #所有漫画的集的数量
    def count_movie_total_number(self,content,xpath):
        tree = etree.HTML(content)
        return len(tree.xpath(xpath))

    #得到当前是第几集漫画，并且创建文件夹，并将第几集漫画的所有ts文件放到对应的文件夹中
    def capture_each_movie_number_name(self,content,xpath):
        tree = etree.HTML(content)
        for i in range(self.count_movie_total_number(content,xpath)):
            i = i + 1
            sub_xpath = movie_total_number + "[{}]/a/text()".format(i)
            contents = tree.xpath(sub_xpath)
            for content in contents:
                #content 是  “第001集”字符串
                self.create_sub_movie_directory(content)
                self.handle_sub_url(i,content)

    #创建以动漫名称命名的文件夹
    def create_movie_directory(self):
        current_dir = os.getcwd()
        fold_dir = os.path.join(current_dir,"名侦探柯南")
        if not os.path.exists(fold_dir):
            os.mkdir(fold_dir)
        else:
            pass
        return fold_dir

    #创建以动漫的第几集命名的文件夹
    def create_sub_movie_directory(self,sub_fold_name):
        root_fold = self.create_movie_directory()
        sub_fold = os.path.join(root_fold,sub_fold_name)
        if not os.path.exists(sub_fold):
            os.mkdir(sub_fold)
        else:
            pass
        return sub_fold

    #处理url，处理后可以得到播放页面的url,并拿到页面中的index.m3u8文件,number_CHN是 “第005集”的字符串
    def handle_sub_url(self,number, number_CHN):
        sub_url = url.split("detail")[0] + 'play/id/143/sid/1/nid/{}.html'.format(number)
        res = requests.get(sub_url,timeout=600000)

        ##得到的 res.text 包含了 unicode 例如\u4ea ，通过以下代码进行转义
        unicode_escape_pattern = re.compile(r'\\u([0-9a-fA-F]{4})')
        decoded_text = unicode_escape_pattern.sub(self.replace_unicode_escape, res.text)

        ##转移后的内容中包含 \ ,  通过以下代码将\删掉
        clear_decoded_text = decoded_text.replace("\\", '')

        pattern = re.compile(r"https://c1.*?/index.m3u8")
        result = pattern.findall(clear_decoded_text)

        index_m3u8 = os.path.join(self.create_sub_movie_directory(number_CHN),"index.m3u8")
        if os.path.exists(index_m3u8):
            pass
        else:
            with open(index_m3u8,mode="wt") as f:
                sub = requests.get(result[0],timeout=600000)
                time.sleep(1)
                sub_text = sub.text
                f.write(sub_text)
            f.close()

    # 得到的 res.text 包含了 unicode 例如\u4eae ，通过以下代码进行转义
    def replace_unicode_escape(self,match):
        code_point = int(match.group(1), 16)
        return chr(code_point)














