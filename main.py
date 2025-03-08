from tqdm import tqdm
import os
import re

from parser import *
from chunker import *

def main():

    url = "https://www.notion.so/help"
    unique_articles = get_article_urls(url)

    '''
    # sanity check
    for each in tqdm(unique_articles):
        response = requests.get(each)
        if response.status_code != 200:
            print(f"Request failed with status code: {response.status_code}")
    '''

    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    all_chunks = []
    count = 0
    total_len = 0

    print("Scraping and chunking data...")
    for article in tqdm(unique_articles):

        dic = scrape_article(article)

        # intermediate files
        file_name = f"{re.sub(r'[^a-zA-Z&\'\"]', '', dic['title'])}.txt"
        with open(f"{output_folder}/{file_name}", 'w', encoding='utf-8') as file:
            file.write(dic['content'])

        blocks = parse_content(dic['content'])

        combined_blocks = combine_related_blocks(blocks)

        chunks = create_chunks(combined_blocks)
        for chunk in chunks:
            all_chunks.append(chunk)
            count += 1
            total_len += len(chunk)

    print("Saving chunks to chunks.txt...")
    with open("chunks.txt", "w") as file:
        file.write("\n##########################################\n")
        for chunk in tqdm(all_chunks):
            file.write(chunk)
            file.write("\n##########################################\n")

    print(f"{count} total chunks")
    print(f"average # of characters = {total_len / count}")

if __name__ == '__main__':
    main()