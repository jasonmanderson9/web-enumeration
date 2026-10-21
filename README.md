# Web Enumeration Tool

A small Python tool for discovering hidden directories and subdomains on a target web server. I built this as a learning project to show how enumeration tools like Gobuster, dirb, and ffuf work under the hood.

I'm writing a full walkthrough of how I built this and how the underlying techniques work. You can find it here: [[write-up link coming soon](https://derzy.io/projects/building-your-own-web-enumeration-tool/)]

## What it does

The tool has two modes:

- **Directory enumeration** — takes a base URL and a wordlist, then requests every possible path (`example.com/admin`, `example.com/backup`, ...) and reports which ones exist.
- **Subdomain enumeration** — takes a domain and a wordlist, then tries every possible subdomain (`dev.example.com`, `staging.example.com`, ...) and reports which ones resolve to a live web server.

## How it works

Enumeration tools are conceptually simple: web servers almost always host more than what is linked on their public pages. Admin panels, backup files, test environments, and forgotten endpoints often sit at predictable paths. Since there's no way to query a server for a list of its directories, the only option is to guess or brute-force by taking a list of common names and ask the server about each one.

For every word in the wordlist, the script sends an HTTP request and looks at the response status code:

- **200 OK** — reported as a potential lead.
- **403 Forbidden** — reported separately; the resource may exist but deny access.
- **404 Not Found** — skipped to reduce output.
- **301 Moved Permanently** and **302 Found** — skipped; the scan continues with the next wordlist entry.
- **Other status codes**, including other redirects — reported as responses, but not followed.

Both modes send a Chrome-style `User-Agent` header. Requests use a five-second timeout, do not follow redirects, and disable TLS certificate verification; the corresponding urllib3 warning is suppressed. Disabling certificate verification means the server's identity is not validated, so use this only where appropriate.

Subdomain enumeration works the same way, except the wordlist entries are prepended to the domain instead of appended to a path.

Everything else such as argument parsing, error handling for timeouts and unreachable hosts, formatting etc. is just plumbing around that core loop.

## Requirements

- Python 3.x
- `requests`

## Installation

```bash
git clone https://github.com/yourusername/web-enumeration.git
cd web-enumeration
pip install requests
```

## Usage

Directory enumeration:

```bash
python main.py -u http://example.com -w wordlist.txt
```

Subdomain enumeration:

```bash
python main.py -d example.com -w wordlist.txt
```

### Options

| Flag | Description |
|------|-------------|
| `-u`, `--url` | Target URL to scan for directories |
| `-d`, `--domain` | Target domain to scan for subdomains |
| `-w`, `--wordlist` | Path to the wordlist file (required) |

Choose exactly one target option (`-u` or `-d`) for each run.

## Wordlists

The quality of enumeration depends almost entirely on the wordlist. This repo doesn't include one, so bring your own. For subdomain enumeration, use a dedicated subdomain list; it will work much better than a directory list. Good starting points:

- [SecLists](https://github.com/danielmiessler/SecLists) — `Discovery/Web-Content/directory-list-2.3-medium.txt` is the classic choice for directories
- [raft wordlists](https://github.com/danielmiessler/SecLists/tree/master/Discovery/Web-Content) — also in SecLists, larger and noisier

For subdomain enumeration, a dedicated subdomain list like `Discovery/DNS/subdomains-top1million-5000.txt` from SecLists will get much better results than a directory list.

## Limitations

This is a learning project, not a replacement for mature tools. A few honest shortcomings:

- Requests are made sequentially, one at a time. Tools like Gobuster use threads and are orders of magnitude faster.
- There's no response filtering beyond status codes. ffuf lets you filter by response size, words, and lines, which matters when a server returns a custom 404 page with a 200 status code.
- No recursion, which means it won't descend into discovered directories.

If you want to extend it, threading is the natural first step. Reading the source of Gobuster or feroxbuster is a good way to see how the pros handle these problems.

## Legal

Only run this against systems you own or have explicit written permission to test. Enumeration is noisy and will show up in server logs. Unauthorized scanning is illegal in most jurisdictions, regardless of intent.
