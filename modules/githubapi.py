import requests
import json
from dateutil import parser
from github import Github

class GithubApi:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id 
        self.client_secret = client_secret 

    def get_url(self, URL):
        """ Get URL specified in args """
        payload = '?client_id=' + self.client_id
        payload += '&client_secret=' + self.client_secret
        return requests.get(URL +payload).json()
 
    def get_issues(self, organization_name, repository_name, state):
        """ Get issues as list """
        issues_list = []
        counter = 1
        base_url = 'https://api.github.com/repos/'
        base_url += organization_name + '/'
        base_url += repository_name + '/issues?'

        while True:
            payload = 'state=' + state
            payload += '&page=' + str(counter)
            payload += '&client_id=' + self.client_id
            payload += '&client_secret=' + self.client_secret
            req_url = base_url + payload
            json_res = requests.get(req_url).json()
            issues_list += json_res
            counter += 1
            if len(json_res) == 0:
                break
        
        return issues_list
    
    def get_closing_times(self, issues_list):
        """ Get issue closing time """
        closing_times = []
        for issue in issues_list:
            status = issue['state']
            if status == 'closed':
                created_at = parser.parse(issue['created_at'])
                closed_at = parser.parse(issue['closed_at'])
                delta_t = (closed_at - created_at).total_seconds()
                closing_times.append(delta_t)
        return closing_times
