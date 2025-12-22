"""
GitHub REST API v3 interaction module.
Handles all API calls to GitHub for repositories, pull requests, and users.
"""

import requests
import time
from typing import Optional, List, Tuple
from datetime import datetime

from models import Repository, PullRequest, User


class GitHubAPI:
    """Class to interact with GitHub REST API v3."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub API client.
        
        Args:
            token: Optional GitHub personal access token for higher rate limits
        """
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Analyzer-App'
        })
        if token:
            self.session.headers.update({
                'Authorization': f'token {token}'
            })
    
    def _make_request(self, url: str, params: Optional[dict] = None) -> Optional[dict]:
        """
        Make a GET request to the API with rate limit handling.
        
        Args:
            url: The URL to request
            params: Optional query parameters
            
        Returns:
            JSON response as dictionary or None if request fails
        """
        try:
            response = self.session.get(url, params=params)
            
            # Check for rate limiting
            if response.status_code == 403:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                if reset_time:
                    wait_time = reset_time - int(time.time()) + 1
                    if wait_time > 0:
                        print(f"Rate limited. Waiting {wait_time} seconds...")
                        time.sleep(min(wait_time, 60))  # Wait max 60 seconds
                        return self._make_request(url, params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def get_repository(self, owner: str, repo_name: str) -> Optional[Repository]:
        """
        Fetch repository information from GitHub.
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            
        Returns:
            Repository object or None if not found
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo_name}"
        data = self._make_request(url)
        
        if data:
            return Repository.from_json(data)
        return None
    
    def get_pull_requests(self, owner: str, repo_name: str) -> List[PullRequest]:
        """
        Fetch pull requests for a repository using the search API.
        Returns the first page of results.
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            
        Returns:
            List of PullRequest objects
        """
        url = f"{self.BASE_URL}/search/issues"
        params = {
            'q': f'is:pr repo:{owner}/{repo_name}',
            'per_page': 30
        }
        
        data = self._make_request(url, params)
        
        if not data or 'items' not in data:
            return []
        
        pull_requests = []
        for item in data['items']:
            # Get detailed PR info for commits, additions, deletions, changed_files
            pr_number = item.get('number')
            pr_details = self.get_pull_request_details(owner, repo_name, pr_number)
            
            pr = PullRequest.from_json(item, pr_details)
            pull_requests.append(pr)
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        return pull_requests
    
    def get_pull_request_details(self, owner: str, repo_name: str, 
                                  pr_number: int) -> Optional[dict]:
        """
        Fetch detailed information about a specific pull request.
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            pr_number: Pull request number
            
        Returns:
            Dictionary with PR details or None if not found
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo_name}/pulls/{pr_number}"
        return self._make_request(url)
    
    def get_rate_limit(self) -> dict:
        """
        Get current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        url = f"{self.BASE_URL}/rate_limit"
        data = self._make_request(url)
        return data if data else {}


def collect_repository_data(owner: str, repo_name: str, 
                           token: Optional[str] = None) -> Tuple[Optional[Repository], 
                                                                  List[PullRequest], 
                                                                  List[User]]:
    """
    Collect all data for a repository including PRs and users.
    
    Args:
        owner: Repository owner username
        repo_name: Repository name
        token: Optional GitHub token
        
    Returns:
        Tuple of (Repository, list of PullRequests, list of Users)
    """
    api = GitHubAPI(token)
    
    print(f"Fetching repository info for {owner}/{repo_name}...")
    repo = api.get_repository(owner, repo_name)
    
    if not repo:
        print(f"Repository {owner}/{repo_name} not found.")
        return None, [], []
    
    print(f"Found: {repo}")
    
    print(f"Fetching pull requests...")
    pull_requests = api.get_pull_requests(owner, repo_name)
    print(f"Found {len(pull_requests)} pull requests.")
    
    # Collect unique users from pull requests
    user_prs = {}
    for pr in pull_requests:
        if pr.user:
            if pr.user not in user_prs:
                user_prs[pr.user] = 0
            user_prs[pr.user] += 1
    
    users = []
    for login, pr_count in user_prs.items():
        user = User(login=login, num_pull_requests=pr_count)
        users.append(user)
    
    print(f"Found {len(users)} unique users.")
    
    repo.pull_requests = pull_requests
    
    return repo, pull_requests, users


