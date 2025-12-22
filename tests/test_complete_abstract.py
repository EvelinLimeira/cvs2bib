#!/usr/bin/env python3
"""Test if the improved scraping gets complete abstracts."""

from bibtools.cli.fetch_abstracts import fetch_abstract_doi_org

# Test with a known Springer DOI
test_doi = "10.1007/978-3-031-86193-2_1"  # WireLlama paper

print("Testing improved DOI.org scraping...")
print(f"DOI: {test_doi}")
print()

abstract = fetch_abstract_doi_org(test_doi)

if abstract:
    print("✓ Abstract found:")
    print("=" * 70)
    print(abstract)
    print("=" * 70)
    print(f"\nLength: {len(abstract)} characters")
    print(f"Words: {len(abstract.split())} words")
else:
    print("✗ No abstract found")
