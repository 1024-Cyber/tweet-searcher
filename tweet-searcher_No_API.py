import argparse
import requests
import random
import sys
import time
from bs4 import BeautifulSoup

USER_AGENTS = [
    # Desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    # Mobile
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-A315G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Mobile Safari/537.36",
    # More
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1",
]

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            ">> Twitter search scraper without API.\n\n"
            ">> Searches Twitter for terms via web scraping.\n"
            ">> Supports multiple comma-separated terms.\n"
            ">> Rotates proxies from a list.\n"
            ">> Limits number of tweet links per term.\n"
            ">> Accepts recency and sort order arguments (for logging).\n"
            ">> Appends results to an output file."
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-q", "--query", type=str, required=True,
        help='Comma-separated search terms. Example: "openai, elon, chatgpt"'
    )
    parser.add_argument(
        "-m", "--minutes", type=int, default=60,
        help="How recent in minutes (for logging only)."
    )
    parser.add_argument(
        "-n", "--num", type=int, default=10,
        help="Max number of tweet links to fetch per term (default 10)."
    )
    parser.add_argument(
        "--sort", choices=['recent', 'top'], default='recent',
        help="Sort order preference (for logging only)."
    )
    parser.add_argument(
        "-o", "--output", type=str, required=True,
        help="Output file to append tweet links."
    )
    parser.add_argument(
        "--proxyfile", type=str, required=True,
        help="Text file containing proxy URLs, one per line."
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()

def load_proxies(proxy_path):
    try:
        with open(proxy_path, "r", encoding="utf-8") as f:
            proxies = [line.strip() for line in f if line.strip()]
        if not proxies:
            print(f" Proxy file is empty: {proxy_path}")
            sys.exit(1)
        return proxies
    except Exception as e:
        print(f" Error reading proxy file: {e}")
        sys.exit(1)

def get_random_proxy(proxies):
    return random.choice(proxies)

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def fetch_search_results(query, proxy, user_agent):
    url = f"https://mobile.twitter.com/search?q={requests.utils.quote(query)}&s=typd"

    headers = {
        "User-Agent": user_agent,
        "Accept-Language": "en-US,en;q=0.9",
    }

    proxies_dict = {
        "http": proxy,
        "https": proxy,
    }

    try:
        response = requests.get(url, headers=headers, proxies=proxies_dict, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f" Request failed with proxy {proxy}: {e}")
        return None

def parse_tweet_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/status/" in href and "/i/" not in href:
            full_link = f"https://twitter.com{href.split('?')[0]}"
            links.add(full_link)

    return list(links)

def save_links(query , links, output_path):
    try:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"\n #########  QUERY: {query}   ######### \n" )
            for link in links:
                f.write(link + "\n")
        print(f" Appended {len(links)} links to: {output_path}")
    except Exception as e:
        print(f" Error saving to file: {e}")

def main():
    args = parse_args()

    # Split and clean search terms
    search_terms = [term.strip() for term in args.query.split(",") if term.strip()]
    if not search_terms:
        print(" No valid search terms provided after splitting.")
        sys.exit(1)

    # Load proxies
    proxies = load_proxies(args.proxyfile)

    all_links = set()

    for term in search_terms:
        print(f"\n Searching for: \"{term}\"")
        print(f" How recent: Last {args.minutes} minutes (best-effort via scraping)")
        print(f" Sort order preference: {args.sort}")
        print(f" Max results per term: {args.num}")

        tries = 0
        max_tries = len(proxies) * 2  # Rotate multiple times if necessary

        success = False
        while tries < max_tries and not success:
            proxy = get_random_proxy(proxies)
            user_agent = get_random_user_agent()
            print(f" Using proxy: {proxy} with UA: {user_agent}")

            html = fetch_search_results(term, proxy, user_agent)
            if html:
                links = parse_tweet_links(html)
                if links:
                    limited_links = links[:args.num]
                    print(f" Found {len(limited_links)} links for \"{term}\":")
                    for link in limited_links:
                        print(link)
                        all_links.add(link)
                    success = True
                else:
                    print(f" No tweet links found in HTML for \"{term}\". Trying another proxy...")
            else:
                print(f"  Failed request for \"{term}\" with this proxy. Retrying...")
            tries += 1

            if not success and tries < max_tries:
                time.sleep(random.uniform(2, 5))  # polite delay

        if not success:
            print(f" Could not fetch results for \"{term}\" after {tries} tries.")

    if all_links:
        save_links(query, sorted(all_links),  args.output)
    else:
        print("\n No links collected. Nothing saved.")

if __name__ == "__main__":
    main()
