#!/usr/bin/env python3
"""CLI for fetching abstracts from CSV and generating output CSV."""

import argparse
import sys
import os
import csv
import time
from pathlib import Path

# Import the abstract fetching functions from fetch_abstracts
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from bibtools.cli.fetch_abstracts import (
    fetch_abstract_springer,
    fetch_abstract_openalex,
    fetch_abstract_crossref,
    fetch_abstract_semanticscholar,
    fetch_abstract_europepmc,
    fetch_abstract_doi_org
)


def main():
    """CLI entry point for CSV-based abstract fetcher."""
    parser = argparse.ArgumentParser(
        description='Fetch abstracts from CSV file with DOIs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch abstracts from CSV
  python -m bibtools.cli.fetch_abstracts_csv --input papers.csv --output papers_with_abstracts.csv
  
  # With Springer API key
  python -m bibtools.cli.fetch_abstracts_csv --input papers.csv --output papers_with_abstracts.csv --springer-api-key YOUR_KEY

CSV Format:
  Required columns: DOI (or Item DOI)
  Optional columns: Title, Abstract (will be filled if empty)
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input CSV file with DOIs'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output CSV file with abstracts'
    )
    
    parser.add_argument(
        '--springer-api-key',
        type=str,
        default=os.environ.get('SPRINGER_API_KEY'),
        help='Springer API key (optional)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=10000,
        help='Maximum number of items to process'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Execute
    exit_code = execute_csv_fetch(
        args.input,
        args.output,
        args.springer_api_key,
        args.limit
    )
    sys.exit(exit_code)


def execute_csv_fetch(input_file: str, output_file: str, 
                     springer_api_key: str = None, limit: int = 10000) -> int:
    """Execute the CSV-based abstract fetching process."""
    
    print("CSV Abstract Fetcher")
    print("=" * 70)
    print(f"Input file:   {input_file}")
    print(f"Output file:  {output_file}")
    print(f"Limit:        {limit} items")
    print(f"Springer API: {'Enabled' if springer_api_key else 'Disabled'}")
    print()
    
    try:
        # Read CSV
        print("Reading CSV file...")
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"Found {len(rows)} rows in CSV")
        
        # Detect DOI column
        doi_column = None
        for col in ['DOI', 'Item DOI', 'doi']:
            if col in rows[0]:
                doi_column = col
                break
        
        if not doi_column:
            print("Error: No DOI column found in CSV", file=sys.stderr)
            print("Expected columns: 'DOI', 'Item DOI', or 'doi'", file=sys.stderr)
            return 1
        
        print(f"Using DOI column: '{doi_column}'")
        
        # Detect abstract column
        abstract_column = None
        for col in ['Abstract', 'Abstract Note', 'abstractNote', 'abstract']:
            if col in rows[0]:
                abstract_column = col
                break
        
        if not abstract_column:
            # Add abstract column
            abstract_column = 'Abstract'
            for row in rows:
                row[abstract_column] = ''
            print(f"Added new column: '{abstract_column}'")
        else:
            print(f"Using abstract column: '{abstract_column}'")
        
        # Filter rows without abstracts
        rows_to_fetch = []
        for i, row in enumerate(rows[:limit]):
            doi = row.get(doi_column, '').strip()
            abstract = row.get(abstract_column, '').strip()
            
            if doi and not abstract:
                rows_to_fetch.append((i, row, doi))
        
        print(f"Found {len(rows_to_fetch)} items without abstracts")
        print()
        
        if not rows_to_fetch:
            print("All items already have abstracts!")
            return 0
        
        # Fetch abstracts
        print("Fetching abstracts...")
        print()
        
        found = 0
        not_found = 0
        
        for idx, (row_idx, row, doi) in enumerate(rows_to_fetch, 1):
            title = row.get('Title', row.get('Item Title', ''))[:50]
            
            # Try each API
            abstract = None
            source = None
            
            # 1. Springer API
            if springer_api_key:
                abstract = fetch_abstract_springer(doi, springer_api_key)
                if abstract:
                    source = 'Springer API'
            
            # 2. OpenAlex
            if not abstract:
                abstract = fetch_abstract_openalex(doi)
                if abstract:
                    source = 'OpenAlex'
            
            # 3. CrossRef
            if not abstract:
                abstract = fetch_abstract_crossref(doi)
                if abstract:
                    source = 'CrossRef'
            
            # 4. Semantic Scholar
            if not abstract:
                abstract = fetch_abstract_semanticscholar(doi)
                if abstract:
                    source = 'Semantic Scholar'
            
            # 5. Europe PMC
            if not abstract:
                abstract = fetch_abstract_europepmc(doi)
                if abstract:
                    source = 'Europe PMC'
            
            # 6. DOI.org scraping
            if not abstract:
                abstract = fetch_abstract_doi_org(doi)
                if abstract:
                    source = 'DOI.org (scraped)'
            
            # Update row
            if abstract:
                rows[row_idx][abstract_column] = abstract
                found += 1
                print(f"[{idx}/{len(rows_to_fetch)}] ✓ {title}... → [{source}]")
            else:
                not_found += 1
                print(f"[{idx}/{len(rows_to_fetch)}] ✗ {title}...")
            
            # Rate limiting
            time.sleep(0.5)
        
        print()
        print("=" * 70)
        print("✓ Abstract fetch completed!")
        print()
        print("Statistics:")
        print(f"  Items checked:     {len(rows_to_fetch)}")
        print(f"  Abstracts found:   {found}")
        print(f"  Not found:         {not_found}")
        print("=" * 70)
        print()
        
        # Write output CSV
        print(f"Writing output to {output_file}...")
        
        # Get all fieldnames
        fieldnames = list(rows[0].keys())
        if abstract_column not in fieldnames:
            fieldnames.append(abstract_column)
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✓ Output saved: {output_file}")
        print()
        
        return 0
        
    except Exception as e:
        print()
        print("=" * 70)
        print("✗ UNEXPECTED ERROR", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print()
        print(f"{type(e).__name__}: {str(e)}", file=sys.stderr)
        print()
        import traceback
        traceback.print_exc()
        return 99


if __name__ == '__main__':
    main()
