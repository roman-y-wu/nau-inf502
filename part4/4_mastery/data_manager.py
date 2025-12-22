"""
Data manager module for CSV file operations.
Handles saving and loading data to/from CSV files.
"""

import os
import csv
from typing import List, Optional, Type, TypeVar, Union

from models import Repository, PullRequest, User


T = TypeVar('T', Repository, PullRequest, User)


def to_CSV(filename: str, obj: Union[Repository, PullRequest, User]) -> None:
    """
    Save an object to a CSV file.
    If the file doesn't exist, create it with headers.
    If it exists, append the new row (avoiding duplicates).
    
    Args:
        filename: Path to the CSV file
        obj: Object to save (Repository, PullRequest, or User)
    """
    # Ensure directory exists
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # Get header and data from object
    header = obj.get_csv_header()
    data = obj.to_csv_string()
    
    # Check if file exists
    file_exists = os.path.isfile(filename)
    
    # If file exists, check for duplicates
    if file_exists:
        # Get unique identifier based on object type
        unique_id = _get_unique_id(obj)
        
        if _entry_exists(filename, obj, unique_id):
            return  # Skip duplicate
    
    # Write to file
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        if not file_exists:
            f.write(header + '\n')
        f.write(data + '\n')


def _get_unique_id(obj: Union[Repository, PullRequest, User]) -> str:
    """
    Get the unique identifier for an object.
    
    Args:
        obj: The object to get ID for
        
    Returns:
        String identifier
    """
    if isinstance(obj, Repository):
        return f"{obj.owner}/{obj.name}"
    elif isinstance(obj, PullRequest):
        return str(obj.number)
    elif isinstance(obj, User):
        return obj.login
    return ""


def _entry_exists(filename: str, obj: Union[Repository, PullRequest, User], 
                  unique_id: str) -> bool:
    """
    Check if an entry already exists in the CSV file.
    
    Args:
        filename: Path to the CSV file
        obj: Object to check
        unique_id: Unique identifier for the object
        
    Returns:
        True if entry exists, False otherwise
    """
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if isinstance(obj, Repository):
                    if f"{row.get('owner', '')}/{row.get('name', '')}" == unique_id:
                        return True
                elif isinstance(obj, PullRequest):
                    if row.get('number', '') == unique_id:
                        return True
                elif isinstance(obj, User):
                    if row.get('login', '') == unique_id:
                        return True
    except (IOError, csv.Error):
        return False
    
    return False


def update_user_csv(filename: str, user: User) -> None:
    """
    Update or add a user in the CSV file.
    If user exists, update their PR count. Otherwise, add new entry.
    
    Args:
        filename: Path to the CSV file
        user: User object to save/update
    """
    # Ensure directory exists
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    header = user.get_csv_header()
    
    if not os.path.isfile(filename):
        # File doesn't exist, create with header and add user
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            f.write(header + '\n')
            f.write(user.to_csv_string() + '\n')
        return
    
    # Read existing users
    existing_users = load_users(filename)
    
    # Check if user exists and update
    user_found = False
    for i, existing in enumerate(existing_users):
        if existing.login == user.login:
            # Update PR count by adding
            existing.num_pull_requests += user.num_pull_requests
            # Update other fields with new data if they're greater
            existing.num_repos = max(existing.num_repos, user.num_repos)
            existing.num_followers = max(existing.num_followers, user.num_followers)
            existing.num_following = max(existing.num_following, user.num_following)
            existing.num_contributions = max(existing.num_contributions, user.num_contributions)
            user_found = True
            break
    
    if not user_found:
        existing_users.append(user)
    
    # Rewrite file with updated data
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        f.write(header + '\n')
        for u in existing_users:
            f.write(u.to_csv_string() + '\n')


def load_repositories(filename: str = 'projects.csv') -> List[Repository]:
    """
    Load all repositories from CSV file.
    
    Args:
        filename: Path to the CSV file
        
    Returns:
        List of Repository objects
    """
    repos = []
    
    if not os.path.isfile(filename):
        return repos
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                repo = Repository.from_csv_row(row)
                repos.append(repo)
    except (IOError, csv.Error) as e:
        print(f"Error loading repositories: {e}")
    
    return repos


def load_pull_requests(owner: str, repo_name: str) -> List[PullRequest]:
    """
    Load pull requests for a specific repository.
    
    Args:
        owner: Repository owner username
        repo_name: Repository name
        
    Returns:
        List of PullRequest objects
    """
    filename = f"projects/{owner}-{repo_name}.csv"
    pull_requests = []
    
    if not os.path.isfile(filename):
        return pull_requests
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pr = PullRequest.from_csv_row(row)
                pull_requests.append(pr)
    except (IOError, csv.Error) as e:
        print(f"Error loading pull requests: {e}")
    
    return pull_requests


def load_all_pull_requests() -> List[tuple]:
    """
    Load all pull requests from all repositories.
    
    Returns:
        List of tuples (owner/repo, PullRequest)
    """
    all_prs = []
    
    if not os.path.isdir('projects'):
        return all_prs
    
    for filename in os.listdir('projects'):
        if filename.endswith('.csv'):
            # Extract owner and repo from filename
            name_parts = filename[:-4].split('-', 1)  # Remove .csv and split
            if len(name_parts) == 2:
                owner, repo_name = name_parts
                prs = load_pull_requests(owner, repo_name)
                for pr in prs:
                    all_prs.append((f"{owner}/{repo_name}", pr))
    
    return all_prs


def load_users(filename: str = 'users.csv') -> List[User]:
    """
    Load all users from CSV file.
    
    Args:
        filename: Path to the CSV file
        
    Returns:
        List of User objects
    """
    users = []
    
    if not os.path.isfile(filename):
        return users
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user = User.from_csv_row(row)
                users.append(user)
    except (IOError, csv.Error) as e:
        print(f"Error loading users: {e}")
    
    return users


def save_repository(repo: Repository) -> None:
    """Save a repository to projects.csv."""
    to_CSV('projects.csv', repo)


def save_pull_requests(owner: str, repo_name: str, 
                       pull_requests: List[PullRequest]) -> None:
    """
    Save pull requests to a repository-specific CSV file.
    
    Args:
        owner: Repository owner username
        repo_name: Repository name
        pull_requests: List of PullRequest objects
    """
    filename = f"projects/{owner}-{repo_name}.csv"
    
    for pr in pull_requests:
        to_CSV(filename, pr)


def save_users(users: List[User]) -> None:
    """
    Save users to users.csv, updating existing entries.
    
    Args:
        users: List of User objects
    """
    for user in users:
        update_user_csv('users.csv', user)


def get_repository_summary(owner: str, repo_name: str) -> dict:
    """
    Get summary statistics for a repository.
    
    Args:
        owner: Repository owner username
        repo_name: Repository name
        
    Returns:
        Dictionary with summary statistics
    """
    prs = load_pull_requests(owner, repo_name)
    
    open_count = sum(1 for pr in prs if pr.state == 'open')
    closed_count = sum(1 for pr in prs if pr.state == 'closed')
    
    # Get unique users
    users = set(pr.user for pr in prs if pr.user)
    
    # Get oldest PR date
    oldest_date = None
    for pr in prs:
        if pr.created_at:
            pr_date = pr.created_at[:10]  # Get just the date part
            if oldest_date is None or pr_date < oldest_date:
                oldest_date = pr_date
    
    return {
        'open_prs': open_count,
        'closed_prs': closed_count,
        'num_users': len(users),
        'oldest_pr_date': oldest_date or 'N/A'
    }

