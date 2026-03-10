#!/usr/bin/env python3
"""Scrape available phone numbers from CrazyTel portal."""

import argparse
import json
import re
import time
import requests

CODES = {
    "SA": [
        "Adelaide", "Bordertown", "Halidon", "Karoonda", "Loxton",
        "Mount Gambier", "Murray Bridge", "Port Augusta", "Victor Harbor",
        "Whyalla",
    ],
    "WA": [
        "Albany", "Broome", "Bunbury", "Geraldton", "Kalgoorlie",
        "Karratha", "Mandurah", "Margaret River", "Meekatharra",
        "Mount Barker", "Port Hedland",
    ],
    "NSW": [
        "Albury", "Armidale", "Ballina", "Bankstown", "Bathurst", "Bega",
        "Bowral", "Campbelltown", "Coffs_Harbour", "Cooma", "Coonabarabran",
        "Crookwell", "Dubbo", "Dural", "Engadine", "Forster", "Glen Innes",
        "Gosford", "Goulburn", "Grafton", "Gulgong", "Kempsey", "Kyogle",
        "Lismore", "Liverpool", "Maitland", "Mudgee", "Mullumbimby",
        "Murwillumbah", "Newcastle", "Nowra", "Orange", "Penrith",
        "Port Macquarie", "Scone", "Sutherland", "Swansea", "Sydney",
        "Tamworth", "Taree", "Tweed Heads", "Wagga_Wagga", "Windsor",
        "Wollongong", "Young",
    ],
    "VIC": [
        "Alexandra", "Bacchus Marsh", "Bairnsdale", "Ballarat", "Beechworth",
        "Bendigo", "Castlemaine", "Clayton", "Croydon", "Dandenong", "Echuca",
        "Geelong", "Gisborne", "Heyfield", "Kalkallo", "Kilmore", "Kyabram",
        "Kyneton", "Melbourne", "Mildura", "Mornington", "Morwell",
        "Ringwood", "Romsey", "Rosebud", "Seymour", "Shepparton",
        "Swan Hill", "Sydenham", "Traralgon", "Warragul", "Warrnambool",
        "Yarram",
    ],
    "QLD": [
        "Agnes Waters", "Ballandean", "Beaudesert", "Beenleigh", "Brisbane",
        "Bundaberg", "Caboolture", "Cairns", "Caloundra", "Cannon Valley",
        "Charleville", "Dalby", "Emerald", "Gatton", "Gladstone",
        "Goondiwindi", "Hervey Bay", "Ipswich", "Jimboomba", "Kingaroy",
        "Mackay", "Maryborough", "Moranbah", "Mt Isa", "Nambour",
        "Noosaville", "Ormeau", "Quilpie", "Redcliffe", "Rockhampton",
        "Southport", "Stanthorpe", "Tamborine Mountain", "Toowoomba",
        "Warwick", "Woodford",
    ],
    "NT": [
        "Alice Springs", "Darwin",
    ],
    "TAS": [
        "Devonport", "Hobart", "Launceston", "Oatlands", "Smithton",
        "Ulverstone",
    ],
    "ACT": [
        "Canberra",
    ],
}

URL = "https://portal.crazytel.com.au/get_fixed_dids.php"

HEADERS = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    ),
    "origin": "https://portal.crazytel.com.au",
    "referer": "https://portal.crazytel.com.au/buy_did.php",
}

COOKIES = {
    "PHPSESSID": "d266e28a806a39f097402b6092408f1d",
}

ROW_RE = re.compile(
    r"<tr>\s*"
    r"<td>(\d+)</td>\s*"
    r"<td><center>(\d+)</center></td>\s*"
    r"<td>\$\s*([\d.]+)</td>\s*"
    r"<td>\$\s*([\d.]+)</td>"
)


PAGE_THRESHOLD = 20


def fetch_numbers(state: str, city: str, session: requests.Session) -> list[dict]:
    resp = session.post(URL, data={"state": state, "city": city})
    resp.raise_for_status()

    numbers = []
    for m in ROW_RE.finditer(resp.text):
        numbers.append({
            "number": m.group(1),
            "channels": int(m.group(2)),
            "setup_cost": float(m.group(3)),
            "monthly_cost": float(m.group(4)),
        })
    return numbers


def fetch_all_numbers(
    state: str, city: str, session: requests.Session, delay: float = 0.5
) -> list[dict]:
    """Fetch numbers repeatedly until no new ones appear.

    Some areas return more numbers than a single response contains.
    When a response returns PAGE_THRESHOLD or more results, keep
    querying until a round adds nothing new.
    """
    seen: dict[str, dict] = {}
    numbers = fetch_numbers(state, city, session)
    for n in numbers:
        seen[n["number"]] = n

    if len(numbers) < PAGE_THRESHOLD:
        return list(seen.values())

    rounds = 1
    empty_streak = 0
    while empty_streak < 3:
        time.sleep(delay)
        numbers = fetch_numbers(state, city, session)
        rounds += 1
        new_count = 0
        for n in numbers:
            if n["number"] not in seen:
                seen[n["number"]] = n
                new_count += 1
        if new_count == 0:
            empty_streak += 1
        else:
            empty_streak = 0
            print(f"+{new_count} ", end="", flush=True)

    print(f"({rounds} rounds) ", end="", flush=True)
    return list(seen.values())


def scrape(states: list[str] | None = None, delay: float = 0.5) -> dict:
    if states is None:
        states = list(CODES.keys())

    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)

    results = {}
    for state in states:
        cities = CODES.get(state)
        if not cities:
            print(f"Unknown state: {state}")
            continue

        results[state] = {}
        for city in cities:
            print(f"  {state} / {city} ... ", end="", flush=True)
            numbers = fetch_all_numbers(state, city, session, delay)
            print(f"{len(numbers)} numbers")
            if numbers:
                results[state][city] = numbers
            time.sleep(delay)

    return results


def main():
    parser = argparse.ArgumentParser(description="Scrape CrazyTel available DIDs")
    parser.add_argument(
        "--state", "-s",
        help="Scrape only this state (e.g. NT, NSW, VIC). Can be comma-separated.",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file (default: numbers_<states>.json)",
    )
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=0.5,
        help="Delay between requests in seconds (default: 0.5)",
    )
    args = parser.parse_args()

    states = None
    if args.state:
        states = [s.strip().upper() for s in args.state.split(",")]

    if args.output:
        output_file = args.output
    else:
        tag = "_".join(states).lower() if states else "all"
        output_file = f"numbers_{tag}.json"

    print(f"Scraping: {', '.join(states) if states else 'all states'}")
    results = scrape(states=states, delay=args.delay)

    total = sum(
        len(nums)
        for cities in results.values()
        for nums in cities.values()
    )
    print(f"\nTotal: {total} numbers found")

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()
