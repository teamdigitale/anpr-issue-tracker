import csv
import datetime
from datetime import timedelta
from modules.githubapi import GithubApi
from modules.utils import office_time_between
from dateutil import parser


# Load cred from file
with open('credentials.txt') as fIn:
    lines = fIn.read().splitlines()
    CLIENT_ID = lines[0]
    CLIENT_SECRET = lines[1]
    ORGANIZATION = lines[2]
    REPO_NAME = lines[3]
    STATE = lines[4]

# Load names list
with open('auth_names.txt') as f:
    nomi = f.read().splitlines()

# Load Api Object and get issues
ghapi = GithubApi(CLIENT_ID, CLIENT_SECRET)
issues = ghapi.get_issues(ORGANIZATION, REPO_NAME, STATE)
dictList = []

def main():
    """ Loop on each issue, extract info, print to CSV """
    for i in issues:
        avvisi_flag = False
        d = {}
        # Get events
        events = ghapi.get_url(i['events_url'])
        print("Processing... %s" % i['title'])
        d['title'] = i['title']
        d['state'] = i['state']
        d['url'] = i['html_url']
        d['created_by'] = i['user']['login']
        d['created_at'] = parser.parse(i['created_at'])

        # Labels 
        if not i['labels']:
            avvisi_flag = False 
        else:
            labelsList = []
            for l in i['labels']: 
                if l['name'] == 'avvisi': 
                    avvisi_flag = True 
                labelsList.append(l['name'])
            d['labels'] = labelsList
        
        # Triage
        if not i['assignee']:
            # Calculate delta for fine
            opened_time = parser.parse(i['created_at'])
            now = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
            delta = office_time_between(opened_time, now)
            lateH, lateM = divmod(delta.total_seconds()/3600, 8)
            d['delta_triage'] = (lateH, lateM) 
            if not avvisi_flag and lateH != 0:
                print("### Multa TRIAGE: %s€" % (lateH*50))
                d['multa_triage'] = lateH*50
        else:
            d['assignee'] = i['assignee']['login']
            # if i['assignee']['login'] in nomi:
            # Check when assignment was done
            if events:
                for e in events:
                    if(e['event'] == 'assigned'):
                        d['assigned_on'] = parser.parse(e['created_at'])
                        delta = office_time_between(d['created_at'], d['assigned_on'])
                        lateH, lateM = divmod(delta.total_seconds()/3600, 8)
                        d['delta_res'] = (lateH, lateM) 
                        if not avvisi_flag and lateH != 0:
                            print("### Multa RES: %s€" % (lateH*50))
                            d['multa_res'] = lateH*50
       
        # Comments 
        d['comments'] = i['comments']
        if i['comments'] != 0:
            comments = ghapi.get_url(i['comments_url'])
            d['last_comment'] = comments[-1]['updated_at']
            d['last_comment_by'] = comments[-1]['user']['login']

        # Check update 
        if(i['state'] == 'open'):
            if i['created_at'] != i['updated_at']:
                if events:
                    for e in events:
                        d['last_update'] = events[-1]['event']
                        d['last_update_by'] = events[-1]['actor']['login']
                        d['last_update_at'] = i['updated_at']
        else:
            d['closed_at'] = i['closed_at']

        dictList.append(d)

    # Print to CSV file
    with open('report.csv', mode='w') as report_file:
        fieldnames = ['title', 'state', 'url', 'created_by', 'created_at', 'assignee',
                 'assigned_on', 'delta_triage', 'multa_triage', 'delta_res', 'multa_res', 'labels', 'comments',
                 'last_comment', 'last_comment_by',
                'last_update', 'last_update_by', 'last_update_at', 'closed_at']
        writer = csv.DictWriter(report_file, fieldnames=fieldnames)
        writer.writeheader()
        for d in dictList:
            writer.writerow(d)

# Call main 
if __name__ == "__main__":
    main()
