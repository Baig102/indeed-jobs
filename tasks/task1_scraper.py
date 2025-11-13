import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import quote_plus


class IndeedScraper:
    def __init__(self, position, city, date_posted=""):
        self.position = position
        self.city = city
        self.date_posted = date_posted
        self.base_url = "https://www.indeed.com/jobs"
        self.jobs = []
        
    def build_url(self, start=0):
        """Build the Indeed search URL with parameters."""
        url = f"{self.base_url}?q={quote_plus(self.position)}&l={quote_plus(self.city)}&start={start}"
        if self.date_posted:
            url += f"&fromage={self.date_posted}"
        return url
    
    def scrape_page(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = []
            
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            if not job_cards:
                job_cards = soup.find_all('div', class_='slider_container')
            
            if not job_cards:
                job_cards = soup.find_all('div', class_='cardOutline')
            
            if not job_cards:
                job_cards = soup.find_all('td', class_='resultContent')
            
            if not job_cards:
                job_cards = soup.find_all('div', attrs={'data-jk': True})
            
            if not job_cards:
                job_cards = soup.find_all('a', class_='tapItem')
            
            print(f"Found {len(job_cards)} job cards using soup")
            
            for card in job_cards:
                try:
                    job_data = self.extract_job_data(card, soup)
                    if job_data and job_data['title'] != 'N/A':
                        self.jobs.append(job_data)
                        print(f"Extracted: {job_data['title']} at {job_data['company']}")
                except Exception as e:
                    print(f"Error extracting job: {e}")
                    continue
            
            return len(job_cards) > 0
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return False
        except Exception as e:
            print(f"Scraping error: {e}")
            return False
    
    def extract_job_data(self, card, soup):
        job_data = {
            'title': 'N/A',
            'company': 'N/A',
            'location': 'N/A',
            'salary': 'N/A',
            'job_type': 'N/A',
            'description': 'N/A',
            'posted_date': 'N/A',
            'job_url': 'N/A'
        }
        
        try:
            title_elem = card.find('h2', class_='jobTitle')
            if not title_elem:
                title_elem = card.find('span', attrs={'title': True})
            if not title_elem:
                title_elem = card.find('a', class_='jcs-JobTitle')
            if not title_elem:
                title_elem = card.find('h2')
            
            if title_elem:
                job_data['title'] = title_elem.get_text(strip=True)
                # Get URL from title link
                link = title_elem.find('a') if title_elem.name != 'a' else title_elem
                if link and link.get('href'):
                    href = link.get('href')
                    if href.startswith('http'):
                        job_data['job_url'] = href
                    else:
                        job_data['job_url'] = 'https://www.indeed.com' + href
            
            company_elem = card.find('span', class_='companyName')
            if not company_elem:
                company_elem = card.find('span', {'data-testid': 'company-name'})
            if not company_elem:
                company_elem = card.find('span', class_='css-63koeb')
            if company_elem:
                job_data['company'] = company_elem.get_text(strip=True)
            
            location_elem = card.find('div', class_='companyLocation')
            if not location_elem:
                location_elem = card.find('div', {'data-testid': 'text-location'})
            if not location_elem:
                location_elem = card.find('div', class_='css-1p0sjhy')
            if location_elem:
                job_data['location'] = location_elem.get_text(strip=True)
            
            salary_elem = card.find('div', class_='salary-snippet')
            if not salary_elem:
                salary_elem = card.find('span', class_='salary')
            if not salary_elem:
                salary_elem = card.find('div', {'data-testid': 'attribute_snippet_testid'})
            if salary_elem:
                job_data['salary'] = salary_elem.get_text(strip=True)
            
            date_elem = card.find('span', class_='date')
            if not date_elem:
                date_elem = card.find('span', {'data-testid': 'myJobsStateDate'})
            if not date_elem:
                date_elem = card.find('span', class_='css-qvloho')
            if date_elem:
                job_data['posted_date'] = date_elem.get_text(strip=True)
            
            desc_elem = card.find('div', class_='job-snippet')
            if not desc_elem:
                desc_elem = card.find('div', {'class': 'metadata'})
            if not desc_elem:
                desc_elem = card.find('ul')
            if not desc_elem:
                desc_elem = card.find('div', class_='css-9446fg')
            if desc_elem:
                job_data['description'] = desc_elem.get_text(strip=True)[:500]  # Limit length
            
            job_type_elem = card.find('div', class_='metadata')
            if job_type_elem:
                text = job_type_elem.get_text(strip=True)
                if 'full-time' in text.lower():
                    job_data['job_type'] = 'Full-time'
                elif 'part-time' in text.lower():
                    job_data['job_type'] = 'Part-time'
                elif 'contract' in text.lower():
                    job_data['job_type'] = 'Contract'
                elif 'remote' in text.lower():
                    job_data['job_type'] = 'Remote'
            
            return job_data
            
        except Exception as e:
            return None
    
    def scrape_all_pages(self, max_pages=5):
        """Scrape multiple pages of job listings."""
        for page in range(max_pages):
            start = page * 10
            url = self.build_url(start)
            
            has_results = self.scrape_page(url)
            
            if not has_results:
                break
            
            time.sleep(2)
        
        return self.jobs
    
    def save_to_csv(self, filename='indeed_jobs.csv'):
        """Save scraped jobs to CSV file."""
        if not self.jobs:
            print("No jobs to save!")
            return False
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['title', 'company', 'location', 'salary', 'job_type', 'description', 'posted_date', 'job_url']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.jobs)
            print(f"Saved {len(self.jobs)} jobs to {filename}")
            return True
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False


def run_scraper(position, city, date_posted="", max_pages=5):
    """Main function to run scraper programmatically."""
    scraper = IndeedScraper(position, city, date_posted)
    jobs = scraper.scrape_all_pages(max_pages)
    success = scraper.save_to_csv('indeed_jobs.csv')
    return {'success': success, 'count': len(jobs), 'jobs': jobs}
