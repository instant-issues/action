FROM python:3.7-alpine

RUN apk --update --no-cache add git && pip install requests pyyaml

COPY entrypoint.sh /entrypoint.sh
COPY ci.py /ci.py
COPY aggregate_github_issues.py /aggregate_github_issues.py
