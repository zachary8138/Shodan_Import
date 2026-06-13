# shodan_import.py

Query [Shodan](https://www.shodan.io/) for internet-exposed hosts matching a search filter and print IP, port, service, and banner details to the terminal. Useful for seeding target lists before running local scanners (for example, the [docker-exposure-scanner](../Cloud/docker-scanner/README.md) in this repo).

**Authorized use only.** Shodan data describes real systems on the internet. Only investigate hosts you are permitted to assess, and comply with Shodan's [terms of service](https://account.shodan.io/legal) and your organization's policies.

## What it does

1. Connects to the Shodan API using your API key.
2. Runs a search query (default in the script: `org:"LC"`).
3. Prints the **first page** of results (up to 100 matches per Shodan API page).
4. For each match, shows IP, port, detected service module, last-seen timestamp, and a truncated banner snippet.

Optional **pagination** code is included in the script (commented out) to walk through all pages when a query returns many hosts.

## Requirements

- **Python 3.8+** (3.10+ recommended)
- **Shodan account** with an API key ([account.shodan.io](https://account.shodan.io/))
- **`shodan` Python package**

Install the library:

```bash
python3 -m pip install shodan
```

Or in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install shodan
```

## Before you run

### 1. Set your API key

Open `shodan_import.py` and replace the placeholder:

```python
API_KEY = 'ENTER_API_KEY'
```

**Recommended:** avoid committing real keys. Prefer an environment variable and read it in the script:

```python
import os
API_KEY = os.environ.get("SHODAN_API_KEY", "")
if not API_KEY:
    raise SystemExit("Set SHODAN_API_KEY")
```

Export the key in your shell before running:

```bash
export SHODAN_API_KEY="your_key_here"
```

### 2. Customize the search query

Edit the `api.search(...)` call. Shodan uses a filter syntax. Examples:

| Goal | Example query |
|------|----------------|
| Organization name | `org:"Acme Corp"` |
| Open Docker API (port 2375) | `port:2375 product:Docker` |
| Docker registry (5000) | `port:5000 product:Docker` |
| Country + port | `country:US port:2375` |
| ASN | `asn:AS15169` |
| Hostname | `hostname:example.com` |
| Time window | `org:"Acme" after:01/01/2026 before:06/01/2026` |

The script includes a commented example for date filtering:

```python
# results = api.search('org:"LC" before:07/06/2026 after:01/06/2026')
```

Use [Shodan's search filters](https://www.shodan.io/search/filters) to refine queries before running against large orgs.

## Usage

From the directory containing the script:

```bash
python3 shodan_import.py
```

Example output:

```text
Found 42 results for LC

IP: 203.0.113.10
Port: 2375
Service: docker
Last Update: 2026-05-15T12:34:56.789012
Banner: HTTP/1.1 200 OK...
--------------------------------------------------
```

### Pagination (all results)

By default, only the **first page** is fetched. For large result sets, uncomment the pagination block at the bottom of `shodan_import.py` (lines marked `PAGINATION:`). That loop increments `page` until Shodan returns no more matches.

**Note:** Shodan bills **one query credit per page** (and other rules apply for streaming/export). Check your plan limits before paginating broad searches.

## Feeding results into docker-exposure-scanner

To turn Shodan IPs into targets for the local Docker scanner, extract IPs and pass them to `docker-exposure-scan`:

```bash
# Example: save IPs from a one-off Shodan CLI export, or parse script output
python3 shodan_import.py 2>/dev/null | awk '/^IP: / { print $2 }' | sort -u > targets.txt

# Scan with inspect mode (requires pip install -e ".[inspect]" in docker-scanner)
xargs -a targets.txt docker-exposure-scan --targets --inspect --fail-on high
```

For production workflows, consider Shodan's official [CLI](https://cli.shodan.io/) (`shodan download`, `shodan parse`) or JSON export instead of parsing stdout.

## Errors and troubleshooting

| Symptom | Likely cause | What to do |
|---------|----------------|------------|
| `Error: Invalid API key` | Wrong or missing key | Verify key at [account.shodan.io](https://account.shodan.io/) |
| `Error: No query credits left` | Plan exhausted | Upgrade plan or wait for reset |
| `ModuleNotFoundError: shodan` | Package not installed | `pip install shodan` |
| `Found 0 results` | Query too narrow or no matches | Test the same query on shodan.io/search |
| Rate / access errors | API limits or account tier | Reduce pagination; narrow the query |

The script catches `shodan.APIError` and prints the message; it does not retry automatically.

## API credits (brief)

- Each **search page** consumes query credits (see your Shodan membership).
- Free accounts have limited credits; paid plans allow more searches and exports.
- Prefer **narrow filters** (`port:2375 org:"..."`) over broad org-only searches when exploring.

## Security notes

- Do **not** commit API keys to git. Use env vars or a local untracked config file.
- Banner output may contain sensitive information; treat logs accordingly.
- Shodan shows historical data; a host may have been patched since the last scan timestamp.

##### License
GPLv3
