# Mercari Research for Yahoo Monitor V0.9

Date: 2026-07-12

## Summary

Mercari can be added as a second monitored marketplace, but the first V0.9 implementation should stay conservative:

- Use public search result pages only.
- Do not use logged-in pages.
- Do not access `/v1/` or `/v2/` API paths.
- Do not bypass CAPTCHA, rate limits, app signatures, device checks, or other access controls.
- Do not automate purchase actions.

This keeps the project aligned with a notification tool rather than an account automation or platform-bypass tool.

## What Is Publicly Observable

The public search page is accessible at URLs like:

```text
https://jp.mercari.com/search?keyword=contax+t3
```

The server-rendered HTML includes:

- Search keyword
- Filter labels
- Item result links
- Item title text
- Price text
- Pagination link

This means a basic monitor can likely parse item IDs, titles, prices, and URLs without logging in.

## Robots.txt Notes

Mercari Japan robots.txt currently includes:

```text
User-agent: *
Disallow: /mypage/
Disallow: /purchase/
Disallow: /sell/
Disallow: /transaction/
Disallow: /language?*
Disallow: /en/mypage/
Disallow: /en/purchase/
Disallow: /en/sell/
Disallow: /en/transaction/
Disallow: /en/language?*
Disallow: /v1/
Disallow: /v2/
```

Practical interpretation for this project:

- Public `/search` pages are not listed as disallowed in robots.txt.
- Account, purchase, sell, transaction, and API-style paths are disallowed.
- V0.9 should avoid `/v1/` and `/v2/` entirely.

## Terms And Conduct Notes

Mercari's terms apply when using the service. Their prohibited conduct guide states that prohibited actions can lead to warning or temporary/permanent usage restrictions. Their terms also allow service access restrictions and account actions when a user violates rules or interferes with service operation.

Practical interpretation for this project:

- Keep requests low frequency.
- Avoid actions that interfere with the service.
- Avoid account automation.
- Avoid scraping private or logged-in areas.
- Avoid automating purchases, comments, follows, likes, or messages.

## Expected Speed

Mercari public search monitoring will probably be slower than a paid monitor that uses non-search data sources.

Likely latency path:

```text
Seller lists item
  -> Mercari internal item data exists
  -> Search index updates
  -> Public search page shows item
  -> Monitor detects item
  -> Telegram sends link
```

So public search monitoring is feasible, but it may not beat paid services that detect items before the public search index updates.

## Recommended V0.9 Scope

### Step 1: Add A Marketplace Source Interface

Create a small common shape for result items:

```text
source
id
title
price
url
keyword
```

Yahoo and Mercari can both return the same item shape.

### Step 2: Add Mercari Public Search Scraper

Create:

```text
mercari.py
```

Initial behavior:

- Build public search URL.
- Parse first page only.
- Extract item ID from item URLs.
- Extract title and price from search result text.
- Return the same candidate structure used by Yahoo.

### Step 3: Add Source-Aware Database Fields

The current database identifies items by `id`. For multi-platform monitoring, item IDs should be scoped by source:

```text
source + id
```

Otherwise, different platforms could theoretically collide.

### Step 4: Add Source-Aware Telegram Messages

Message header should show marketplace:

```text
Mercari New Item
Yahoo Flea Market New Item
```

### Step 5: Add Conservative Rate Controls

Mercari should start slower than Yahoo:

```text
Mercari interval: 10-30 seconds
Yahoo interval: 2 seconds
```

Tune only after observing stability.

## Not Recommended For V0.9

Do not implement these in V0.9:

- App request reverse engineering.
- Private API calls.
- Login session monitoring.
- Cookie reuse.
- CAPTCHA avoidance.
- Proxy rotation.
- Auto-buy or checkout automation.

These add technical, account, legal, and stability risk before the basic public monitor is proven.

## Research Sources

- Mercari public search page: https://jp.mercari.com/search?keyword=contax+t3
- Mercari robots.txt: https://jp.mercari.com/robots.txt
- Mercari Terms of Use: https://static.jp.mercari.com/tos
- Mercari prohibited actions guide: https://help.jp.mercari.com/guide/articles/258/

## Recommendation

Start V0.9 with a public-search-only Mercari monitor. Treat it as a second source for alerts, not as a fastest-possible paid-monitor competitor.

Once the public version is stable, compare detection time against your paid monitor. If it is consistently late, we can decide whether it is worth exploring other compliant data sources such as seller pages, category pages, or notification-style public pages.
