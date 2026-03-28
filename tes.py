from flash_search import search, extract_website_content, save_results_to_file, SearchResult

print("Starting search for 'Machine Learning'...")
# 1. Search dengan satu baris
results = list(search("Machine Learning", advanced=True, num_results=10))
print(f"Found {len(results)} results")

# 2. Tampilkan hasil
for result in results:
    print(f"Title: {result.title}\n URL: {result.url}\n")
