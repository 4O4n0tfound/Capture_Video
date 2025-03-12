import datetime

from API_function import API_Function
from basic_function import Basic_Function,url
import datetime




if __name__ == "__main__":

    print(datetime.datetime.now())
    Basic_Function().create_movie_directory()
    API_Function().count(url=url)
    Basic_Function().download_ts_files()
    print(datetime.datetime.now())

