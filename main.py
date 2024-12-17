import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    tokens = word_tokenize(text)  # Tokenize text
    stop_words = set(stopwords.words("english"))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return filtered_tokens


def classify_website(keyword_count, threshold=1):
    if sum(keyword_count.values()) >= threshold:
        return True
    return False


def match_keywords(tokens, keywords):
    keyword_count = {keyword: tokens.count(keyword) for keyword in keywords}
    total_matches = sum(keyword_count.values())
    return keyword_count, total_matches


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
            "digital transforma tion", "web development", "technology consulting",
            "web", "design", "development"
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

        tokens = preprocess_text(visible_text)
        keyword_count, total_matches = match_keywords(tokens, found_keywords)
        classification = classify_website(keyword_count)
        # Return results
        if classification:
            return {"isSoftwareCompany":True,"keywordList":f"{', '.join(found_keywords)}","isError":False,"ErrorMessage":""}
        else:
            return {"isSoftwareCompany":False,"keywordList":"","isError":False,"ErrorMessage":""}
    
    except requests.exceptions.RequestException as e:
        return {"isSoftwareCompany":False,"keywordList":"","isError":True,"ErrorMessage":str(e.args)}


def get_data():
    try:
        return pd.read_csv("./AnalyzeData.csv")
    except Exception as E:
        print("Error ocuccred")


if __name__ == "__main__":
    data = get_data()
    dict1 = []
    row1 = data.sample(frac=0.5)
    check_url_for_software_dev_company("https://anisans.com")
    sample = 0
    # for index,row in row1.iterrows():
    #     if sample == 50:
    #         break
    #     result = check_url_for_software_dev_company(row["Website"])
    #     result["website"] = row["Website"]
    #     dict1.append(result)
    #     print(result)
    #     sample +=1
    # df = pd.DataFrame(dict1)
    # df.to_excel("sampleOutput.xlsx")
    # # df.to_csv("sample.csv",index=False)