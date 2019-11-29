from lib.clients import Clients
from lib.repository import Repository

class Repositories(Clients):
    def __init__(self):  
        super().__init__()
              
    def list(self):
        repos = self.fetch_repos()
        return repos

    def fetch_repos(self):
        hasMore = True
        offset = 0
        limit = 100
        repos = []
        print('Fetching...')
        while(hasMore):
            print('requesting')
            response = self._Clients__travis_client.repos(offset=offset, limit=limit, active=True).json()
            repos += [repo['slug'] for repo in response['repositories']]
            hasMore = response['@pagination']['is_last'] == False
            if (hasMore):
                offset = response['@pagination']['next']['offset']
                limit = response['@pagination']['next']['limit'] 
        return repos

    def repo(self, slug):
        return Repository(slug)
