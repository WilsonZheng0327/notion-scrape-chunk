# notion-scrape-chunk
Scraping all help articles from https://www.notion.com/help and chunking information

Versions:\
Python 3.13.0\
pip 24.2\
Others please refer to requirements.txt

Clone the repo with: ```git clone https://github.com/WilsonZheng0327/notion-scrape-chunk.git```\
Download packages with: ```pip install -r requirements.txt```\
Run main script with: ```python main.py```

```get_notion_info()``` in *main.py* returns an array of chunks as required by the project\
I've added an additional output that is *chunks.txt* that will have all the chunks saved to a text file with delimiters.

*sample_output.txt* is what it would look like, also added for convenience. Running the script takes about 6 minutes.
