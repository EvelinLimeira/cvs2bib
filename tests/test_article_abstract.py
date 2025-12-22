#!/usr/bin/env python3
"""Test with the article DOI you provided."""

from bibtools.cli.fetch_abstracts import fetch_abstract_doi_org
import urllib.request
import re

doi = "10.1007/s10845-025-02637-x"

print(f"Testing DOI: {doi}")
print("=" * 70)

# Get the abstract using our function
abstract = fetch_abstract_doi_org(doi)

if abstract:
    print("\n✓ Abstract found:")
    print("-" * 70)
    print(abstract)
    print("-" * 70)
    print(f"\nLength: {len(abstract)} characters")
    print(f"Words: {len(abstract.split())} words")
else:
    print("\n✗ No abstract found with current method")
    
# Let's also check what's in the HTML
print("\n" + "=" * 70)
print("Checking HTML structure...")
print("=" * 70)

url = f"https://doi.org/{doi}"
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

with urllib.request.urlopen(req, timeout=15) as response:
    html = response.read().decode('utf-8', errors='ignore')

# Check for abstract section
if 'id="Abs1"' in html:
    print("\n✓ Found abstract section with id='Abs1'")
    match = re.search(r'<section[^>]*id="Abs1"[^>]*>(.*?)</section>', html, re.DOTALL)
    if match:
        section = match.group(1)
        print(f"Section length: {len(section)} characters")
        print(f"\nFirst 500 chars of section:\n{section[:500]}")
else:
    print("\n✗ No section with id='Abs1' found")

# Check for paragraphs in abstract
p_tags = re.findall(r'<p[^>]*class="[^"]*Para[^"]*"[^>]*>(.*?)</p>', html, re.DOTALL)
print(f"\n✓ Found {len(p_tags)} paragraph tags with 'Para' class")
if p_tags:
    print(f"\nFirst paragraph (first 200 chars):\n{p_tags[0][:200]}")
