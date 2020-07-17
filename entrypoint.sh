#!/bin/sh
/ci.py

# force push to issues branch
git init
git add .
git -c user.name='instant issues' -c user.email='instantissues@example.com' commit -m 'update'
git push -f https://bot:$INPUT_TOKEN@github.com/$GITHUB_REPOSITORY master:issues
