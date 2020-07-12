# Instant Issues Action

This is a GitHub Action for [Instant Issues](https://github.com/instant-issues/instant-issues.github.io).

This action aggregates all open issues into a single JSON file and force pushes
it to the `issues` branch, so that the [Instant Issues frontend](https://instant-issues.github.io)
can download it from `raw.githubusercontent.com`.

## Upstream workflow

Create `.github/workflows/aggregate-issues.yml` with the following content:

```yaml
name: Aggregate issues for Instant Issues

on:
  issues:
    types: [opened, closed, reopened, edited, deleted]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: instant-issues/action@master
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        repos: ${{ github.repository }}
```

## Downstream workflow

Create `.github/workflows/aggregate-issues.yml` with the following content:

```yaml
name: Aggregate issues for Instant Issues

on:
  push:
  schedule:
    # run every hour
    - cron: '0 * * * *'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: instant-issues/action@master
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        repos: |
               someorg/somerepo1
               someorg/somerepo2
```

## Technical Background

* Uploading GitHub artificats is more straightforward than force pushing
  but that's not an option because they [don't have a persistent download URL](https://github.com/actions/upload-artifact/issues/60).

* Uploading release assets is more straightforward than force pushing
  but that's not an option because the assets are served without the `Access-Control-Allow-Origin` header.

* To not needlessly spam GitHub we upload issues using a force push. Since the
  [GitHub REST API](https://developer.github.com/v3/repos/contents/) does not
  provide an endpoint for force pushing, we do the force pushing by running
  `git` in Docker.
