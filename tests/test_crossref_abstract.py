#!/usr/bin/env python3
"""Test Crossref API for complete abstracts."""

from bibtools.cli.fetch_abstracts import fetch_abstract_crossref

# Test with a known Springer DOI
test_doi = "10.1007/978-3-031-86193-2_1"

print("Testing Crossref API...")
print(f"DOI: {test_doi}")
print()

abstract = fetch_abstract_crossref(test_doi)

if abstract:
    print("✓ Crossref returned an abstract:")
    print("=" * 70)
    print(abstract)
    print("=" * 70)
    print(f"\nLength: {len(abstract)} characters")
    print(f"Words: {len(abstract.split())} words")
else:
    print("✗ Crossref did not return an abstract")
