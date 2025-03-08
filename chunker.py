import re
from typing import List, Dict, Any

def parse_content(content: str) -> List[Dict[str, str]]:
    '''Parse content with special $@type@$ and $@type_end@$ tags into structured blocks.'''
    # RE for boundaries of each block
    pattern = r'\$@(\w+)@\$(.*?)\$@\1_end@\$'
    
    blocks = []
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        block_type = match.group(1)
        block_content = match.group(2).strip()
        
        blocks.append({
            'type': block_type,
            'content': block_content
        })
    
    return blocks

def combine_related_blocks(blocks: List[Dict[str, str]]) -> List[Dict[str, str]]:
    '''
    combine related blocks:
    - if a block ends with a colon, combine it with the next block
    - the combined block will have the type of the second block
    '''
    if not blocks:
        return []
    
    combined_blocks = []
    
    i = 0
    while i < len(blocks):
        cur_block = blocks[i]

        if (i < len(blocks)-1 and cur_block['content'] and \
            cur_block['content'].strip().endswith(':')):
            next_block = blocks[i+1]
            combined_block = {
                'type': next_block['type'],
                'content': cur_block['content'] + "\n" + next_block['content']
            }

            combined_blocks.append(combined_block)
            i += 2
        else:
            combined_blocks.append(cur_block)
            i += 1
    
    return combined_blocks

def create_chunks(blocks: List[Dict[str, str]], max_chunk_size: int = 750) -> List[str]:
    chunks = []
    current_chunk = []
    current_size = 0

    i = 0
    while i < len(blocks):
        block = blocks[i]
        block_size = len(block['content'])
        block_type = block['type']

        # check if a new chunk needs to be created
        #       *current chunk must not be empty
        #       *header block will always be added
        if (current_size + block_size > max_chunk_size) and \
            current_chunk and not block_type.startswith('h'):

            # if last block added is header, move it to next chunk
            if current_chunk[-1]['type'].startswith('h'):
                header_block = current_chunk.pop()

                # check if current chunk is not empty, add to chunks if so
                if current_chunk:
                    chunks.append(format_chunk(current_chunk))

                # new chunk with header popped previously
                current_chunk = [header_block]
                current_size = len(header_block['content'])
            else:
                # last block is not a header, simply add to chunks
                chunks.append(format_chunk(current_chunk))
                current_chunk = []
                current_size = 0
        
        # add current block to the chunk
        current_chunk.append(block)
        current_size += block_size

        # SPECIAL CASE: single block size > max chunk size
        if (block_size > max_chunk_size) and \
            not block_type.startswith('h') and \
            len(current_chunk) == 1:
            chunks.append(format_chunk(current_chunk))
            current_chunk = []
            current_size = 0

        i += 1
    
    # last chunk
    if current_chunk:
        chunks.append(format_chunk(current_chunk))

    return chunks

def format_chunk(blocks: List[Dict[str, str]]) -> str:
    '''format a list of dictionaries to appropriate string format'''

    formatted_chunk = ""
    
    for block in blocks:
        block_type = block['type']
        content = block['content']
        
        if block_type == 'h1':
            formatted_chunk += f"# {content}\n"
        elif block_type == 'h2':
            formatted_chunk += f"## {content}\n"
        elif block_type == 'h3':
            formatted_chunk += f"### {content}\n"
        elif block_type == 'p':
            formatted_chunk += f"{content}\n"
        elif block_type == 'list':
            formatted_chunk += f"{content}\n"
        elif block_type == 'table':
            formatted_chunk += f"{content}\n"
        else:
            formatted_chunk += f"{content}\n"
    
    return formatted_chunk.strip()