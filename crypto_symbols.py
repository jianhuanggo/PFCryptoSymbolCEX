"""
Script to extract cryptocurrency symbols and descriptions from CoinMarketCap.
"""
import json
import time
import requests
from bs4 import BeautifulSoup

def get_coin_list(page=1, limit=100):
    """
    Get a list of cryptocurrencies from CoinMarketCap.
    
    Args:
        page (int): Page number for pagination
        limit (int): Number of results per page
        
    Returns:
        list: List of cryptocurrency data
    """
    url = f"https://coinmarketcap.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        api_url = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start={(page-1)*limit+1}&limit={limit}&sortBy=market_cap&sortType=desc&convert=USD&cryptoType=all&tagType=all&audited=false"
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'cryptoCurrencyList' in data['data']:
                return data['data']['cryptoCurrencyList']
    except Exception as e:
        print(f"API access failed: {e}. Falling back to web scraping.")
    
    try:
        response = requests.get(f"{url}?page={page}", headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            coins = []
            
            table_rows = soup.select('table tbody tr')
            
            for row in table_rows:
                try:
                    symbol_element = row.select_one('td:nth-child(3) .coin-item-symbol')
                    if symbol_element:
                        symbol = symbol_element.text.strip()
                        
                        name_element = row.select_one('td:nth-child(3) a')
                        if name_element and 'href' in name_element.attrs:
                            detail_url = f"https://coinmarketcap.com{name_element['href']}"
                            
                            coins.append({
                                'symbol': symbol,
                                'detail_url': detail_url
                            })
                except Exception as e:
                    print(f"Error parsing row: {e}")
                    continue
            
            return coins
    except Exception as e:
        print(f"Web scraping failed: {e}")
    
    return []

def get_description(coin_data):
    """
    Get the description for a cryptocurrency.
    
    Args:
        coin_data (dict): Cryptocurrency data including detail URL or slug
        
    Returns:
        str: Description of the cryptocurrency
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    if 'description' in coin_data and coin_data['description']:
        return coin_data['description']
    
    if 'slug' in coin_data:
        try:
            api_url = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail?slug={coin_data['slug']}"
            response = requests.get(api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'description' in data['data']:
                    return data['data']['description']
        except Exception as e:
            print(f"API description fetch failed: {e}. Falling back to web scraping.")
    
    if 'detail_url' in coin_data:
        try:
            response = requests.get(coin_data['detail_url'], headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                about_section = soup.select_one('[data-tab-section-id="about"]')
                if about_section:
                    description_element = about_section.select_one('div > div > div > p')
                    if description_element:
                        return description_element.text.strip()
                
                description_elements = soup.select('.content p')
                if description_elements:
                    return description_elements[0].text.strip()
        except Exception as e:
            print(f"Web scraping for description failed: {e}")
    
    return "No description available"

def main():
    """
    Main function to extract cryptocurrency data and save to JSON.
    """
    all_coins = []
    page = 1
    max_pages = 5  # Limit to 5 pages for demonstration
    
    print("Fetching cryptocurrency data from CoinMarketCap...")
    
    while page <= max_pages:
        print(f"Processing page {page}...")
        coins = get_coin_list(page=page)
        
        if not coins:
            print(f"No more coins found on page {page}. Stopping.")
            break
        
        for coin in coins:
            time.sleep(0.5)
            
            description = get_description(coin)
            
            coin_data = {
                "symbol": coin['symbol'],
                "source_of_information": "coinmarketcap.com",
                "description": description
            }
            
            all_coins.append(coin_data)
            print(f"Processed {coin['symbol']}")
        
        page += 1
    
    print("\nSample entries:")
    for i in range(min(3, len(all_coins))):
        print(json.dumps(all_coins[i], indent=2))
    
    with open('cex_crypto_descriptions.json', 'w') as f:
        json.dump(all_coins, f, indent=2)
    
    print(f"\nSaved {len(all_coins)} cryptocurrency entries to cex_crypto_descriptions.json")

if __name__ == "__main__":
    main()
