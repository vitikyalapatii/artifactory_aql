#!/usr/bin/env python

# Knowing only the repo name and the pull number, acquire the list of subprojects which need
# to be rebuilt. This is done using the pygithub library which, in turn, calls the public github
# API. A Github Personal Access Token may be needed for access permission. A maven command is
# emitted to STDOUT which may be immediately executed (try backticks). If verbose is chosen, the
# extra messages are sent to STDERR so the maven command may be separately captured easily.
# The main reason for this program is to restore efficiency to the rebuild process and not
# rebuild all subprojects when only a few have been changed.

#   Usage: getRebuildProjects.py [-h] -p PULLREQUEST [-t TOKENNAME] [-v]
#   
#   Optional arguments:
#     -h, --help                                Show this help message and exit
#     -p PULLREQUEST, --pullRequest PULLREQUEST Pull Request string in form "org/repo:prNumber".
#     -t TOKENNAME,   --tokenName TOKENNAME     Github Personal Access Token environment variable name.
#     -v, --verbose                             Display more info during run.
#
# Example usage:
#   export GITHUB_PAT=5874244bd24222c44a444b345349a34f3434d3402
#   getRebuildProjects.py -p relateiq/graph-streams:196 -t GITHUB_PAT -v


author__ = "walter.murphy"
__version__ = "0.2"

import os, sys, argparse
import github

def main(patnm, pullreq, verbose):
    # 'patnm' is the Github 'Personal Access Token' name
    # 'pullreq' is the PullRequest ID in form: 'relateiq/graph-streams:196'
    #   where part before ':' is github repo path fragment and after is pull number.

    tc_pat = os.environ.get(patnm)
    if tc_pat is None:
        g = github.Github()
    else:
        g = github.Github(tc_pat)

    try:
        repoName, pullstr = pullreq.split(':')
        pr = int(pullstr)
    except (ValueError):
        sys.stderr.write("Incorrectly formatted PullRequest specifier.\n")
        sys.exit(1)

    try:
        repo = g.get_repo(repoName)
        pull = repo.get_pull(pr)
        pgList = pull.get_files()
    except (github.UnknownObjectException, github.BadCredentialsException):
        sys.stderr.write("Bad credentials or unrecognized Git Repo or Pull number.\n")
        sys.exit(1)

    if verbose:
        sys.stderr.write("  Title: {}\n".format(pull.title))
        sys.stderr.write("  Files changed: {}\n".format(pgList.totalCount) )

    pl = set()
    for f in pgList.get_page(0):
        if '/' not in f.filename: continue  #
        pl.add( f.filename.split('/')[0] )

    if len(pl) is 0:
        cmd = "mvn install integration-test"
    else:
        cmd = "mvn install integration-test -pl {} -am".format(','.join(list(pl)))

    print(cmd)


if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--pullRequest', help='Pull Request string in form "org/repo:prNumber".', required=True)
  parser.add_argument('-t', '--tokenName', help='Github Personal Access Token environment variable name.')
  parser.add_argument('-v', '--verbose', help='Display more info during run.', action='store_true', default=False)
  args = vars(parser.parse_args())

  verbose = True if args['verbose'] else False

  main(args['tokenName'], args['pullRequest'], verbose)


