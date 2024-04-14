from bs4 import BeautifulSoup
import json

# Function to extract names from HTML
def extract_names_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    names = [a.text for a in soup.find_all('a', href=True)]
    return set(names)

# Load HTML content
with open('reports/followers_1.html', 'r', encoding='utf-8') as file:
    followers_html = file.read()

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

# Extract names
past_followers_names = extract_names_from_html(followers_html) # if html
current_followers_names = extract_names_from_followers(followers_json) # if json

# Find names in 'past follwers' not in 'followers'
names_in_following_not_in_followers = past_followers_names - current_followers_names

# Print out results
print(f"Past Follower Count: {len(past_followers_names)}")
print(f"Current Following Count: {len(current_followers_names)}")
print(f"Accounts Not Following Back: {len(names_in_following_not_in_followers)}")
for name in sorted(names_in_following_not_in_followers):
    print(name)
