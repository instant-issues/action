FROM python:3.7-alpine

RUN apk --update --no-cache add git && pip install requests

COPY aggregate_github_issues.py /aggregate_github_issues.py
COPY entrypoint.sh /entrypoint.sh
