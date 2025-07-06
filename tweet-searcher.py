import tweepy
import argparse
import sys
import os
from datetime import datetime, timedelta, timezone

# --------------- CONFIG ---------------
DEFAULT_RESULTS = 10
MAX_API_LIMIT = 100  # Twitter API v2 max_results limit per request
DEFAULT_TOKEN_FILE = "bearer_token.txt"
# --------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            ">> Search recent tweets for one or more terms and get their links.\n\n"
            ">> Multiple search terms separated by commas.\n"
            ">> Specify how recent in minutes.\n"
            ">> Control number of tweets to fetch per term.\n"
            ">> Optionally save all links to a file in append mode.\n"
            ">> Choose sort order: recent vs top tweets.\n"
            ">> Read your Bearer Token from a file."
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-q", "--query", type=str, required=True,
        help='Comma-separated search terms. Example: "openai, elon, chatgpt"'
    )
    parser.add_argument(
        "-m", "--minutes", type=int, required=True,
        help="How recent in minutes (e.g. 30)."
    )
    parser.add_argument(
        "-n", "--num", type=int, default=DEFAULT_RESULTS,
        help=f"Number of tweets per query (default {DEFAULT_RESULTS}, max {MAX_API_LIMIT})."
    )
    parser.add_argument(
        "-o", "--output", type=str,
        help="Optional: Output file to append all tweet links."
    )
    parser.add_argument(
        "--sort", choices=['recent', 'top'], default='recent',
        help="Sort order: 'recent' (default) or 'top' (engaged tweets)."
    )
    parser.add_argument(
        "--tokenfile", type=str, default=DEFAULT_TOKEN_FILE,
        help=f"Path to text file containing your Twitter Bearer Token (default '{DEFAULT_TOKEN_FILE}')."
    )

    # Show help if no arguments
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()

def load_bearer_token(token_path):
    if not os.path.exists(token_path):
        print(f" Bearer token file not found: {token_path}")
        sys.exit(1)

    with open(token_path, "r", encoding="utf-8") as f:
        token = f.read().strip()

    if not token:
        print(f" Bearer token file is empty: {token_path}")
        sys.exit(1)

    return token

def search_tweets(client, query, start_time_iso, max_results, sort_order):
    if max_results > MAX_API_LIMIT:
        print(f" Limiting max_results to {MAX_API_LIMIT} (Twitter API limit).")
        max_results = MAX_API_LIMIT

    try:
        tweets = client.search_recent_tweets(
            query=query,
            start_time=start_time_iso,
            expansions=['author_id'],
            tweet_fields=['author_id', 'created_at'],
            user_fields=['username'],
            max_results=max_results,
            sort_order="recency" if sort_order == "recent" else "relevancy"
        )
    except tweepy.TooManyRequests as e:
        print(" ERROR: Rate limit exceeded (HTTP 429). Twitter says Too Many Requests.")
        print(" Wait 15 minutes before trying again, or reduce number of terms/results.")
        sys.exit(1)

    if not tweets or not tweets.data:
        return []

    # Map user ID to username
    user_map = {}
    if tweets.includes and 'users' in tweets.includes:
        user_map = {user.id: user.username for user in tweets.includes['users']}

    links = []
    for tweet in tweets.data:
        username = user_map.get(tweet.author_id, "unknown")
        tweet_id = tweet.id
        link = f"https://twitter.com/{username}/status/{tweet_id}"
        links.append(link)

    return links

def save_to_file(query, links, output_path):
    try:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"\n #########  QUERY: {query}   ######### \n" )
            for link in links:
                f.write(link + "\n")
        print(f"\n Appended {len(links)} links to for {query} to : {output_path}")
    except Exception as e:
        print(f" Error saving to file: {e}")

def main():
    args = parse_args()

    if args.num < 1:
        print(" Number of results must be at least 1.")
        return

    # Split comma-separated search terms
    query_terms = [q.strip() for q in args.query.split(',') if q.strip()]
    if not query_terms:
        print(" No valid search terms found after splitting by commas.")
        return

    # Load Bearer Token
    bearer_token = load_bearer_token(args.tokenfile)
    client = tweepy.Client(bearer_token=bearer_token)

    # Calculate start_time in ISO 8601 format
    now = datetime.now(timezone.utc)
    delta = timedelta(minutes=args.minutes)
    start_time = now - delta
    start_time_iso = start_time.isoformat()

    all_links = set()

    for query in query_terms:
        print(f"\n Searching for tweets with query: \"{query}\" in the last {args.minutes} minutes...")
        print(f" Max results to fetch for this term: {args.num}")
        print(f" Sort order: {'Recency' if args.sort == 'recent' else 'Top (Relevancy)'}\n")

        results = search_tweets(client, query, start_time_iso, args.num, args.sort)

        if not results:
            print(f" No tweets found for \"{query}\" in the specified time range.")
            continue

        print(f" Found {len(results)} tweet links for \"{query}\":\n")
        for link in results:
            print(link)
            all_links.add(link)

    if args.output and all_links:
        save_to_file(query, sorted(all_links),  args.output)
    elif args.output and not all_links:
        print("\n No links to save.")

if __name__ == "__main__":
    main()
