Tweet Searcher

A command-line Python toolkit to search Twitter for tweets matching your keywords, with two modes:

1)  API-based Search (using Twitter’s official API)  
2)  Non-API Search (web scraping via mobile.twitter.com with proxy rotation)

---

## ✅ Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Setup](#-setup)
- [Usage](#-usage)
  - [1️ API-based Scraper]
  - [2️ Non-API Scraper]
- [Example Outputs](#-example-outputs)
- [Notes & Limitations](#-notes--limitations)
- [License](#-license)
- [Author](#-author)

---

## ✅ Features

✅ Multiple comma-separated search terms  
✅ "How recent" filter in minutes  
✅ Limit number of tweets per term  
✅ Choose sort order (recent/top)  
✅ Output to text file (appends results)  
✅ Random User-Agent rotation (Non-API)  
✅ HTTP, HTTPS, SOCKS5 proxy support (Non-API)  
✅ Reads Bearer Token securely from a file (API)  

---

## ✅ Requirements

- Python 3.7+
- Twitter Developer account & Bearer Token (for API mode)

---

## ✅ Setup

Clone the repo:


git clone https://github.com/1024/tweet-searcher.git
cd tweet-searcher


Install dependencies:


pip install -r requirements.txt

---

## ✅ Usage

The repo contains **two separate CLI scripts**:

---

1)   API-based Scraper

Search Twitter using the official Twitter API (v2).

### ✅ Example command:


python tweetsearch_api.py \
  -q "elon, chatgpt, crypto" \
  -m 30 \
  -n 10 \
  --sort recent \
  -o results.txt \
  --tokenfile bearer_token.txt


### ✅ Arguments

| Argument         | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| `-q / --query`   | **Required**. Comma-separated search terms                   |
| `-m / --minutes` | How recent in minutes to filter tweets                       |
| `-n / --num`     | Max number of tweets per search term                         |
| `--sort`         | Sort order preference (`recent` or `top`)                    |
| `-o / --output`  | **Required**. Output file to append tweet links              |
| `--tokenfile`    | **Required**. Path to text file containing your Bearer Token |

---

### ✅ Example bearer\_token.txt

```
YOUR_LONG_BEARER_TOKEN_HERE
```


2)    Non-API Scraper

Scrapes Twitter search results from mobile.twitter.com without using the API.

✅ Ideal for:

* Bypassing API quotas
* Searching without Twitter Developer access

### ✅ Example command:

```bash
python tweetscraper.py \
  -q "elon, chatgpt, crypto" \
  -m 30 \
  -n 10 \
  --sort recent \
  -o results.txt \
  --proxyfile proxies.txt
```

### ✅ Arguments

| Argument         | Description                                           |
| ---------------- | ----------------------------------------------------- |
| `-q / --query`   | **Required**. Comma-separated search terms            |
| `-m / --minutes` | How recent in minutes (informational/logging only)    |
| `-n / --num`     | Max number of tweet links per search term             |
| `--sort`         | Sort order preference (`recent` or `top`)             |
| `-o / --output`  | **Required**. Output file to append results           |
| `--proxyfile`    | **Required**. Path to text file containing proxy list |

---
---

## ✅ Example Outputs

Your results file will look like:

```
=== QUERY: elon ===
https://twitter.com/user/status/1234567890
https://twitter.com/user/status/0987654321

=== QUERY: chatgpt ===
https://twitter.com/user/status/1122334455
https://twitter.com/user/status/5544332211
```

✅ Appends to existing file in this format.

---

## ✅ Notes & Limitations

⚠️ The **API version** respects Twitter’s official rate limits (e.g. 450 requests/15 min).
⚠️ The **Non-API version** scrapes public search pages; Twitter may block IPs for excessive scraping.
⚠️ Free proxies are unreliable. For serious scraping, use paid/residential rotating proxies.
⚠️ SOCKS5 support needs:


⚠️ The "how recent" filter is best-effort/logging only on the Non-API scraper.

---

## ✅ License

MIT License.
Use responsibly and respect Twitter’s Terms of Service.

---

## ✅ Author

**1024-Cyber**
Feel free to fork, star, or contribute!





