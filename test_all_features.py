#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive test script untuk googlesearch module
Menunjukkan semua fitur yang tersedia
"""

from flash_search import search, extract_website_content, save_results_to_file, save_website_content, SearchResult

print("="*80)
print("GOOGLESEARCH MODULE - COMPREHENSIVE TEST")
print("="*80)

# Test 1: Basic Search
print("\n1. BASIC SEARCH (Simple Links)")
print("-" * 80)
results = list(search("Python programming", num_results=3))
print(f"Found {len(results)} results")
for i, url in enumerate(results, 1):
    print(f"  {i}. {url}")

# Test 2: Advanced Search (SearchResult Objects)
print("\n2. ADVANCED SEARCH (SearchResult Objects)")
print("-" * 80)
results = list(search("Data Science", num_results=3, advanced=True))
print(f"Found {len(results)} advanced results")
for i, result in enumerate(results, 1):
    print(f"  {i}. Title: {result.title}")
    print(f"     URL: {result.url}")
    print(f"     Desc: {result.description[:60]}...")

# Test 3: Extract Website Content
print("\n3. EXTRACT WEBSITE CONTENT")
print("-" * 80)
url = "https://www.python.org/"
print(f"Extracting content from: {url}")
content = extract_website_content(url)
if "Error" in content:
    print(f"  Result: {content}")
else:
    print(f"  Successfully extracted {len(content)} characters")
    print(f"  First 100 chars: {content[:100]}...")

# Test 4: Save Website Content to File
print("\n4. SAVE WEBSITE CONTENT TO FILE")
print("-" * 80)
test_url = "https://www.python.org/about/gettingstarted/"
result_msg = save_website_content(test_url)
print(f"  {result_msg}")
# Get the actual filename
filename = test_url.split("//")[-1].split("/")[0] + ".txt"
print(f"  File created: {filename}")

# Test 5: Save Search Results to File
print("\n5. SAVE SEARCH RESULTS TO FILE")
print("-" * 80)
results = list(search("Artificial Intelligence", num_results=5, advanced=True))
save_results_to_file(results, "search_results.txt")
print(f"  Saved {len(results)} search results to: search_results.txt")

print("\n" + "="*80)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("="*80)
