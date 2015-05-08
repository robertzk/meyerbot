from github import Github # Download https://github.com/jacquev6/PyGithub and run setup.py
import re
import datetime

# This class will comment on every pull request in a given repository
# if the pull request lacks any tests and at least ten lines of code and three
# files were changed.
class MeyerBot:

    number_of_latest_pull_requests_to_examine = 1337

    username = None
    gh = None
    repo_name = None
    org = None

    user = None
    owner = None
    repo = None

    def __init__(self, username, password, repo, org = None):
        """
        Given a username, password, and repo (e.g., "avantbasic"), initialize
        a Meyerbot. `org` must be provided if the repo exists not within the
        user's account, but one of the attached organizations.
        """
        self.username = username
        self.gh = Github(username, password)
        self.repo_name = repo
        self.org = org

    def post(self):
        """
        Traverse the ten latest pull requests and comment with "Tests?" if any
        violate the testing heuristic (at least ten lines of code changed but no
        changes in the test directory).
        """
        pull_reqs = self.get_pull_requests()
        for pull_req in pull_reqs:
            if self.is_candidate_pull_request(pull_req):
                if self.is_pull_request_without_pivotal_task(pull_req):
                    pull_req.create_issue_comment("Pivotal task #?")
                if self.is_pull_request_without_tests(pull_req):
                    pull_req.create_issue_comment("Tests?")
                # only posts if tests function returns false    
                elif self.is_pull_request_old(pull_req):
                    pull_req.create_issue_comment("This good to go?")

    def is_candidate_pull_request(self, pull_req):
        """
        Checks if the pull request is shitty (at least ten lines of code changed
        but no tests in the test directory).
        """
        modified_files = [file for file in pull_req.get_files()
                          if not re.search('\\.rb$', file.filename) is None]
        if len(modified_files) < 3:
            return False

        users_that_commented = [comment.user.login for comment in pull_req.get_issue_comments()]
        if self.username in users_that_commented:
            return False

        # We can add + file.deletions to count deletions as well
        lines_modified = sum([file.additions for file in modified_files])
        if lines_modified < 10:
            return False

        return True


    def is_pull_request_without_pivotal_task(self, pull_req):
        """
        Return true or false according as the pull request has an pivotal task
        number (heuristically any 8+ digit string).
        """
        return (re.search('[0-9]{8}', pull_req.body) is None) or \
               (re.search('[0-9]{8}', pull_req.title) is None) or \
               (re.search('pivotal', pull_req.body, re.IGNORECASE) is None) or \
               (re.search('pivotal', pull_req.title, re.IGNORECASE) is None) or \
               not any([self.is_commit_with_pivotal_task(commit) for commit in pull_req.get_commits()])

    def is_commit_with_pivotal_task(self, commit):
        """ 
        Return true or false according as the commit has a pivotal task
        number (heuristically any 8+ digit string).
        """
        message = commit._commit.value._message.value
        return not ((re.search('pivotal', message, re.IGNORECASE) is None) and
                   (re.search('[0-9]{8}', message) is None))

    def is_pull_request_without_tests(self, pull_req):
        """
        Return true or false according as the pull request has tests.
        """
        modified_files = [file for file in pull_req.get_files()
                          if not re.search('\\.rb$', file.filename) is None]

        unit_test_files = [file for file in modified_files \
                           if not ( re.search('^[^/]*tests?/', file.filename) | re.search('^spec/', file.filename) ) is None]

        return len(unit_test_files) == 0

    def is_pull_request_old(self, pull_req):
        """
        Return true or false according as the pull request is older than
        6 days
        """
        return (datetime.datetime.today()-pull_req.created_at).days >= 6
 
    def get_owner(self):
        """
        If an organization was provided, return the organization.
        Otherwise, return the github user.
        """
        if self.user is None:
            self.user = self.gh.get_user()
        if self.org is None:
            return self.user
        if self.owner is None:
            try:
                self.owner = [org for org in self.user.get_orgs() \
                              if org.login.lower() == self.org.lower()][0]
            except Exception as e:
                raise BaseException("Could not find organization '" + str(self.org) + \
                                    "' because: " + str(e))

        return self.owner

    def get_repo(self, owner = None):
        """
        Get a repo by owner.
        """
        if owner is None:
            owner = self.get_owner()

        if self.repo is None:
            try:
                self.repo = [repo for repo in owner.get_repos() if repo.name == self.repo_name][0]
            except Exception as e:
                raise BaseException("Could not find repo '" + str(self.repo_name) + \
                                    "' because: " + str(e))
        return self.repo

    def get_pull_requests(self, repo = None):
        """
        Get the latest pull requests for the specified repo. The default is the
        repo specified for Meyerbot.
        """
        if repo is None:
            repo = self.get_repo()
        return repo.get_pulls()[0:self.number_of_latest_pull_requests_to_examine]
