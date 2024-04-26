import json

# Function to extract names from a JSON file
def extract_names_from_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        json_content = json.load(file)
    return set(entry['value'] for item in json_content for entry in item['string_list_data'])

# Extract names from JSON files
current_followers_names = extract_names_from_json('reports/followers_1.json')  # From current JSON
old_followers_names = extract_names_from_json('reports/old_followers.json')  # From old JSON

# Find names in 'old followers' not in 'current followers'
unfollowed_names = old_followers_names - current_followers_names

# Output results
print(f"Old Follower Count: {len(old_followers_names)}")
print(f"Current Follower Count: {len(current_followers_names)}")
print(f"Accounts Not Following Back: {len(unfollowed_names)}")
for name in sorted(unfollowed_names):
    print(name)
