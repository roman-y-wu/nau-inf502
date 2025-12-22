"""
Visualization module for GitHub data analysis.
Creates various charts and graphs using matplotlib and seaborn.
"""

import os
from typing import List, Tuple
from collections import defaultdict
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np

from models import PullRequest, User, Repository
from data_manager import load_pull_requests, load_all_pull_requests, load_users, load_repositories


# Set style for all plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


def ensure_output_dir():
    """Ensure the output directory for graphs exists."""
    if not os.path.exists('graphs'):
        os.makedirs('graphs')


def create_repo_boxplot_commits(owner: str, repo_name: str) -> str:
    """
    Create a boxplot comparing closed and open pull requests by number of commits.
    
    Args:
        owner: Repository owner username
        repo_name: Repository name
        
    Returns:
        Path to saved figure
    """
    ensure_output_dir()
    prs = load_pull_requests(owner, repo_name)
    
    if not prs:
        print("No pull requests found.")
        return ""
    
    # Separate by state
    open_commits = [pr.commits for pr in prs if pr.state == 'open']
    closed_commits = [pr.commits for pr in prs if pr.state == 'closed']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    data = []
    labels = []
    if open_commits:
        data.append(open_commits)
        labels.append(f'Open ({len(open_commits)})')
    if closed_commits:
        data.append(closed_commits)
        labels.append(f'Closed ({len(closed_commits)})')
    
    if data:
        bp = ax.boxplot(data, labels=labels, patch_artist=True)
        colors = ['#3498db', '#e74c3c']
        for patch, color in zip(bp['boxes'], colors[:len(data)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
    
    ax.set_xlabel('Pull Request State', fontsize=12)
    ax.set_ylabel('Number of Commits', fontsize=12)
    ax.set_title(f'Commits: Open vs Closed PRs\n{owner}/{repo_name}', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    filepath = f'graphs/{owner}-{repo_name}-commits-boxplot.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filepath


def create_repo_boxplot_additions_deletions(owner: str, repo_name: str) -> str:
    """
    Create a boxplot comparing closed and open pull requests by additions and deletions.
    
    Args:
        owner: Repository owner username
        repo_name: Repository name
        
    Returns:
        Path to saved figure
    """
    ensure_output_dir()
    prs = load_pull_requests(owner, repo_name)
    
    if not prs:
        print("No pull requests found.")
        return ""
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Additions boxplot
    open_additions = [pr.additions for pr in prs if pr.state == 'open']
    closed_additions = [pr.additions for pr in prs if pr.state == 'closed']
    
    data_add = []
    labels_add = []
    if open_additions:
        data_add.append(open_additions)
        labels_add.append('Open')
    if closed_additions:
        data_add.append(closed_additions)
        labels_add.append('Closed')
    
    if data_add:
        bp1 = axes[0].boxplot(data_add, labels=labels_add, patch_artist=True)
        for patch, color in zip(bp1['boxes'], ['#2ecc71', '#27ae60']):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
    
    axes[0].set_xlabel('State', fontsize=11)
    axes[0].set_ylabel('Additions', fontsize=11)
    axes[0].set_title('Additions', fontsize=12, fontweight='bold')
    
    # Deletions boxplot
    open_deletions = [pr.deletions for pr in prs if pr.state == 'open']
    closed_deletions = [pr.deletions for pr in prs if pr.state == 'closed']
    
    data_del = []
    labels_del = []
    if open_deletions:
        data_del.append(open_deletions)
        labels_del.append('Open')
    if closed_deletions:
        data_del.append(closed_deletions)
        labels_del.append('Closed')
    
    if data_del:
        bp2 = axes[1].boxplot(data_del, labels=labels_del, patch_artist=True)
        for patch, color in zip(bp2['boxes'], ['#e74c3c', '#c0392b']):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
    
    axes[1].set_xlabel('State', fontsize=11)
    axes[1].set_ylabel('Deletions', fontsize=11)
    axes[1].set_title('Deletions', fontsize=12, fontweight='bold')
    
    fig.suptitle(f'Additions & Deletions: Open vs Closed PRs\n{owner}/{repo_name}', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    filepath = f'graphs/{owner}-{repo_name}-add-del-boxplot.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filepath


def create_repo_boxplot_changed_files_by_author(owner: str, repo_name: str) -> str:
    """
    Create a boxplot of changed files grouped by author association.
    
    Args:
        owner: Repository owner username
        repo_name: Repository name
        
    Returns:
        Path to saved figure
    """
    ensure_output_dir()
    prs = load_pull_requests(owner, repo_name)
    
    if not prs:
        print("No pull requests found.")
        return ""
    
    # Group by author association
    by_association = defaultdict(list)
    for pr in prs:
        assoc = pr.author_association if pr.author_association else 'UNKNOWN'
        by_association[assoc].append(pr.changed_files)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if by_association:
        data = list(by_association.values())
        labels = [f'{k}\n({len(v)})' for k, v in by_association.items()]
        
        bp = ax.boxplot(data, labels=labels, patch_artist=True)
        colors = plt.cm.Set3(np.linspace(0, 1, len(data)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
    
    ax.set_xlabel('Author Association', fontsize=12)
    ax.set_ylabel('Number of Changed Files', fontsize=12)
    ax.set_title(f'Changed Files by Author Association\n{owner}/{repo_name}', 
                 fontsize=14, fontweight='bold')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    filepath = f'graphs/{owner}-{repo_name}-changed-files-boxplot.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filepath


def create_repo_scatter_additions_deletions(owner: str, repo_name: str) -> str:
    """
    Create a scatter plot of additions vs deletions.
    
    Args:
        owner: Repository owner username
        repo_name: Repository name
        
    Returns:
        Path to saved figure
    """
    ensure_output_dir()
    prs = load_pull_requests(owner, repo_name)
    
    if not prs:
        print("No pull requests found.")
        return ""
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    additions = [pr.additions for pr in prs]
    deletions = [pr.deletions for pr in prs]
    states = [pr.state for pr in prs]
    
    # Color by state
    colors = ['#3498db' if s == 'open' else '#e74c3c' for s in states]
    
    scatter = ax.scatter(additions, deletions, c=colors, alpha=0.6, s=50, edgecolors='white')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#3498db', label='Open'),
                       Patch(facecolor='#e74c3c', label='Closed')]
    ax.legend(handles=legend_elements, loc='upper right')
    
    ax.set_xlabel('Additions', fontsize=12)
    ax.set_ylabel('Deletions', fontsize=12)
    ax.set_title(f'Additions vs Deletions\n{owner}/{repo_name}', fontsize=14, fontweight='bold')
    
    # Add diagonal line for reference
    max_val = max(max(additions) if additions else 0, max(deletions) if deletions else 0)
    if max_val > 0:
        ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.3, label='Equal ratio')
    
    plt.tight_layout()
    filepath = f'graphs/{owner}-{repo_name}-scatter-add-del.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filepath


def create_repo_histogram_commits(owner: str, repo_name: str) -> str:
    """
    Create a histogram of commits per pull request.
    
    Args:
        owner: Repository owner username
        repo_name: Repository name
        
    Returns:
        Path to saved figure
    """
    ensure_output_dir()
    prs = load_pull_requests(owner, repo_name)
    
    if not prs:
        print("No pull requests found.")
        return ""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    commits = [pr.commits for pr in prs]
    
    ax.hist(commits, bins=30, color='#9b59b6', alpha=0.7, edgecolor='white')
    
    ax.set_xlabel('Number of Commits', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(f'Distribution of Commits per PR\n{owner}/{repo_name}', 
                 fontsize=14, fontweight='bold')
    
    # Add mean line
    mean_commits = np.mean(commits)
    ax.axvline(mean_commits, color='#e74c3c', linestyle='--', linewidth=2,
               label=f'Mean: {mean_commits:.1f}')
    ax.legend()
    
    plt.tight_layout()
    filepath = f'graphs/{owner}-{repo_name}-commits-histogram.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filepath


# ============ ALL REPOSITORIES GRAPHS ============

def create_all_prs_line_per_day() -> str:
    """
    Create a line graph showing total pull requests per day across all repos.
    
    Returns:
        Path to saved figure
    """
    ensure_output_dir()
    all_prs = load_all_pull_requests()
    
    if not all_prs:
        print("No pull requests found.")
        return ""
    
    # Count PRs by date
    prs_by_date = defaultdict(int)
    for repo_name, pr in all_prs:
        if pr.created_at:
            date = pr.created_at[:10]
            prs_by_date[date] += 1
    
    # Sort by date
    sorted_dates = sorted(prs_by_date.keys())
    counts = [prs_by_date[d] for d in sorted_dates]
    
    # Convert to datetime for better plotting
    dates = [datetime.strptime(d, '%Y-%m-%d') for d in sorted_dates]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(dates, counts, color='#3498db', linewidth=2, marker='o', markersize=4)
    ax.fill_between(dates, counts, alpha=0.3, color='#3498db')
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Number of Pull Requests', fontsize=12)
    ax.set_title('Total Pull Requests per Day (All Repositories)', 
                 fontsize=14, fontweight='bold')
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    filepath = 'graphs/all-prs-per-day.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filepath


def create_all_prs_line_open_closed_per_day() -> str:
    """
    Create a line graph comparing open and closed PRs per day.
    
    Returns:
        Path to saved figure
    """
    ensure_output_dir()
    all_prs = load_all_pull_requests()
    
    if not all_prs:
        print("No pull requests found.")
        return ""
    
    # Count by state and date
    open_by_date = defaultdict(int)
    closed_by_date = defaultdict(int)
    
    for repo_name, pr in all_prs:
        if pr.created_at:
            date = pr.created_at[:10]
            if pr.state == 'open':
                open_by_date[date] += 1
            else:
                closed_by_date[date] += 1
    
    # Get all unique dates
    all_dates = sorted(set(list(open_by_date.keys()) + list(closed_by_date.keys())))
    
    open_counts = [open_by_date.get(d, 0) for d in all_dates]
    closed_counts = [closed_by_date.get(d, 0) for d in all_dates]
    
    dates = [datetime.strptime(d, '%Y-%m-%d') for d in all_dates]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(dates, open_counts, color='#3498db', linewidth=2, marker='o', 
            markersize=4, label='Open')
    ax.plot(dates, closed_counts, color='#e74c3c', linewidth=2, marker='s', 
            markersize=4, label='Closed')
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Number of Pull Requests', fontsize=12)
    ax.set_title('Open vs Closed Pull Requests per Day (All Repositories)', 
                 fontsize=14, fontweight='bold')
    ax.legend()
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    filepath = 'graphs/all-prs-open-closed-per-day.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filepath


def create_all_users_per_repo_bar() -> str:
    """
    Create a bar chart showing number of users per repository.
    
    Returns:
        Path to saved figure
    """
    ensure_output_dir()
    all_prs = load_all_pull_requests()
    
    if not all_prs:
        print("No pull requests found.")
        return ""
    
    # Count unique users per repo
    users_per_repo = defaultdict(set)
    for repo_name, pr in all_prs:
        if pr.user:
            users_per_repo[repo_name].add(pr.user)
    
    repos = list(users_per_repo.keys())
    user_counts = [len(users_per_repo[r]) for r in repos]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(repos)))
    bars = ax.bar(repos, user_counts, color=colors, edgecolor='white')
    
    # Add value labels on bars
    for bar, count in zip(bars, user_counts):
        height = bar.get_height()
        ax.annotate(f'{count}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Repository', fontsize=12)
    ax.set_ylabel('Number of Users', fontsize=12)
    ax.set_title('Number of Users per Repository', fontsize=14, fontweight='bold')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    filepath = 'graphs/all-users-per-repo-bar.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filepath


def create_all_commits_histogram() -> str:
    """
    Create a histogram of commits per pull request across all repos.
    
    Returns:
        Path to saved figure
    """
    ensure_output_dir()
    all_prs = load_all_pull_requests()
    
    if not all_prs:
        print("No pull requests found.")
        return ""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    commits = [pr.commits for _, pr in all_prs]
    
    ax.hist(commits, bins=30, color='#1abc9c', alpha=0.7, edgecolor='white')
    
    ax.set_xlabel('Number of Commits', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Distribution of Commits per PR (All Repositories)', 
                 fontsize=14, fontweight='bold')
    
    mean_commits = np.mean(commits)
    ax.axvline(mean_commits, color='#e74c3c', linestyle='--', linewidth=2,
               label=f'Mean: {mean_commits:.1f}')
    ax.legend()
    
    plt.tight_layout()
    filepath = 'graphs/all-commits-histogram.png'
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    return filepath


# ============ CORRELATION ANALYSIS ============

def calculate_user_correlation() -> pd.DataFrame:
    """
    Calculate correlation between user statistics.
    
    Returns:
        DataFrame with correlation matrix
    """
    users = load_users()
    
    if not users:
        print("No users found.")
        return pd.DataFrame()
    
    # Create DataFrame
    data = {
        'followers': [u.num_followers for u in users],
        'following': [u.num_following for u in users],
        'pull_requests': [u.num_pull_requests for u in users],
        'contributions': [u.num_contributions for u in users],
        'repos': [u.num_repos for u in users]
    }
    
    df = pd.DataFrame(data)
    correlation = df.corr()
    
    # Create heatmap
    ensure_output_dir()
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0,
                square=True, linewidths=0.5, fmt='.2f', ax=ax)
    
    ax.set_title('User Statistics Correlation Matrix', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graphs/user-correlation-heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    return correlation


def calculate_pr_correlation(owner: str, repo_name: str) -> pd.DataFrame:
    """
    Calculate correlation between pull request numeric data.
    
    Args:
        owner: Repository owner username
        repo_name: Repository name
        
    Returns:
        DataFrame with correlation matrix
    """
    prs = load_pull_requests(owner, repo_name)
    
    if not prs:
        print("No pull requests found.")
        return pd.DataFrame()
    
    # Create DataFrame
    data = {
        'commits': [pr.commits for pr in prs],
        'additions': [pr.additions for pr in prs],
        'deletions': [pr.deletions for pr in prs],
        'changed_files': [pr.changed_files for pr in prs]
    }
    
    df = pd.DataFrame(data)
    correlation = df.corr()
    
    # Create heatmap
    ensure_output_dir()
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(correlation, annot=True, cmap='RdYlBu_r', center=0,
                square=True, linewidths=0.5, fmt='.2f', ax=ax)
    
    ax.set_title(f'PR Numeric Data Correlation\n{owner}/{repo_name}', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'graphs/{owner}-{repo_name}-pr-correlation.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    return correlation


def create_all_repo_graphics(owner: str, repo_name: str) -> List[str]:
    """
    Create all graphics for a specific repository.
    
    Args:
        owner: Repository owner username
        repo_name: Repository name
        
    Returns:
        List of paths to saved figures
    """
    paths = []
    
    print(f"Creating boxplot for commits...")
    p = create_repo_boxplot_commits(owner, repo_name)
    if p:
        paths.append(p)
    
    print(f"Creating boxplot for additions/deletions...")
    p = create_repo_boxplot_additions_deletions(owner, repo_name)
    if p:
        paths.append(p)
    
    print(f"Creating boxplot for changed files by author...")
    p = create_repo_boxplot_changed_files_by_author(owner, repo_name)
    if p:
        paths.append(p)
    
    print(f"Creating scatter plot for additions vs deletions...")
    p = create_repo_scatter_additions_deletions(owner, repo_name)
    if p:
        paths.append(p)
    
    print(f"Creating histogram for commits...")
    p = create_repo_histogram_commits(owner, repo_name)
    if p:
        paths.append(p)
    
    return paths


def create_all_cross_repo_graphics() -> List[str]:
    """
    Create all graphics considering data from all repositories.
    
    Returns:
        List of paths to saved figures
    """
    paths = []
    
    print("Creating line graph for PRs per day...")
    p = create_all_prs_line_per_day()
    if p:
        paths.append(p)
    
    print("Creating line graph for open/closed PRs per day...")
    p = create_all_prs_line_open_closed_per_day()
    if p:
        paths.append(p)
    
    print("Creating bar chart for users per repo...")
    p = create_all_users_per_repo_bar()
    if p:
        paths.append(p)
    
    print("Creating histogram for commits...")
    p = create_all_commits_histogram()
    if p:
        paths.append(p)
    
    return paths

