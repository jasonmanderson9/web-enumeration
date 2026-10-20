# Web Enumeration Tool

A small Python tool for discovering hidden directories and subdomains on a target web server. I built this as a learning project to show how enumeration tools like Gobuster, dirb, and ffuf work under the hood.

I'm writing a full walkthrough of how I built this and how the underlying techniques work. You can find it here: [write-up link coming soon]

## What it does

The tool has two modes:

- **Directory enumeration** — takes a base URL and a wordlist, then requests every possible path (`example.com/admin`, `example.com/backup`, ...) and reports which ones exist.
- **Subdomain enumeration** — takes a domain and a wordlist, then tries every possible subdomain (`dev.example.com`, `staging.example.com`, ...) and reports which ones resolve to a live web server.

## How it works

Enumeration tools are conceptually simple: web servers almost always host more than what is linked on their public pages. Admin panels, backup files, test environments, and forgotten endpoints often sit at predictable paths. Since there's no way to query a server for a list of its directories, the only option is to guess or brute-force by taking a list of common names and ask the server about each one.

For every word in the wordlist, the script sends an HTTP request and looks at the response status code:

- **200 OK** — the resource exists and is accessible.
- **301/302 Redirect** — the resource exists, but the server wants to send you somewhere else (often a login page). Still worth investigating.
- **403 Forbidden** — the resource exists but access is denied.
- **404 Not Found** — nothing there. This is the vast majority of responses.

The tool reports responses with status codes 200, 301, and 302 as potential leads, reports 403 responses separately as forbidden resources that may exist but deny access, and skips 404 responses. Other HTTP response codes and request failures are also reported. Redirects are disabled in the requests so the tool sees the raw status code instead of silently following them.

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

## Wordlists

The quality of enumeration depends almost entirely on the wordlist. This repo doesn't ship with one, so bring your own. Good starting points:

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
