"""
Unit tests for GitHub Repository Analyzer.
Contains at least 5 unit tests as required.
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime

from models import License, User, PullRequest, Repository
from data_manager import to_CSV, load_repositories, load_users, load_pull_requests
from scraper import GitHubScraper


class TestLicenseModel(unittest.TestCase):
    """Tests for the License class."""
    
    def test_license_from_json(self):
        """Test creating License from JSON data."""
        data = {
            'key': 'mit',
            'name': 'MIT License',
            'url': 'https://api.github.com/licenses/mit'
        }
        
        license_obj = License.from_json(data)
        
        self.assertEqual(license_obj.key, 'mit')
        self.assertEqual(license_obj.name, 'MIT License')
        self.assertEqual(license_obj.url, 'https://api.github.com/licenses/mit')
    
    def test_license_from_none(self):
        """Test creating License from None returns empty license."""
        license_obj = License.from_json(None)
        
        self.assertEqual(license_obj.key, '')
        self.assertEqual(license_obj.name, '')
        self.assertEqual(str(license_obj), 'No License')
    
    def test_license_csv_string(self):
        """Test License CSV string generation."""
        license_obj = License(key='apache-2.0', name='Apache License 2.0', url='http://example.com')
        csv_str = license_obj.to_csv_string()
        
        self.assertIn('apache-2.0', csv_str)
        self.assertIn('Apache License 2.0', csv_str)


class TestUserModel(unittest.TestCase):
    """Tests for the User class."""
    
    def test_user_creation(self):
        """Test basic user creation."""
        user = User(
            login='testuser',
            num_pull_requests=5,
            num_repos=10,
            num_followers=100,
            num_following=50,
            num_contributions=500
        )
        
        self.assertEqual(user.login, 'testuser')
        self.assertEqual(user.num_pull_requests, 5)
        self.assertEqual(user.num_repos, 10)
        self.assertEqual(user.num_followers, 100)
    
    def test_user_from_json(self):
        """Test creating User from JSON data."""
        data = {'login': 'jsonuser'}
        user = User.from_json(data)
        
        self.assertEqual(user.login, 'jsonuser')
        self.assertEqual(user.num_pull_requests, 0)
    
    def test_user_csv_string(self):
        """Test User CSV string generation."""
        user = User(login='csvuser', num_pull_requests=3, num_repos=5)
        csv_str = user.to_csv_string()
        
        self.assertIn('csvuser', csv_str)
        self.assertIn('3', csv_str)
        self.assertIn('5', csv_str)
    
    def test_user_str_representation(self):
        """Test User string representation."""
        user = User(login='displayuser', num_pull_requests=7)
        str_repr = str(user)
        
        self.assertIn('displayuser', str_repr)
        self.assertIn('7 PRs', str_repr)


class TestPullRequestModel(unittest.TestCase):
    """Tests for the PullRequest class."""
    
    def test_pull_request_creation(self):
        """Test basic PullRequest creation."""
        pr = PullRequest(
            title='Test PR',
            number=123,
            body='This is a test',
            state='open',
            created_at='2024-01-15T10:00:00Z',
            closed_at=None,
            user='testuser',
            commits=5,
            additions=100,
            deletions=50,
            changed_files=3
        )
        
        self.assertEqual(pr.title, 'Test PR')
        self.assertEqual(pr.number, 123)
        self.assertEqual(pr.state, 'open')
        self.assertEqual(pr.commits, 5)
        self.assertIsNone(pr.closed_at)
    
    def test_pull_request_csv_escaping(self):
        """Test that special characters are escaped in CSV."""
        pr = PullRequest(
            title='PR with "quotes" and\nnewlines',
            number=456,
            body='Body with "quotes"',
            state='closed',
            created_at='2024-01-15',
            closed_at='2024-01-20',
            user='user1'
        )
        
        csv_str = pr.to_csv_string()
        
        # Quotes should be doubled, newlines removed
        self.assertNotIn('\n', csv_str)
        self.assertIn('""', csv_str)  # Escaped quotes
    
    def test_pull_request_str_representation(self):
        """Test PullRequest string representation."""
        pr = PullRequest(
            title='My Pull Request',
            number=789,
            body='',
            state='open',
            created_at='',
            closed_at=None,
            user='user1'
        )
        
        str_repr = str(pr)
        
        self.assertIn('#789', str_repr)
        self.assertIn('My Pull Request', str_repr)
        self.assertIn('open', str_repr)


class TestRepositoryModel(unittest.TestCase):
    """Tests for the Repository class."""
    
    def test_repository_creation(self):
        """Test basic Repository creation."""
        license_obj = License(key='mit', name='MIT License')
        repo = Repository(
            name='testrepo',
            owner='testowner',
            description='A test repository',
            homepage='https://example.com',
            license=license_obj,
            forks=10,
            watchers=100,
            stars=500,
            date_of_collection='2024-01-15'
        )
        
        self.assertEqual(repo.name, 'testrepo')
        self.assertEqual(repo.owner, 'testowner')
        self.assertEqual(repo.stars, 500)
        self.assertEqual(repo.get_full_name(), 'testowner/testrepo')
    
    def test_repository_from_json(self):
        """Test creating Repository from JSON data."""
        data = {
            'name': 'jsonrepo',
            'owner': {'login': 'jsonowner'},
            'description': 'From JSON',
            'homepage': '',
            'license': {'key': 'gpl-3.0', 'name': 'GPL 3.0'},
            'forks_count': 5,
            'watchers_count': 50,
            'stargazers_count': 200
        }
        
        repo = Repository.from_json(data)
        
        self.assertEqual(repo.name, 'jsonrepo')
        self.assertEqual(repo.owner, 'jsonowner')
        self.assertEqual(repo.license.key, 'gpl-3.0')
        self.assertEqual(repo.stars, 200)
    
    def test_repository_str_representation(self):
        """Test Repository string representation includes stars."""
        license_obj = License()
        repo = Repository(
            name='myproject',
            owner='myowner',
            description='Cool project',
            homepage='',
            license=license_obj,
            forks=0,
            watchers=0,
            stars=1000,
            date_of_collection='2024-01-15'
        )
        
        str_repr = str(repo)
        
        self.assertIn('myowner/myproject', str_repr)
        self.assertIn('1000 stars', str_repr)


class TestCSVOperations(unittest.TestCase):
    """Tests for CSV file operations."""
    
    def setUp(self):
        """Set up temporary directory for test files."""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_to_csv_creates_file(self):
        """Test that to_CSV creates a new file with header."""
        user = User(login='newuser', num_pull_requests=1)
        filename = 'test_users.csv'
        
        to_CSV(filename, user)
        
        self.assertTrue(os.path.exists(filename))
        
        with open(filename, 'r') as f:
            content = f.read()
            self.assertIn('login', content)  # Header
            self.assertIn('newuser', content)  # Data
    
    def test_to_csv_appends_data(self):
        """Test that to_CSV appends to existing file."""
        user1 = User(login='user1', num_pull_requests=1)
        user2 = User(login='user2', num_pull_requests=2)
        filename = 'test_users.csv'
        
        to_CSV(filename, user1)
        to_CSV(filename, user2)
        
        with open(filename, 'r') as f:
            lines = f.readlines()
            # Should have header + 2 data lines
            self.assertEqual(len(lines), 3)
    
    def test_to_csv_no_duplicates(self):
        """Test that to_CSV doesn't add duplicate entries."""
        user = User(login='sameuser', num_pull_requests=1)
        filename = 'test_users.csv'
        
        to_CSV(filename, user)
        to_CSV(filename, user)  # Try to add same user
        
        with open(filename, 'r') as f:
            lines = f.readlines()
            # Should have header + 1 data line (not 2)
            self.assertEqual(len(lines), 2)
    
    def test_to_csv_creates_directory(self):
        """Test that to_CSV creates directory if needed."""
        user = User(login='diruser', num_pull_requests=1)
        filename = 'subdir/test_users.csv'
        
        to_CSV(filename, user)
        
        self.assertTrue(os.path.exists('subdir'))
        self.assertTrue(os.path.exists(filename))


class TestScraperUtilities(unittest.TestCase):
    """Tests for scraper utility functions."""
    
    def test_parse_number_simple(self):
        """Test parsing simple numbers."""
        scraper = GitHubScraper()
        
        self.assertEqual(scraper._parse_number('100'), 100)
        self.assertEqual(scraper._parse_number('0'), 0)
        self.assertEqual(scraper._parse_number('5,000'), 5000)
    
    def test_parse_number_with_k(self):
        """Test parsing numbers with 'k' suffix."""
        scraper = GitHubScraper()
        
        self.assertEqual(scraper._parse_number('1k'), 1000)
        self.assertEqual(scraper._parse_number('1.5k'), 1500)
        self.assertEqual(scraper._parse_number('2.5K'), 2500)
    
    def test_parse_number_with_m(self):
        """Test parsing numbers with 'm' suffix."""
        scraper = GitHubScraper()
        
        self.assertEqual(scraper._parse_number('1m'), 1000000)
        self.assertEqual(scraper._parse_number('1.5M'), 1500000)
    
    def test_parse_number_empty_or_invalid(self):
        """Test parsing empty or invalid input."""
        scraper = GitHubScraper()
        
        self.assertEqual(scraper._parse_number(''), 0)
        self.assertEqual(scraper._parse_number('abc'), 0)
        self.assertEqual(scraper._parse_number(None), 0)


class TestDataManagerLoading(unittest.TestCase):
    """Tests for data loading functions."""
    
    def setUp(self):
        """Set up temporary directory for test files."""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up temporary directory."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_load_repositories_empty(self):
        """Test loading from non-existent file returns empty list."""
        repos = load_repositories('nonexistent.csv')
        self.assertEqual(repos, [])
    
    def test_load_users_empty(self):
        """Test loading from non-existent file returns empty list."""
        users = load_users('nonexistent.csv')
        self.assertEqual(users, [])
    
    def test_load_pull_requests_empty(self):
        """Test loading from non-existent repo returns empty list."""
        prs = load_pull_requests('nonexistent', 'repo')
        self.assertEqual(prs, [])


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)


