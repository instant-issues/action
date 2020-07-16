#!/usr/bin/env python3
import argparse
import json
import os
import sys
from collections import defaultdict
import itertools

import requests

REPOS_API = 'https://api.github.com/repos/'

def find_common_almost_disjoint_labels(sorted_labels, labels, issues):
    top10_labels = [l['name'] for l in sorted_labels[:10]]
    label_neighbors = defaultdict(lambda: defaultdict(lambda: 0))

    for issue in issues:
        top_labels = [l for l in issue['labels'] if l in top10_labels]

        for a, b in itertools.product(top_labels, top_labels):
            if a != b:
                label_neighbors[a][b] += 1

    major_labels = set()

    for label, others in label_neighbors.items():
        for other, count in list(others.items()):
            if count / labels[other]['issueCount'] < 0.02:
                major_labels.add(label)
    return major_labels

def aggregate_issues(repo, session):
    issues = []
    pulls = []

    page = 1

    session = requests.Session()

    label_counts = defaultdict(lambda: [0, 0]) # {label_name: [issue_count, pull_count]}
    labels = {}

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
                labels[label['name']] = dict(name=label['name'], description=label['description'])
                label_counts[label['name']][is_pull] += 1
        page += 1

    sorted_labels = []
    for name, (issue_count, pull_count) in sorted(label_counts.items(), key = lambda x: x[1], reverse=True):
        labels[name]['issueCount'] = issue_count
        labels[name]['pullCount'] = pull_count
        sorted_labels.append(labels[name])

    return dict(
        repo = args.repo,
        labels = sorted_labels,
        issues = sorted(issues, key = lambda x: x['title'].lower()),
        pulls = sorted(pulls, key = lambda x: x['title'].lower()),
        commonAlmostDisjointLabels = sorted(find_common_almost_disjoint_labels(sorted_labels, labels, issues), key=lambda l: labels[l]['issueCount'], reverse=True)
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('repo', help='e.g. gittenburg/instant-issues')
    args = parser.parse_args()

    print(json.dumps(aggregate_issues(args.repo, requests.Session())))
