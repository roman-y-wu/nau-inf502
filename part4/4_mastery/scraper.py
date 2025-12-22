"""
Web scraper module for GitHub user profile pages.
Uses BeautifulSoup to scrape user statistics from their profile page.
"""

import requests
import re
from typing import Optional
from bs4 import BeautifulSoup

from models import User


class GitHubScraper:
    """Class to scrape GitHub user profile pages."""
    
    BASE_URL = "https://github.com"
    
    def __init__(self):
        """Initialize the scraper with a requests session."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36')
        })
    
    def scrape_user_profile(self, username: str) -> dict:
        """
        Scrape user profile page for statistics.
        
        Args:
            username: GitHub username
            
        Returns:
            Dictionary with scraped data (repos, followers, following, contributions)
        """
        url = f"{self.BASE_URL}/{username}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch profile for {username}: {e}")
            return {
                'num_repos': 0,
                'num_followers': 0,
                'num_following': 0,
                'num_contributions': 0
            }
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract statistics
        num_repos = self._extract_repos(soup)
        num_followers = self._extract_followers(soup)
        num_following = self._extract_following(soup)
        num_contributions = self._extract_contributions(soup)
        
        return {
            'num_repos': num_repos,
            'num_followers': num_followers,
            'num_following': num_following,
            'num_contributions': num_contributions
        }
    
    def _parse_number(self, text: str) -> int:
        """
        Parse a number from text, handling 'k' suffix for thousands.
        
        Args:
            text: Text containing a number (e.g., "1.2k", "100")
            
        Returns:
            Integer value
        """
        if not text:
            return 0
        
        text = text.strip().lower()
        
        # Handle 'k' suffix for thousands
        if 'k' in text:
            try:
                num = float(text.replace('k', ''))
                return int(num * 1000)
            except ValueError:
                return 0
        
        # Handle 'm' suffix for millions
        if 'm' in text:
            try:
                num = float(text.replace('m', ''))
                return int(num * 1000000)
            except ValueError:
                return 0
        
        # Try to extract just the number
        try:
            # Remove any non-numeric characters except dots
            cleaned = re.sub(r'[^\d.]', '', text)
            if cleaned:
                return int(float(cleaned))
        except ValueError:
            pass
        
        return 0
    
    def _extract_repos(self, soup: BeautifulSoup) -> int:
        """Extract the number of repositories from the profile page."""
        # Try to find the repositories count in the navigation
        nav_items = soup.find_all('a', {'data-tab-item': 'repositories'})
        for item in nav_items:
            counter = item.find('span', class_='Counter')
            if counter:
                return self._parse_number(counter.get_text())
        
        # Alternative: look for the tab with repositories
        repo_tab = soup.find('a', href=re.compile(r'\?tab=repositories'))
        if repo_tab:
            counter = repo_tab.find('span', class_='Counter')
            if counter:
                return self._parse_number(counter.get_text())
        
        # Try finding in the profile sidebar
        nav_links = soup.select('nav a[href*="repositories"]')
        for link in nav_links:
            counter = link.find('span', class_='Counter')
            if counter:
                return self._parse_number(counter.get_text())
        
        return 0
    
    def _extract_followers(self, soup: BeautifulSoup) -> int:
        """Extract the number of followers from the profile page."""
        # Look for followers link
        followers_link = soup.find('a', href=re.compile(r'\?tab=followers'))
        if followers_link:
            # Get the text content and extract number
            text = followers_link.get_text()
            # Find number pattern
            match = re.search(r'([\d.]+[km]?)', text.lower())
            if match:
                return self._parse_number(match.group(1))
            
            # Look for span with number
            span = followers_link.find('span', class_='text-bold')
            if span:
                return self._parse_number(span.get_text())
        
        # Alternative: look in the profile card
        profile_details = soup.find_all('a', class_='Link--secondary')
        for link in profile_details:
            if 'follower' in link.get('href', ''):
                text = link.get_text()
                match = re.search(r'([\d.]+[km]?)', text.lower())
                if match:
                    return self._parse_number(match.group(1))
        
        return 0
    
    def _extract_following(self, soup: BeautifulSoup) -> int:
        """Extract the number of users being followed from the profile page."""
        # Look for following link
        following_link = soup.find('a', href=re.compile(r'\?tab=following'))
        if following_link:
            text = following_link.get_text()
            match = re.search(r'([\d.]+[km]?)', text.lower())
            if match:
                return self._parse_number(match.group(1))
            
            span = following_link.find('span', class_='text-bold')
            if span:
                return self._parse_number(span.get_text())
        
        # Alternative: look in the profile card
        profile_details = soup.find_all('a', class_='Link--secondary')
        for link in profile_details:
            if 'following' in link.get('href', ''):
                text = link.get_text()
                match = re.search(r'([\d.]+[km]?)', text.lower())
                if match:
                    return self._parse_number(match.group(1))
        
        return 0
    
    def _extract_contributions(self, soup: BeautifulSoup) -> int:
        """Extract the number of contributions in the last year."""
        # Look for contribution count in the profile
        contrib_heading = soup.find('h2', class_='f4')
        if contrib_heading:
            text = contrib_heading.get_text()
            if 'contribution' in text.lower():
                match = re.search(r'([\d,]+)', text)
                if match:
                    return int(match.group(1).replace(',', ''))
        
        # Alternative: look for the contribution graph heading
        contrib_elements = soup.find_all(string=re.compile(r'\d+\s*contributions?'))
        for element in contrib_elements:
            match = re.search(r'([\d,]+)\s*contributions?', element, re.IGNORECASE)
            if match:
                return int(match.group(1).replace(',', ''))
        
        # Try finding in activity overview
        activity = soup.find('div', class_='js-yearly-contributions')
        if activity:
            heading = activity.find('h2')
            if heading:
                text = heading.get_text()
                match = re.search(r'([\d,]+)', text)
                if match:
                    return int(match.group(1).replace(',', ''))
        
        return 0


def scrape_users(users: list) -> list:
    """
    Scrape profile data for a list of users.
    
    Args:
        users: List of User objects
        
    Returns:
        Updated list of User objects with scraped data
    """
    scraper = GitHubScraper()
    
    for user in users:
        print(f"Scraping profile for {user.login}...")
        profile_data = scraper.scrape_user_profile(user.login)
        
        user.num_repos = profile_data['num_repos']
        user.num_followers = profile_data['num_followers']
        user.num_following = profile_data['num_following']
        user.num_contributions = profile_data['num_contributions']
    
    return users


