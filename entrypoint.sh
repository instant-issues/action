#!/bin/sh
for repo in $INPUT_REPOS; do
	repo=$(echo $repo | tr '[:upper:]' '[:lower:]')
	mkdir -p $(dirname $repo)
	TOKEN=$INPUT_TOKEN /aggregate_github_issues.py $repo > $repo.json
done

# force push to issues branch
git init
git add .
git -c user.name='instant issues' -c user.email='instantissues@example.com' commit -m 'update'
git push -f https://bot:$INPUT_TOKEN@github.com/$GITHUB_REPOSITORY master:issues
