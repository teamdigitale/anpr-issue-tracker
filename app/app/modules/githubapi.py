""" Middleware for interacting with GH APIs """
import requests
import json
from github import Github

class GithubApi(object):
    """ Class for handling the GitHub API """
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_url(self, URL):
        """ Get URL specified in args """
        payload = '?client_id=' + self.client_id
        payload += '&client_secret=' + self.client_secret
        return requests.get(URL +payload).json()

    def get_issues(self, organization_name, repository_name, state, since):
        """ Get issues as list """
        issues_list = []
        counter = 1
        base_url = 'https://api.github.com/repos/'
        base_url += organization_name + '/'
        base_url += repository_name + '/issues?'

        while True:
            payload = 'since=' + since
            payload += '&state=' + state
            payload += '&page=' + str(counter)
            payload += '&client_id=' + self.client_id
            payload += '&client_secret=' + self.client_secret
            req_url = base_url + payload
            json_res = requests.get(req_url).json()
            issues_list += json_res
            counter = counter + 1
            if len(json_res) == 0:
                break
        return issues_list
