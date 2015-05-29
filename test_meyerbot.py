import unittest
from meyerbot import MeyerBot

class PrTestDouble:
    title = None
    body = None

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def get_commits(self):
        return []

class TestMeyerBot(unittest.TestCase):

    def setUp(self):
        self.bot = MeyerBot('user', 'pass', 'repo')

    def test_pr_with_pivotal_number_in_title(self):
        pr = PrTestDouble('My PR title #12345678', 'My PR description')
        self.assertFalse(self.bot.is_pull_request_without_pivotal_task(pr))

    def test_pr_with_pivotal_number_in_body(self):
        pr = PrTestDouble('My PR title', 'My PR description #12345678')
        self.assertFalse(self.bot.is_pull_request_without_pivotal_task(pr))

    def test_pr_with_pivotal_word_in_title(self):
        pr = PrTestDouble('My PR title with Pivotal word', 'My PR description')
        self.assertFalse(self.bot.is_pull_request_without_pivotal_task(pr))

    def test_pr_with_pivotal_word_in_body(self):
        pr = PrTestDouble('My PR title', 'My PR description with Pivotal word')
        self.assertFalse(self.bot.is_pull_request_without_pivotal_task(pr))

    def test_pr_without_any_pivotal_reference(self):
        pr = PrTestDouble('My PR title without references', 'My PR description without references')
        self.assertTrue(self.bot.is_pull_request_without_pivotal_task(pr))

if __name__ == '__main__':
    unittest.main()
