import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

def get_article_urls(url):
    '''returns a sorted list of related urls to be scraped'''

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Request failed with status code: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')

    unique_articles = set()
    category_urls = set()
    
    # get urls in main help page first
    for a_tag in soup.find_all('a'):
        href = a_tag.get('href')
        if href:
            if "notion-academy" in href or href=="https://www.notion.com/help/reference":
                continue
            if "help/" in href or "developers.notion.com/" in href:
                if href.startswith('/'):
                    href = f"https://www.notion.com{href}"
                unique_articles.add(href)
                if "category" in href:
                    category_urls.add(href)
    print(f"Extracted {len(unique_articles)} urls from main help page...")

    # get urls from each category
    print("Extracting URLs from categorical websites...")
    for category_url in tqdm(category_urls):
        response = requests.get(category_url)
        if response.status_code != 200:
            print(f"Category url request failed with status code: {response.status_code}")

        category_soup = BeautifulSoup(response.content, 'html.parser')

        for a_tag in category_soup.find_all('a'):
            href = a_tag.get('href')
            if href and "help/guides/" in href:
                if href.startswith('/'):
                    href = f"https://www.notion.com{href}"
                unique_articles.add(href)

    # remove category urls and API documentations

    for url in category_urls:
        unique_articles.remove(url)

    unique_articles = [i for i in unique_articles if "developers" not in i]

    print(f"Extracted {len(unique_articles)} unique articles in total...")

    return sorted(unique_articles)

def scrape_article(url):
    '''returns a dictionary with information about the article given the url'''

    time.sleep(1)
    response = requests.get(url)
    article_soup = BeautifulSoup(response.content, 'html.parser')

    title = article_soup.find('h1').get_text(strip=True) if article_soup.find('h1') else 'No Title'

    content = []
    main_content = article_soup.find('article', 
                                     class_='contentfulRichText_richText__rW7Oq')
    
    # className: "contentfulRichText_richText__rW7Oq contentfulRichText_sans__UVbfz"

    content.append(f"$@h1@$\n{title}\n$@h1_end@$\n")

    if main_content:
        for media in main_content.find_all(['img', 'video', 'audio', 'figure', 'svg']):
            media.decompose()

        for element in main_content.find_all(['p', 'h2', 'h3', 'ul', 'ol', 'table']):
            if element.find_parent(['ul', 'ol', 'table']):
                continue
            elif element.name in ['ul', 'ol']:
                # recursively process nested lists
                # print("process_list() called")
                content.append("$@list@$\n")
                process_list(element, content)
                content.append("$@list_end@$\n")
            elif element.name == 'table':
                # extract table data into a 2D array
                table_text = process_table(element)
                content.append("$@table@$\n")
                content.append(table_text)
                content.append("\n$@table_end@$\n")
            else:  # avoid redundancy
                element_content = element.get_text(strip=True)
                if "Uh-oh" in element_content:
                    continue
                else:
                    content.append(f"$@{element.name}@$\n")
                    content.append(element_content)
                    content.append(f"\n$@{element.name}_end@$\n")

    return {
        'url': url,
        'title': title,
        'content': ''.join(content).encode('ascii', errors='ignore').decode('ascii')
    }

def process_list(list_element, content, level=0):
    '''recursively process nested lists and add them to content'''
    list_items = list_element.find_all('li', recursive=False)
    if not list_items:
        return
    # print(f"{len(list_items)} items at level {level}")
    # symbols different level of nested list
    symbols = ['-', '*', '>', '<', '#', '~']
    symbol = symbols[level]
    
    # content.append("List:")
    for item in list_items:
        item_text = item.get_text(strip=True)
        content.append(f"{symbol} {item_text}\n")
        
        # recursive call
        nested_lists = item.find_all(['ul', 'ol'], recursive=True)
        for nested_list in nested_lists:
            if nested_list.find_parent('li') == item:
                process_list(nested_list, content, level + 1)

def process_table(table_element):
    '''extract data from table into a 2D array'''
    table_data = []
    
    for row in table_element.find_all('tr'):
        row_data = []
        for cell in row.find_all(['th', 'td']):
            cell_text = cell.get_text(strip=True)
            row_data.append(cell_text)
        table_data.append(row_data)
    
    table_text = "Table: ["
    for row in table_data:
        row_text = "["
        for element in row:
            row_text += element + ","
        row_text += "]\n"
        table_text += row_text
    table_text = table_text[:-1] + "]"

    return table_text