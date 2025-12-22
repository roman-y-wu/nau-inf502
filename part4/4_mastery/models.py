"""
Data models for GitHub repository analysis.
Contains classes for Repository, PullRequest, User, and License.
"""

from datetime import datetime
from typing import Optional, List


class License:
    """Represents a GitHub repository license."""
    
    def __init__(self, key: str = "", name: str = "", url: str = ""):
        self.key = key
        self.name = name
        self.url = url
    
    def __str__(self) -> str:
        return self.name if self.name else "No License"
    
    def to_csv_string(self) -> str:
        """Return CSV-formatted string of license data."""
        return f"{self.key},{self.name},{self.url}"
    
    @staticmethod
    def get_csv_header() -> str:
        """Return CSV header for license data."""
        return "license_key,license_name,license_url"
    
    @classmethod
    def from_json(cls, data: Optional[dict]) -> 'License':
        """Create License object from JSON dictionary."""
        if data is None:
            return cls()
        return cls(
            key=data.get('key', ''),
            name=data.get('name', ''),
            url=data.get('url', '')
        )


class User:
    """Represents a GitHub user."""
    
    def __init__(self, login: str, num_pull_requests: int = 0,
                 num_repos: int = 0, num_followers: int = 0,
                 num_following: int = 0, num_contributions: int = 0):
        self.login = login
        self.num_pull_requests = num_pull_requests
        self.num_repos = num_repos
        self.num_followers = num_followers
        self.num_following = num_following
        self.num_contributions = num_contributions
    
    def __str__(self) -> str:
        return f"{self.login} ({self.num_pull_requests} PRs)"
    
    def to_csv_string(self) -> str:
        """Return CSV-formatted string of user data."""
        return (f"{self.login},{self.num_pull_requests},{self.num_repos},"
                f"{self.num_followers},{self.num_following},{self.num_contributions}")
    
    @staticmethod
    def get_csv_header() -> str:
        """Return CSV header for user data."""
        return "login,num_pull_requests,num_repos,num_followers,num_following,num_contributions"
    
    @classmethod
    def from_json(cls, data: dict) -> 'User':
        """Create User object from JSON dictionary."""
        return cls(login=data.get('login', ''))
    
    @classmethod
    def from_csv_row(cls, row: dict) -> 'User':
        """Create User object from CSV row dictionary."""
        return cls(
            login=row.get('login', ''),
            num_pull_requests=int(row.get('num_pull_requests', 0)),
            num_repos=int(row.get('num_repos', 0)),
            num_followers=int(row.get('num_followers', 0)),
            num_following=int(row.get('num_following', 0)),
            num_contributions=int(row.get('num_contributions', 0))
        )


class PullRequest:
    """Represents a GitHub pull request."""
    
    def __init__(self, title: str, number: int, body: str, state: str,
                 created_at: str, closed_at: Optional[str], user: str,
                 commits: int = 0, additions: int = 0, deletions: int = 0,
                 changed_files: int = 0, author_association: str = ""):
        self.title = title
        self.number = number
        self.body = body
        self.state = state
        self.created_at = created_at
        self.closed_at = closed_at
        self.user = user
        self.commits = commits
        self.additions = additions
        self.deletions = deletions
        self.changed_files = changed_files
        self.author_association = author_association
    
    def __str__(self) -> str:
        return f"#{self.number}: {self.title} ({self.state})"
    
    def to_csv_string(self) -> str:
        """Return CSV-formatted string of pull request data."""
        # Escape body text for CSV (replace quotes and newlines)
        safe_body = self.body.replace('"', '""').replace('\n', ' ').replace('\r', '') if self.body else ''
        safe_title = self.title.replace('"', '""').replace('\n', ' ').replace('\r', '') if self.title else ''
        closed_at = self.closed_at if self.closed_at else ''
        
        return (f'{self.number},"{safe_title}","{safe_body}",{self.state},'
                f'{self.created_at},{closed_at},{self.user},'
                f'{self.commits},{self.additions},{self.deletions},'
                f'{self.changed_files},{self.author_association}')
    
    @staticmethod
    def get_csv_header() -> str:
        """Return CSV header for pull request data."""
        return ("number,title,body,state,created_at,closed_at,user,"
                "commits,additions,deletions,changed_files,author_association")
    
    @classmethod
    def from_json(cls, issue_data: dict, pr_details: Optional[dict] = None) -> 'PullRequest':
        """Create PullRequest object from JSON dictionaries."""
        user = issue_data.get('user', {})
        user_login = user.get('login', '') if user else ''
        
        # Get pull request URL to extract number
        pr_url = issue_data.get('pull_request', {}).get('url', '')
        number = issue_data.get('number', 0)
        
        # Default values for detailed info
        commits = 0
        additions = 0
        deletions = 0
        changed_files = 0
        author_association = issue_data.get('author_association', '')
        
        # If we have detailed PR data, use it
        if pr_details:
            commits = pr_details.get('commits', 0)
            additions = pr_details.get('additions', 0)
            deletions = pr_details.get('deletions', 0)
            changed_files = pr_details.get('changed_files', 0)
            author_association = pr_details.get('author_association', author_association)
        
        return cls(
            title=issue_data.get('title', ''),
            number=number,
            body=issue_data.get('body', '') or '',
            state=issue_data.get('state', ''),
            created_at=issue_data.get('created_at', ''),
            closed_at=issue_data.get('closed_at'),
            user=user_login,
            commits=commits,
            additions=additions,
            deletions=deletions,
            changed_files=changed_files,
            author_association=author_association
        )
    
    @classmethod
    def from_csv_row(cls, row: dict) -> 'PullRequest':
        """Create PullRequest object from CSV row dictionary."""
        return cls(
            title=row.get('title', ''),
            number=int(row.get('number', 0)),
            body=row.get('body', ''),
            state=row.get('state', ''),
            created_at=row.get('created_at', ''),
            closed_at=row.get('closed_at') if row.get('closed_at') else None,
            user=row.get('user', ''),
            commits=int(row.get('commits', 0)),
            additions=int(row.get('additions', 0)),
            deletions=int(row.get('deletions', 0)),
            changed_files=int(row.get('changed_files', 0)),
            author_association=row.get('author_association', '')
        )


class Repository:
    """Represents a GitHub repository."""
    
    def __init__(self, name: str, owner: str, description: str,
                 homepage: str, license: License, forks: int,
                 watchers: int, stars: int, date_of_collection: str):
        self.name = name
        self.owner = owner
        self.description = description
        self.homepage = homepage
        self.license = license
        self.forks = forks
        self.watchers = watchers
        self.stars = stars
        self.date_of_collection = date_of_collection
        self.pull_requests: List[PullRequest] = []
    
    def __str__(self) -> str:
        desc = self.description[:50] + "..." if self.description and len(self.description) > 50 else (self.description or "No description")
        return f"{self.owner}/{self.name}: {desc} ({self.stars} stars)"
    
    def to_csv_string(self) -> str:
        """Return CSV-formatted string of repository data."""
        safe_desc = self.description.replace('"', '""').replace('\n', ' ').replace('\r', '') if self.description else ''
        homepage = self.homepage if self.homepage else ''
        
        return (f'{self.name},{self.owner},"{safe_desc}",{homepage},'
                f'{self.license.key},{self.license.name},'
                f'{self.forks},{self.watchers},{self.stars},{self.date_of_collection}')
    
    @staticmethod
    def get_csv_header() -> str:
        """Return CSV header for repository data."""
        return ("name,owner,description,homepage,license_key,license_name,"
                "forks,watchers,stars,date_of_collection")
    
    def get_full_name(self) -> str:
        """Return the full repository name (owner/name)."""
        return f"{self.owner}/{self.name}"
    
    @classmethod
    def from_json(cls, data: dict, date_of_collection: Optional[str] = None) -> 'Repository':
        """Create Repository object from JSON dictionary."""
        if date_of_collection is None:
            date_of_collection = datetime.now().strftime('%Y-%m-%d')
        
        owner = data.get('owner', {})
        owner_login = owner.get('login', '') if owner else ''
        
        license_data = data.get('license')
        license_obj = License.from_json(license_data)
        
        return cls(
            name=data.get('name', ''),
            owner=owner_login,
            description=data.get('description', '') or '',
            homepage=data.get('homepage', '') or '',
            license=license_obj,
            forks=data.get('forks_count', 0),
            watchers=data.get('watchers_count', 0),
            stars=data.get('stargazers_count', 0),
            date_of_collection=date_of_collection
        )
    
    @classmethod
    def from_csv_row(cls, row: dict) -> 'Repository':
        """Create Repository object from CSV row dictionary."""
        license_obj = License(
            key=row.get('license_key', ''),
            name=row.get('license_name', '')
        )
        
        return cls(
            name=row.get('name', ''),
            owner=row.get('owner', ''),
            description=row.get('description', ''),
            homepage=row.get('homepage', ''),
            license=license_obj,
            forks=int(row.get('forks', 0)),
            watchers=int(row.get('watchers', 0)),
            stars=int(row.get('stars', 0)),
            date_of_collection=row.get('date_of_collection', '')
        )


