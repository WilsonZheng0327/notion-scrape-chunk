from tqdm import tqdm
import os
import re

from parser import *
from chunker import *


def get_notion_info():
    '''returns an array of chunks of information scraped from Notion help center'''

    '''
    Using BeautifulSoup, get all articles in the help center

    Intermediate output:
        urls.txt - urls of articles scraped
    '''
    url = "https://www.notion.so/help"
    unique_articles = get_article_urls(url)

    with open("urls.txt", 'w') as file:
        for article in unique_articles:
            file.write(f"{article}\n")

    # stores all parsed content of each article
    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    all_chunks = []
    count = 0
    total_len = 0

    '''
    Using BeautifulSoup, scrape the main content of each article
    ignoring media, and format lists and tables

    Intermediate output: 
        output/{article_name}.txt - parsed content
    '''
    print("Scraping and chunking data...")
    for article in tqdm(unique_articles):

        dic = scrape_article(article)

        # intermediate output files
        file_name = f"{re.sub(r'[^a-zA-Z&\'\"]', '', dic['title'])}.txt"
        with open(f"{output_folder}/{file_name}", 'w', encoding='utf-8') as file:
            file.write(dic['content'])

        # parse output file into blocks of content (based on html tags)
        blocks = parse_content(dic['content'])

        # combine blocks that should be in the same chunk
        combined_blocks = combine_related_blocks(blocks)

        # form chunks
        chunks = create_chunks(combined_blocks)
        for chunk in chunks:
            all_chunks.append(chunk)
            count += 1
            total_len += len(chunk)

    '''
    Final output:
        chunks.txt - all chunks separated by a line of #
                     
    Formatting:
        # = h1
        ## = h2
        ### = h3
    '''
    print("Saving chunks to chunks.txt...")
    with open("chunks.txt", "w") as file:
        file.write("\n\n##########################################\n\n")
        for chunk in tqdm(all_chunks):
            file.write(chunk)
            file.write("\n\n##########################################\n\n")

    print(f"{count} total chunks")
    print(f"average # of characters = {total_len / count}")

    return all_chunks


if __name__ == '__main__':
    all_chunks = get_notion_info()