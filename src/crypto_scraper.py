import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
from typing import List, Dict, Any, Optional

class CoinMarketCapScraper:
    """
    A scraper for CoinMarketCap to extract cryptocurrency symbols and descriptions.
    """
    
    BASE_URL = "https://coinmarketcap.com"
    LISTINGS_URL = f"{BASE_URL}/currencies/"
    SOURCE_INFO = "coinmarketcap.com"
    
    def __init__(self, max_pages: int = 5, delay: float = 1.0):
        """
        Initialize the scraper.
        
        Args:
            max_pages: Maximum number of pages to scrape (for testing, set to None for all pages)
            delay: Delay between requests to avoid rate limiting
        """
        self.max_pages = max_pages
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def get_coin_list(self) -> List[Dict[str, str]]:
        """
        Get the list of all cryptocurrencies with their symbols and URLs.
        
        Returns:
            List of dictionaries containing coin data
        """
        all_coins = []
        page = 1
        
        while True:
            print(f"Scraping page {page}...")
            url = f"{self.LISTINGS_URL}?page={page}"
            
            response = self.session.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch page {page}: {response.status_code}")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            coin_elements = soup.select('table tbody tr')
            
            if not coin_elements:
                print(f"No coins found on page {page}, stopping pagination")
                break
            
            for coin_element in coin_elements:
                try:
                    name_element = coin_element.select_one('td:nth-child(3) div a')
                    if not name_element:
                        continue
                    
                    coin_url = self.BASE_URL + name_element.get('href', '')
                    
                    
                    symbol_element = coin_element.select_one('td:nth-child(3) p')
                    if symbol_element and symbol_element.text.strip():
                        text = symbol_element.text.strip()
                        symbol_match = re.search(r'\b[A-Z0-9]{2,6}\b', text)
                        if symbol_match:
                            symbol = symbol_match.group(0)
                        else:
                            url_parts = coin_url.split('/')
                            if len(url_parts) >= 5:
                                coin_name = url_parts[4]
                                
                                symbol_map = {
                                    'bitcoin': 'BTC',
                                    'ethereum': 'ETH',
                                    'tether': 'USDT',
                                    'bnb': 'BNB',
                                    'solana': 'SOL',
                                    'usd-coin': 'USDC',
                                    'xrp': 'XRP',
                                    'dogecoin': 'DOGE',
                                    'cardano': 'ADA',
                                    'tron': 'TRX',
                                    'avalanche': 'AVAX',
                                    'polkadot': 'DOT'
                                }
                            
                            symbol = symbol_map.get(coin_name, coin_name.upper())
                    
                    all_coins.append({
                        'symbol': symbol,
                        'url': coin_url,
                    })
                    
                except Exception as e:
                    print(f"Error processing a coin: {e}")
                    continue
            
            if self.max_pages and page >= self.max_pages:
                break
                
            pagination = soup.select('ul.pagination li')
            has_next = False
            
            for page_item in pagination:
                if page_item.text.strip() == str(page + 1):
                    has_next = True
                    break
            
            if not has_next:
                print(f"No next page found after page {page}, stopping pagination")
                break
                
            page += 1
            time.sleep(self.delay)  # Be nice to the server
        
        return all_coins
    
    def get_description(self, url: str) -> Optional[str]:
        """
        Get the description of a cryptocurrency from its detail page.
        
        Args:
            url: URL of the cryptocurrency detail page
            
        Returns:
            Description text or None if not found
        """
        try:
            response = self.session.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch {url}: {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            about_tab = soup.find('a', {'href': '#about'}) or soup.find('button', string=re.compile('About'))
            
            if about_tab:
                about_section = soup.find('div', {'id': 'about'})
                if not about_section:
                    about_heading = soup.find('h2', string=re.compile('About'))
                    if about_heading:
                        about_section = about_heading.find_parent('div')
                
                if about_section:
                    paragraphs = about_section.find_all('p')
                    if paragraphs:
                        description = ' '.join([p.text.strip() for p in paragraphs])
                        if len(description) > 500:
                            description = description[:497] + '...'
                        return description
            
            # Alternative approach: look for meta description
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc and 'content' in meta_desc.attrs:
                return meta_desc['content']
            
            # Last resort: try to find any paragraph that might contain a description
            content_divs = soup.select('main div p')
            if content_divs:
                for div in content_divs:
                    text = div.text.strip()
                    if len(text) > 100:  # Assume it's a description if it's long enough
                        if len(text) > 500:
                            text = text[:497] + '...'
                        return text
                
            return None
            
        except Exception as e:
            print(f"Error getting description for {url}: {e}")
            return None
    
    def scrape_all(self) -> List[Dict[str, str]]:
        """
        Scrape all cryptocurrencies and their descriptions.
        
        Returns:
            List of dictionaries with symbol, source_of_information, and description
        """
        result = []
        
        coins = self.get_coin_list()
        print(f"Found {len(coins)} coins")
        
        for i, coin in enumerate(coins):
            print(f"Processing {i+1}/{len(coins)}: {coin['symbol']}")
            
            description = self.get_description(coin['url'])
            if description:
                result.append({
                    'symbol': coin['symbol'],
                    'source_of_information': self.SOURCE_INFO,
                    'description': description
                })
            else:
                result.append({
                    'symbol': coin['symbol'],
                    'source_of_information': self.SOURCE_INFO,
                    'description': f"No description available for {coin['symbol']}"
                })
                
            if i < len(coins) - 1:  # Don't sleep after the last coin
                time.sleep(self.delay)
        
        return result

def main():
    """
    Main function to run the scraper and save results.
    """
    output_file = "cex_crypto_descriptions.json"
    
    scraper = CoinMarketCapScraper(max_pages=5, delay=1.0)
    
    print("Starting to scrape CoinMarketCap...")
    results = scraper.scrape_all()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Scraping completed. Found {len(results)} cryptocurrencies.")
    print(f"Results saved to {output_file}")
    
    print("\nSample entries:")
    for i, entry in enumerate(results[:3]):
        print(f"{i+1}. {entry['symbol']}: {entry['description'][:100]}...")

if __name__ == "__main__":
    main()
