import businesstime
from datetime import timedelta, timezone, datetime
from dateutil import parser
from modules.githubapi import GithubApi
from modules.utils import *


def main():
    """ Loop on each issue, extract info, print to CSV """

    # Load cred from file
    with open(SECRETS_DIR + 'auth.s') as fIn:
        # todo: check if lines is not null
        lines = fIn.read().splitlines()
        CLIENT_ID = lines[0]
        CLIENT_SECRET = lines[1]
        ORGANIZATION = lines[2]
        REPO_NAME = lines[3]
        STATE = lines[4]

    # Load names list
    with open(SECRETS_DIR + 'users.s') as f:
        nomi = f.read().splitlines()

    # Set variables
    since = '2019-01-01T00:00:00'
    no_triage = 0
    late_triage = 0
    sol_fine = 0
    fine_flag = False

    # Check DB
    db = check_db()
    if db != False:
        diff = datetime.now().date() - parser.parse(db).date()
        # Leave a 5 days span between 2 interactions
        if diff.days < 5:
            print("Week already covered. Closing")
            return
        else:
            since = str(db, 'utf-8')

    # Load Api Object and get issues
    ghapi = GithubApi(CLIENT_ID, CLIENT_SECRET)
    issues = ghapi.get_issues(ORGANIZATION, REPO_NAME, STATE, since)
    dict_list = []
    bt = businesstime.BusinessTime()

    for i in issues:
        fine_flag = False
        d = {}
        # Get events
        print("Processing... %s" % i['title'])
        d['title'] = i['title']
        d['state'] = i['state']
        d['url'] = i['html_url']
        d['created_by'] = i['user']['login']
        d['created_at'] = parser.parse(i['created_at'], ignoretz=True)

        # TODO: fixme
        events = ghapi.get_url(i['events_url'])
        # Labels - If 'avvisi', go to next issue
        if not i['labels']:
            # events = ghapi.get_url(i['events_url'])
            pass
        else:
            # TODO: Do we need this?
            labelsList = []
            for l in i['labels']:
                if l['name'] == 'avvisi':
                    continue
                labelsList.append(l['name'])
            d['labels'] = labelsList

        ### 1. Triage
        ### a. no-triage
        ### If the issue has not been assigned yet, and it does not have an
        ### 'avvisi' flag, then it a fine occurs.
        ### b. late-triage
        ### If the issue has been assigned late (delta > 1 day), a late triage
        ### fine occurs.

        # 1.a. - no-triage
        if not i['assignee']:
            # Calculate delta (businesstimedelta)
            opened_time = parser.parse(i['created_at'], ignoretz=True)
            now = datetime.now()
            delta = bt.businesstimedelta(opened_time, now)

            if delta.days != 0:
                print("### Penale TRIAGE: %s" % (delta.days*50))
                d['no_triage'] = delta.days*50
                no_triage += d['no_triage']
                fine_flag = True
        # 1.b - late-triage
        else:
            d['assignee'] = i['assignee']['login']
            if i['assignee']['login'] in nomi:
                # Check assignment time
                if events:
                    for e in events:
                        if(e['event'] == 'assigned'):
                            d['assigned_on'] = parser.parse(e['created_at'], ignoretz=True)
                            delta = bt.businesstimedelta(d['created_at'], d['assigned_on'])
                            if delta.days != 0:
                                print("### Penale Late TRIAGE: %s€" % (delta.days*50))
                                d['late_triage'] = delta.days*50
                                late_triage+= d['late_triage']
                                fine_flag = True

        # 2 Solution
        # If there are not comments and delta > 2 days, a fine occurs
        d['comments'] = i['comments']
        if i['comments'] != 0:
            comments = ghapi.get_url(i['comments_url'])
            d['last_comment'] = comments[-1]['updated_at']
            d['last_comment_by'] = comments[-1]['user']['login']
        else:
            # Calculate delta
            opened_time = parser.parse(i['created_at'], ignoretz=True)
            now = datetime.now()
            delta = bt.businesstimedelta(opened_time, now)

            if delta.days >= 2:
                print("### Penale SOLUZIONE: %s€" % delta.days*50)
                d['sol_fine'] = delta.days*50
                sol_fine += d['sol_fine']
                fine_flag = True

        # Check update
        if i['state'] == 'open':
            if i['created_at'] != i['updated_at']:
                if events:
                    for e in events:
                        d['last_update'] = events[-1]['event']
                        d['last_update_by'] = events[-1]['actor']['login']
                        d['last_update_at'] = i['updated_at']
        else:
            d['closed_at'] = i['closed_at']

        if fine_flag:
            dict_list.append(d)

    tpl_render(dict_list, no_triage, late_triage, sol_fine, since)
    move_files()

    with open('private/iterations.db', mode='w') as db_file:
        db_file.write(datetime.now().isoformat())


# Call main
if __name__ == "__main__":
    main()
