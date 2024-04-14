from bs4 import BeautifulSoup

# Function to extract names from HTML
def extract_names_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    names = [a.text for a in soup.find_all('a', href=True)]
    return set(names)

# Load HTML content
with open('reports/followers_1.html', 'r', encoding='utf-8') as file:
    followers_html = file.read()
    
with open('reports/following.html', 'r', encoding='utf-8') as file:
    following_html = file.read()

# Extract names
followers_names = extract_names_from_html(followers_html)
following_names = extract_names_from_html(following_html)

# Find names in 'following' not in 'followers'
names_in_following_not_in_followers = following_names - followers_names

# Print out results
print(f"Follower Count: {len(followers_names)}")
print(f"Following Count: {len(following_names)}")
print("Accounts Not Following Back:")
for name in sorted(names_in_following_not_in_followers):
    print(name)