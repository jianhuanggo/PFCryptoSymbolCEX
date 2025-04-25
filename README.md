# PFCryptoSymbolCEX

A Python script to extract cryptocurrency symbols and descriptions from CoinMarketCap.

## Features

- Extracts cryptocurrency symbols and descriptions from CoinMarketCap
- Handles pagination to get comprehensive data
- Outputs data in a standardized JSON format
- Uses API when available, falls back to web scraping when needed

## Requirements

- Python 3.6+
- Required packages:
  - requests
  - beautifulsoup4

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the script to extract cryptocurrency data:

```bash
python crypto_symbols.py
```

The script will:
1. Fetch cryptocurrency data from CoinMarketCap
2. Extract symbols and descriptions
3. Print sample entries to the console
4. Save all data to `cex_crypto_descriptions.json`

## Output Format

The output is a list of dictionaries with the following structure:

```json
{
  "symbol": "ETH",
  "source_of_information": "coinmarketcap.com",
  "description": "Ethereum is a decentralized open-source blockchain system..."
}
```
