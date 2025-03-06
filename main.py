from API_function import API_Function
from basic_function import Basic_Function,url




if __name__ == "__main__":
    Basic_Function().create_movie_directory()
    API_Function().count(url=url)

