import json

# Function to extract names from the following JSON
def extract_names_from_following(json_content):
    names = [entry['value'] for item in json_content['relationships_following']
             for entry in item['string_list_data']]
    return set(names)

# Function to extract names from the followers JSON (list of dictionaries)
def extract_names_from_followers(json_content):
    names = [entry['value'] for item in json_content
             for entry in item['string_list_data']]
    return set(names)

# Load JSON content
with open('reports/followers_1.json', 'r', encoding='utf-8') as file:
    followers_json = json.load(file)
    
with open('reports/following.json', 'r', encoding='utf-8') as file:
    following_json = json.load(file)

# Extract names
followers_names = extract_names_from_followers(followers_json)
following_names = extract_names_from_following(following_json)

# Find names in 'following' not in 'followers'
names_in_following_not_in_followers = following_names - followers_names

# Print out results
print(f"Follower Count: {len(followers_names)}")
print(f"Following Count: {len(following_names)}")
print(f"Accounts Not Following Back: {len(names_in_following_not_in_followers)}")
for name in sorted(names_in_following_not_in_followers):
    print(name)
