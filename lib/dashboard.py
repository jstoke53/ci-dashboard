import queue, math
from threading import Thread
from lib.tools import Tools
from lib.repositories import Repositories

class Dashboard:
    def __init__(self):
        self.__tools = Tools()
        self.__config = self.__tools.read_config()
        self.repos = self.__config['repos']
        self.threads = self.__config['threads']
        self.grid_size = self.__config['grid_size']
        self.repos_per_page = int(math.pow(self.grid_size, 2))

    def fetch(self, **kwargs):
        if 'page' in kwargs:
            page = int(kwargs.pop('page'))
            last_page = False
            start = (page - 1) * self.repos_per_page
            end = start + self.repos_per_page

            if kwargs:
                all_repos = self.fetch_builds(** kwargs)
                all_repos = [repo for repo in all_repos if repo['last_build']]
                number_of_repos = len(all_repos)  
                end = min(end, number_of_repos)       
                repos = all_repos[start:end]         
            else:
                number_of_repos = len(self.repos)
                end = min(end, number_of_repos)
                repos = self.fetch_builds(start=start, end=end)

            if end >= number_of_repos:
                last_page = True 

            pages = math.ceil(number_of_repos / self.repos_per_page)
            headers = {'pages': pages, 'last_page': last_page}
            return headers, repos

        else:
            repos = self.fetch_builds(**kwargs)
            if kwargs:
                repos = [repo for repo in repos if repo['last_build']]
                
            headers = {}
            return headers, repos
            

    def fetch_builds(self, start=0, end=None, **kwargs):
        self.__dashboard_data = []
        self.__repos_queue = queue.Queue()

        for repo in self.repos[start:end]:
            self.__repos_queue.put(repo)
             
        self.__start_job(job=self.__collect_data, kwargs=kwargs)
        sorted_data = sorted(self.__dashboard_data, key=lambda k: k['info']['slug'])
        return sorted_data


    def __collect_data(self, **kwargs):
        while not self.__repos_queue.empty():
            slug = self.__repos_queue.get()
            repo = Repositories().repo(slug)
            data = { 'info': repo.info(), 'last_build':repo.last_build(**kwargs)}   
            self.__dashboard_data.append(data)


    def __start_job(self, job, kwargs):
        threads_list = []
        for _ in range(self.threads):
            t = Thread(target=job, kwargs=kwargs)
            threads_list.append(t)
            t.start()

        for thread in threads_list:
            thread.join()
            