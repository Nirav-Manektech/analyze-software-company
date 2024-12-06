import requests
from bs4 import BeautifulSoup
import re

def check_url_for_software_dev_company(url):
    try:
        # Fetch the webpage content
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        content = response.text
        
        # Parse the HTML
        soup = BeautifulSoup(content, "html.parser")
        
        # Keywords to identify a software development company
        keywords = [
            "software development", "mobile app", "custom solutions",
            "IT services", "cloud solutions", "ERP", "CRM", "business automation",
            "digital transformation", "web development", "technology consulting"
        ]
        
        # Analyze meta title and description
        title = soup.title.string if soup.title else ""
        meta_description = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag:
            meta_description = meta_tag.get("content", "")
        
        # Analyze visible text
        visible_text = soup.get_text(separator=" ").lower()
        
        # Check for keywords
        found_keywords = [
            keyword for keyword in keywords
            if re.search(rf"\b{keyword}\b", visible_text, re.IGNORECASE)
        ]
        
        # Return results
        if found_keywords:
            return f"The URL '{url}' is likely a software development company. Keywords found: {', '.join(found_keywords)}"
        else:
            return f"The URL '{url}' does not appear to be a software development company."
    
    except requests.exceptions.RequestException as e:
        return f"Error accessing the URL '{url}': {e}"



if __name__ == "__main__":
    # Example Usage
    url_to_check = "https://radixweb.com"
    result = check_url_for_software_dev_company(url_to_check)
    print(result)
