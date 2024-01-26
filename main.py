import os
import toml
import requests
from urllib.parse import urlparse

def is_absolute_url(url):
    return bool(urlparse(url).scheme)

def check_link_validity(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_theme_requirements():
    # Check for theme.toml
    theme_toml_path = "theme.toml"
    if not os.path.exists(theme_toml_path):
        return False, "Missing theme.toml file in the theme root"

    # Check for /images/screenshot.png or .jpg
    screenshot_path = os.path.join("images", "screenshot.png")
    if not os.path.exists(screenshot_path):
        screenshot_path = os.path.join("images", "screenshot.jpg")
        if not os.path.exists(screenshot_path):
            return False, "Missing screenshot.png or screenshot.jpg in the images directory"

    # Check for /images/tn.png or .jpg
    tn_path = os.path.join("images", "tn.png")
    if not os.path.exists(tn_path):
        tn_path = os.path.join("images", "tn.jpg")
        if not os.path.exists(tn_path):
            return False, "Missing tn.png or tn.jpg in the images directory"

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
            return False, f"Missing or empty value for '{key}' in theme.toml"

    # Check if the licenselink is an absolute URL and is valid
    if "licenselink" in toml_data:
        license_link = toml_data["licenselink"]
        if not is_absolute_url(license_link) or not check_link_validity(license_link):
            return False, "The 'licenselink' must be an absolute and valid URL"

    # Ask the user if the theme is ported
    is_ported = input("Is the theme ported from an existing theme? (y/n): ").lower() == "y"

    if is_ported:
        # Check for [original] section
        if "original" not in toml_data:
            return False, "Missing [original] section in theme.toml for ported theme"

        original_data = toml_data["original"]

        # Check for required keys in [original] section
        original_required_keys = ["author", "homepage", "repo"]
        for key in original_required_keys:
            if key not in original_data or not original_data[key]:
                return False, f"Missing or empty value for '{key}' in [original] section of theme.toml"

            # Check if the 'homepage' link is an absolute URL and is valid
            if key == "homepage" and not is_absolute_url(original_data[key]):
                return False, "The 'homepage' link in [original] section must be an absolute URL"

            # Check if the 'repo' link is an absolute URL and is valid
            if key == "repo" and not is_absolute_url(original_data[key]):
                return False, "The 'repo' link in [original] section must be an absolute URL"

    return True, "Theme requirements are met."

def main():
    success, message = check_theme_requirements()

    if success:
        print("Theme requirements are met. Ready to submit!")
    else:
        print(f"Theme does not meet requirements. {message}")

if __name__ == "__main__":
    main()
