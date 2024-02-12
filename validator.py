import os
import toml
import requests
import re
from urllib.parse import urlparse

art = '''
  M   M  BBBBB  
  MM MM  B    B 
  M M M  BBBBB  
  M   M  B    B 
  M   M  BBBBB  

==== Mansoor Barri ====
https://mansoorbarri.com
'''
print(art)

def is_absolute_url(url):
    return bool(urlparse(url).scheme)

def check_link_validity(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_readme_links(readme_path):
    if not os.path.exists(readme_path):
        return False, "Missing README.md file in the specified theme directory", None

    with open(readme_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Use regex to find all links in the README.md
    links = re.findall(r'\[.*?\]\((.*?)\)', md_content)

    for link_url in links:
        is_absolute = is_absolute_url(link_url)
        is_valid = check_link_validity(link_url)

        if not is_absolute:
            return False, f"The link '{link_url}' in README.md is not absolute", "README.md"
        elif not is_valid:
            return False, f"The link '{link_url}' in README.md is absolute but invalid", "README.md"

    return True, "Links in README.md are valid.", None

def check_theme_requirements(theme_directory):
    # Check for theme.toml
    theme_toml_path = os.path.join(theme_directory, "theme.toml")
    if not os.path.exists(theme_toml_path):
        return False, "Missing theme.toml file in the specified theme directory", None

    # Check for /images/screenshot.png or .jpg
    screenshot_path = os.path.join(theme_directory, "images", "screenshot.png")
    if not os.path.exists(screenshot_path):
        screenshot_path = os.path.join(theme_directory, "images", "screenshot.jpg")
        if not os.path.exists(screenshot_path):
            return False, "Missing screenshot.png or screenshot.jpg in the images directory", None

    # Check for /images/tn.png or .jpg
    tn_path = os.path.join(theme_directory, "images", "tn.png")
    if not os.path.exists(tn_path):
        tn_path = os.path.join(theme_directory, "images", "tn.jpg")
        if not os.path.exists(tn_path):
            return False, "Missing tn.png or tn.jpg in the images directory", None
    
    # Check README.md for links
    readme_path = os.path.join(theme_directory, "README.md")
    readme_success, readme_message, _ = check_readme_links(readme_path)
    if not readme_success:
        return False, readme_message, "README.md"

    return True, "Theme requirements are met.", None

    # Check theme.toml for specified metadata
    with open(theme_toml_path, "r", encoding="utf-8") as f:
        toml_data = toml.load(f)

    required_keys = [
        "name",
        "license",
        "licenselink",
        "description",
        "homepage",
        "demosite",
        "tags",
        "authors",
    ]

    for key in required_keys:
        if key not in toml_data or not toml_data[key]:
            return False, f"Missing or empty value for '{key}' in theme.toml", "theme.toml"

    # Check if the licenselink is an absolute URL and is valid
    if "licenselink" in toml_data:
        license_link = toml_data["licenselink"]
        is_absolute = is_absolute_url(license_link)
        is_valid = check_link_validity(license_link)

        if not is_absolute:
            return False, f"The 'licenselink' is not absolute", "theme.toml"
        elif not is_valid:
            return False, f"The 'licenselink' is absolute but invalid", "theme.toml"

    # Ask the user if the theme is ported
    is_ported = input("Is the theme ported from an existing theme? (y/n): ").lower() == "y"

    if is_ported:
        # Check for [original] section
        if "original" not in toml_data:
            return False, "Missing [original] section in theme.toml for ported theme", "theme.toml"

        original_data = toml_data["original"]

        # Check for required keys in [original] section
        original_required_keys = ["author", "homepage", "repo"]
        for key in original_required_keys:
            if key not in original_data or not original_data[key]:
                return False, f"Missing or empty value for '{key}' in [original] section of theme.toml", "theme.toml"

            # Check if the 'homepage' link is an absolute URL and is valid
            if key == "homepage":
                homepage_link = original_data[key]
                is_absolute = is_absolute_url(homepage_link)
                is_valid = check_link_validity(homepage_link)
                if not is_absolute:
                    return False, f"The 'homepage' link is not absolute in [original] section", "theme.toml"
                elif not is_valid:
                    return False, f"The 'homepage' link is absolute but invalid in [original] section", "theme.toml"

            # Check if the 'repo' link is an absolute URL and is valid
            if key == "repo":
                repo_link = original_data[key]
                is_absolute = is_absolute_url(repo_link)
                is_valid = check_link_validity(repo_link)
                if not is_absolute:
                    return False, f"The 'repo' link is not absolute in [original] section", "theme.toml"
                elif not is_valid:
                    return False, f"The 'repo' link is absolute but invalid in [original] section", "theme.toml"

    return True, "Theme requirements are met.", None

def main():
    theme_directory = input("Enter the path to the theme directory: ")
    success, message, file = check_theme_requirements(theme_directory)

    if success:
        print("Theme requirements are met. Ready to submit!")
    else:
        print(f"Theme does not meet requirements in {file}. {message}")

if __name__ == "__main__":
    main()
