#!/usr/bin/env python3
import os
import json

import requests
import yaml

from aggregate_github_issues import aggregate_issues

RAW_GITHUB = 'https://raw.githubusercontent.com/'

# We are getting the config via HTTP because "with" in GitHub workflows can
# only pass strings so we avoid writing YAML as a string in YAML.
res = requests.get(RAW_GITHUB + os.environ['GITHUB_REPOSITORY'] + '/master/.github/workflows/instant-issue-repos.yml')

if res.ok:
    repos = yaml.safe_load(res.text)
else:
    repos = [dict(name=os.environ['GITHUB_REPOSITORY'])]

session = requests.Session()

for repo in repos:
    repo['name'] = repo['name'].lower()
    print('STARTING', repo['name'])

    repo.update(aggregate_issues(repo['name'], os.environ['INPUT_TOKEN'], session))
    os.makedirs(repo['name'].split('/')[0], exist_ok=True)
    with open(repo['name'] + '.json', 'w') as f:
        json.dump(repo, f)
