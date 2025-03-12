#一些基础的功能，被其他的类进行调用
import os,re
from lxml import etree
import requests,time
from concurrent.futures import ThreadPoolExecutor

#MX动漫网页，指定来到“名侦探柯南“页面
url = 'https://www.mxdm123.com/dm/mingzhentankenanguoyuban/'
#https://www.mxdm123.com/play/mingzhentankenanguoyuban-1-1/
url_1 = 'https://mxdm0.com/index.php/vod/play/id/143/sid/1/nid/6.html'
url_2 = 'https://mxdm0.com/index.php/vod/play/id/143/sid/1/nid/5.html'
movie_total_number = '//div[@class="module"]/div/div/div/a'


args = {
    'Cache-Control': 'no-cache',
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
    "TE":"trailers"
}

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
    def new_func(self,i,tree):
        # print("123")
        sub_xpath = movie_total_number + "[{}]/span/text()".format(i)
        # print("sub_xpath is {}".format(sub_xpath))
        contents = tree.xpath(sub_xpath)
        for content in contents:
            #content 是  “第01集”字符串
            self.create_sub_movie_directory(content)
            self.handle_sub_url(i,content)
        # return contents

    #创建线程资源池，并行执行。
    def capture_each_movie_number_name(self,content,xpath):
        tree = etree.HTML(content)
        #理论上total应该通过动态来获得，动漫一共有多少集，然后遍历创建文件夹，但是
        #长时间爬虫导致服务器返回 520 error code， 短时间不能登录网站
        #所以，再次将 total 改成 50，只爬取 第01集 到 第50集的内容
        # total = self.count_movie_total_number(content,xpath)
        with ThreadPoolExecutor(50) as t:
            #for i in range(1,total):
            for i in range(1, 51):
                t.submit(self.new_func,i=i,tree=tree)

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
        sub_url = url.split("/dm/")[0] + '/play/mingzhentankenanguoyuban-1-{}'.format(number)
        res = requests.get(sub_url,timeout=60)
        time.sleep(3)

        ##得到的 res.text 包含了 unicode 例如\u4ea ，通过以下代码进行转义
        unicode_escape_pattern = re.compile(r'\\u([0-9a-fA-F]{4})')
        decoded_text = unicode_escape_pattern.sub(self.replace_unicode_escape, res.text)

        ##转移后的内容中包含 \ ,  通过以下代码将\删掉
        clear_decoded_text = decoded_text.replace("\\", '')

        pattern = re.compile(r"https://play.*?/index.m3u8")
        result = pattern.findall(clear_decoded_text)

        index_m3u8 = os.path.join(self.create_sub_movie_directory(number_CHN),"index.m3u8")
        if os.path.exists(index_m3u8):
            pass
        else:
            with open(index_m3u8,mode="wt") as f:
                sub = requests.get(result[0],timeout=60)
                time.sleep(5)
                sub_text = sub.text
                f.write(sub_text)
                f.close()

        #由于网站的设计， 第一次会得到一个 index.m3u8，里面保存目的 index.m3u8 的url
        with open(index_m3u8,mode='r') as f:
            individual_part = (f.readlines())[-1]
            m3u8_url = result[0].replace(re.findall("/20230816.*?index.m3u8$",result[0])[0],individual_part.strip())
            target_content = requests.get(m3u8_url)
            self.target_index_m3u8 = os.path.join(self.create_sub_movie_directory(number_CHN),"target_index.m3u8")
            with open(self.target_index_m3u8,mode="wt") as tf:
                tf.write(target_content.text)
                tf.close()
        f.close()


    # 得到的 res.text 包含了 unicode 例如\u4eae ，通过以下代码进行转义
    def replace_unicode_escape(self,match):
        code_point = int(match.group(1), 16)
        return chr(code_point)

    #打开 sub_movie_directory 下的 m3u8文件，通过正则表达式找到 00000001.ts 等文件并下载
    def download_ts_files(self):
        """
        先拿到 ‘第01集’ 字符串，作为 ts合并后的 mp4文件的名字，也是后续url的组成部分
        打开 m3u8 文件，通过正则表达式，找到 00001.ts 等文件，并都放在一个列表中
        遍历列表
        # 	https://play.modujx10.com/20230816/c4SGvWHM/1385kb/hls/1OzzpPEJ.jpg
        :return:
        """
        print("12312")
        with ThreadPoolExecutor(50) as T:
            for i in range(50):
                T.submit(self.func_down_ts)

    def func_down_ts(self):
        #查看 名侦探柯南 文件夹下，一共有多少个文件夹
        print("insta")
        conan_dir = os.path.dirname(__file__) + "\名侦探柯南"
        total_dir = os.listdir(conan_dir)
        _len = len(total_dir)
        #遍历每个 ”第01集“ 文件夹，组装 target_index_m3u8 的路径
        for i in total_dir:
            target_index_m3u8 = os.path.join(conan_dir,i,"target_index.m3u8")
            with open(target_index_m3u8, 'r') as target_file:
                ts_list = target_file.readlines()
                for ts_line in ts_list:
                    ts_line = ts_line.strip()
                    if re.findall("/2023.*?jpg$", ts_line) != []:
                        ts_url = "https://play.modujx10.com" + ts_line
                        ts_file_name = ts_line.split("/")[-1].split(".")[0] + '.ts'
                        sub_movie_directory = os.path.join(conan_dir,i,ts_file_name)
                        with open(sub_movie_directory, "wb",encoding="utf-8") as tfn:
                            resp = requests.get(ts_url,params=args)

                            tfn.write(resp.text)

            target_file.close()