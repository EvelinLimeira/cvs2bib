#!/usr/bin/env python3
"""Test Springer API with a sample DOI."""

from bibtools.cli.fetch_abstracts import fetch_abstract_springer
from bibtools.utils.config import get_springer_api_key

# Test with a known Springer DOI
test_doi = "10.1007/978-3-031-86193-2_1"  # WireLlama paper
springer_key = get_springer_api_key()

print("Testing Springer API...")
print(f"DOI: {test_doi}")
print(f"API Key: {springer_key[:20]}...")
print()

abstract = fetch_abstract_springer(test_doi, springer_key)

if abstract:
    print("✓ Springer API returned an abstract:")
    print("-" * 70)
    print(abstract[:500] + "..." if len(abstract) > 500 else abstract)
    print("-" * 70)
else:
    print("✗ Springer API did not return an abstract")
    print("This DOI might not be available in Springer API")
