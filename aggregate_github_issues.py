#!/usr/bin/env python3
import argparse
import json
import os
import sys
from collections import defaultdict

import requests

REPOS_API = 'https://api.github.com/repos/'

def aggregate_issues(repo, session):
    issues = []
    pulls = []

    page = 1

    session = requests.Session()

    label_colors = {}
    label_counts = defaultdict(lambda: [0, 0]) # {label_name: [issue_count, pull_count]}

    while True:
        print('fetching page %s' % page, file=sys.stderr)
        res = session.get(REPOS_API + repo + '/issues', params=dict(per_page=100, page=page, q='is:issue'),
            headers={'Authorization': 'token ' + os.environ['TOKEN']})
        res.raise_for_status()

        results = res.json()
        if len(results) == 0:
            break

        for result in res.json():
            issue = dict(num=result['number'], title=result['title'], labels=[l['name'] for l in result['labels']])

            # /issues of the GitHub v3 API returns both issues and pulls
            is_pull = 'pull_request' in result
            if is_pull:
                pulls.append(issue)
            else:
                issues.append(issue)
            for label in result['labels']:
                label_colors[label['name']] = label['color']
                label_counts[label['name']][is_pull] += 1
        page += 1
    return dict(
        repo = args.repo,
        labelColors = label_colors,
        labels = [dict(name=x[0], issueCount=x[1][0], pullCount=x[1][1]) for x in sorted(label_counts.items(), key = lambda x: x[1], reverse=True)],
        issues = sorted(issues, key = lambda x: x['title'].lower()),
        pulls = sorted(pulls, key = lambda x: x['title'].lower())
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', help='e.g. gittenburg/instant-issues')
    args = parser.parse_args()

    print(json.dumps(aggregate_issues(args.repo, requests.Session())))
