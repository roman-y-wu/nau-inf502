"""
GitHub Repository Analyzer - Main Application
A complete application for collecting and analyzing GitHub repository data.
"""

import os
import sys

from github_api import collect_repository_data
from scraper import scrape_users
from data_manager import (
    save_repository, save_pull_requests, save_users,
    load_repositories, load_pull_requests, get_repository_summary
)
from visualizations import (
    create_all_repo_graphics, create_all_cross_repo_graphics,
    calculate_user_correlation, calculate_pr_correlation
)


def print_menu():
    """Display the main menu."""
    print("\n" + "=" * 60)
    print("       GitHub Repository Analyzer")
    print("=" * 60)
    print("\n1. Collect data for a repository")
    print("2. List all collected repositories")
    print("3. List pull requests from a repository")
    print("4. Show repository summary")
    print("5. Create graphics for a repository")
    print("6. Create graphics for all repositories")
    print("7. Calculate user correlation")
    print("8. Calculate PR correlation for a repository")
    print("9. Exit")
    print("\n" + "-" * 60)


def get_repo_selection(repos):
    """
    Helper function to let user select a repository.
    
    Args:
        repos: List of Repository objects
        
    Returns:
        Tuple of (owner, repo_name) or (None, None) if cancelled
    """
    if not repos:
        print("No repositories collected yet.")
        return None, None
    
    print("\nAvailable repositories:")
    for i, repo in enumerate(repos, 1):
        print(f"  {i}. {repo.owner}/{repo.name}")
    
    try:
        choice = input("\nSelect repository number (or 'q' to cancel): ").strip()
        if choice.lower() == 'q':
            return None, None
        
        idx = int(choice) - 1
        if 0 <= idx < len(repos):
            return repos[idx].owner, repos[idx].name
        else:
            print("Invalid selection.")
            return None, None
    except ValueError:
        print("Invalid input.")
        return None, None


def collect_repository():
    """Collect data for a specific repository."""
    print("\n--- Collect Repository Data ---")
    
    owner = input("Enter repository owner: ").strip()
    if not owner:
        print("Owner cannot be empty.")
        return
    
    repo_name = input("Enter repository name: ").strip()
    if not repo_name:
        print("Repository name cannot be empty.")
        return
    
    # Optional: GitHub token for higher rate limits
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("\nNote: Set GITHUB_TOKEN environment variable for higher API rate limits.")
    
    print(f"\nCollecting data for {owner}/{repo_name}...")
    
    try:
        repo, pull_requests, users = collect_repository_data(owner, repo_name, token)
        
        if repo is None:
            return
        
        # Save repository data
        print("\nSaving repository data...")
        save_repository(repo)
        
        # Save pull requests
        if pull_requests:
            print(f"Saving {len(pull_requests)} pull requests...")
            save_pull_requests(owner, repo_name, pull_requests)
        
        # Scrape and save user data
        if users:
            print(f"\nScraping profile data for {len(users)} users...")
            users = scrape_users(users)
            
            print("Saving user data...")
            save_users(users)
        
        print(f"\n✓ Successfully collected data for {owner}/{repo_name}")
        print(f"  - Repository info saved to: projects.csv")
        print(f"  - Pull requests saved to: projects/{owner}-{repo_name}.csv")
        print(f"  - User data saved to: users.csv")
        
    except Exception as e:
        print(f"\nError collecting data: {e}")
        import traceback
        traceback.print_exc()


def list_repositories():
    """List all collected repositories."""
    print("\n--- Collected Repositories ---")
    
    repos = load_repositories()
    
    if not repos:
        print("No repositories have been collected yet.")
        return
    
    print(f"\nFound {len(repos)} repository/repositories:\n")
    
    for i, repo in enumerate(repos, 1):
        print(f"  {i}. {repo}")
        print(f"     License: {repo.license}")
        print(f"     Forks: {repo.forks} | Watchers: {repo.watchers}")
        print(f"     Collected: {repo.date_of_collection}")
        print()


def list_pull_requests():
    """List pull requests from a selected repository."""
    print("\n--- List Pull Requests ---")
    
    repos = load_repositories()
    owner, repo_name = get_repo_selection(repos)
    
    if owner is None:
        return
    
    prs = load_pull_requests(owner, repo_name)
    
    if not prs:
        print(f"No pull requests found for {owner}/{repo_name}.")
        return
    
    print(f"\nPull requests for {owner}/{repo_name}:")
    print(f"{'#':<6} {'State':<8} {'User':<20} {'Title':<40}")
    print("-" * 76)
    
    for pr in prs:
        title = pr.title[:37] + "..." if len(pr.title) > 40 else pr.title
        user = pr.user[:17] + "..." if len(pr.user) > 20 else pr.user
        print(f"{pr.number:<6} {pr.state:<8} {user:<20} {title:<40}")
    
    print(f"\nTotal: {len(prs)} pull requests")


def show_summary():
    """Show summary statistics for a repository."""
    print("\n--- Repository Summary ---")
    
    repos = load_repositories()
    owner, repo_name = get_repo_selection(repos)
    
    if owner is None:
        return
    
    summary = get_repository_summary(owner, repo_name)
    
    print(f"\nSummary for {owner}/{repo_name}:")
    print("-" * 40)
    print(f"  Open pull requests:   {summary['open_prs']}")
    print(f"  Closed pull requests: {summary['closed_prs']}")
    print(f"  Total pull requests:  {summary['open_prs'] + summary['closed_prs']}")
    print(f"  Number of users:      {summary['num_users']}")
    print(f"  Oldest PR date:       {summary['oldest_pr_date']}")


def create_repo_graphics():
    """Create graphics for a specific repository."""
    print("\n--- Create Repository Graphics ---")
    
    repos = load_repositories()
    owner, repo_name = get_repo_selection(repos)
    
    if owner is None:
        return
    
    print(f"\nCreating graphics for {owner}/{repo_name}...")
    
    paths = create_all_repo_graphics(owner, repo_name)
    
    if paths:
        print(f"\n✓ Created {len(paths)} graphics:")
        for path in paths:
            print(f"  - {path}")
    else:
        print("No graphics were created. Check if the repository has pull request data.")


def create_cross_repo_graphics():
    """Create graphics considering all repositories."""
    print("\n--- Create Cross-Repository Graphics ---")
    
    repos = load_repositories()
    
    if not repos:
        print("No repositories have been collected yet.")
        return
    
    print(f"\nCreating graphics using data from {len(repos)} repositories...")
    
    paths = create_all_cross_repo_graphics()
    
    if paths:
        print(f"\n✓ Created {len(paths)} graphics:")
        for path in paths:
            print(f"  - {path}")
    else:
        print("No graphics were created. Check if repositories have pull request data.")


def show_user_correlation():
    """Calculate and display user correlation."""
    print("\n--- User Statistics Correlation ---")
    
    print("\nCalculating correlation between user statistics...")
    
    correlation = calculate_user_correlation()
    
    if correlation.empty:
        print("No user data available for correlation analysis.")
        return
    
    print("\nCorrelation Matrix:")
    print("-" * 60)
    print(correlation.to_string())
    print("\n✓ Correlation heatmap saved to: graphs/user-correlation-heatmap.png")


def show_pr_correlation():
    """Calculate and display PR correlation for a repository."""
    print("\n--- Pull Request Correlation ---")
    
    repos = load_repositories()
    owner, repo_name = get_repo_selection(repos)
    
    if owner is None:
        return
    
    print(f"\nCalculating correlation for {owner}/{repo_name}...")
    
    correlation = calculate_pr_correlation(owner, repo_name)
    
    if correlation.empty:
        print("No pull request data available for correlation analysis.")
        return
    
    print("\nCorrelation Matrix:")
    print("-" * 60)
    print(correlation.to_string())
    print(f"\n✓ Correlation heatmap saved to: graphs/{owner}-{repo_name}-pr-correlation.png")


def main():
    """Main application entry point."""
    print("\nWelcome to GitHub Repository Analyzer!")
    print("This tool collects and analyzes data from GitHub repositories.")
    
    while True:
        print_menu()
        
        choice = input("Enter your choice (1-9): ").strip()
        
        if choice == '1':
            collect_repository()
        elif choice == '2':
            list_repositories()
        elif choice == '3':
            list_pull_requests()
        elif choice == '4':
            show_summary()
        elif choice == '5':
            create_repo_graphics()
        elif choice == '6':
            create_cross_repo_graphics()
        elif choice == '7':
            show_user_correlation()
        elif choice == '8':
            show_pr_correlation()
        elif choice == '9':
            print("\nThank you for using GitHub Repository Analyzer!")
            print("Goodbye!\n")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please enter a number between 1 and 9.")


if __name__ == "__main__":
    main()


