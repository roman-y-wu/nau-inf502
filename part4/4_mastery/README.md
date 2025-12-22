# GitHub Repository Analyzer

A comprehensive Python application for collecting and analyzing data from GitHub repositories, pull requests, and users.

## Features

### Data Collection
- **Repository Information**: Name, owner, description, homepage, license, forks, watchers, stars
- **Pull Requests**: Title, number, body, state, dates, commits, additions, deletions, changed files
- **User Profiles**: Login, PR count, repositories, followers, following, contributions (scraped from GitHub)

### Analysis & Visualization
- **Repository-specific graphics**:
  - Boxplot: Commits comparison (open vs closed PRs)
  - Boxplot: Additions and deletions comparison
  - Boxplot: Changed files by author association
  - Scatter plot: Additions vs deletions
  - Histogram: Commits per pull request

- **Cross-repository graphics**:
  - Line graph: Total PRs per day
  - Line graph: Open vs closed PRs per day
  - Bar chart: Users per repository
  - Histogram: Commits per PR (all repos)

- **Correlation Analysis**:
  - User statistics correlation (followers, following, PRs, contributions)
  - Pull request numeric data correlation

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Set up GitHub token for higher API rate limits:

```bash
export GITHUB_TOKEN=your_github_personal_access_token
```

## Usage

Run the main application:

```bash
python main.py
```

### Menu Options

1. **Collect data for a repository** - Fetch all data (repo info, PRs, users) from GitHub
2. **List all collected repositories** - View all repositories in the local database
3. **List pull requests from a repository** - View PRs for a specific repo
4. **Show repository summary** - Display statistics (open/closed PRs, users, oldest PR)
5. **Create graphics for a repository** - Generate all visualizations for one repo
6. **Create graphics for all repositories** - Generate cross-repository visualizations
7. **Calculate user correlation** - Analyze correlations in user statistics
8. **Calculate PR correlation for a repository** - Analyze correlations in PR data
9. **Exit**

## Project Structure

```
├── main.py              # Main application with user interface
├── models.py            # Data models (Repository, PullRequest, User, License)
├── github_api.py        # GitHub REST API v3 interaction
├── scraper.py           # Web scraping for user profiles
├── data_manager.py      # CSV file operations
├── visualizations.py    # Chart and graph generation
├── tests.py             # Unit tests
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── projects.csv         # Collected repository data (generated)
├── users.csv            # Collected user data (generated)
├── projects/            # Pull request CSV files per repository (generated)
│   └── owner-repo.csv
└── graphs/              # Generated visualization images (generated)
    └── *.png
```

## Data Storage

### CSV Files
- `projects.csv` - Repository information
- `users.csv` - User profile data
- `projects/owner-repo.csv` - Pull requests per repository

### Object Model

Each class has:
- `to_csv_string()` - Returns CSV-formatted row data
- `get_csv_header()` - Returns CSV header row
- `from_json()` - Creates object from API response
- `from_csv_row()` - Creates object from CSV dictionary

## API Rate Limits

Without authentication: 60 requests/hour
With token: 5,000 requests/hour

Set your GitHub personal access token:
```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

## Running Tests

Execute the unit tests:

```bash
python -m unittest tests -v
```

Or simply:

```bash
python tests.py
```

## Example Workflow

```bash
# 1. Start the application
python main.py

# 2. Select option 1 to collect data
# Enter: owner = "microsoft", repo = "vscode"

# 3. After collection, create visualizations
# Select option 5 for repository graphics
# Select option 6 for cross-repository graphics

# 4. View correlations
# Select option 7 for user correlations
# Select option 8 for PR correlations
```

## Dependencies

- **requests** - HTTP library for API calls
- **beautifulsoup4** - HTML parsing for web scraping
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **matplotlib** - Data visualization
- **seaborn** - Statistical data visualization

## License

This project is for educational purposes (NAU INF502).

