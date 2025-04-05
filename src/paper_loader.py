import requests
import json
import time

def decode_abstract(abstract_dict):
    if not isinstance(abstract_dict, dict):
        return abstract_dict 
 
    word_positions = []

    for word, positions in abstract_dict.items():
        for pos in positions:
            word_positions.append((pos, word))

    word_positions.sort()
    restored_abstract = " ".join(word for _, word in word_positions)
    
    return restored_abstract

def get_id_from_openc(id):
    if id:
        # 'https://openalex.org/W3123532914'
        return id.split("/")[-1]
    else:
        return ""
    
def get_topics_from_openalex(origin_topics):
    result = []
    for topic in origin_topics:
        result.append({
            "topic_id": get_id_from_openc(topic.get("id", "")),
            "display_name": topic.get("display_name", ""),
            "score": topic.get("score", ""),
            "subfield": topic["subfield"]["display_name"],
            "field": topic["field"]["display_name"],
            "domain": topic["domain"]["display_name"],
        })
    return result

def get_article_info_by_author_id(author_id):
    if not author_id or author_id == "Not Found":
        return []
    
    base_url = f"https://api.openalex.org/works?filter=author.id:{author_id}&per-page=25"
    all_results = []
    cursor = "*"  # Start with initial cursor
    
    while cursor:
        try:
            url = f"{base_url}&cursor={cursor}"
            print(f"Fetching papers with cursor: {cursor}")
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Process current page results
            for work in data['results']:
                paper_info = {
                    "title": work.get("title", ""),
                    "doi": work.get("doi", ""),
                    "openalex_id": get_id_from_openc(work.get("id", "")),
                    "author_id": author_id,
                    "publication_date": work.get("publication_date", ""),
                    "abstract": decode_abstract(work.get("abstract_inverted_index", "")),
                    "topics": get_topics_from_openalex(work.get("topics", []))
                }
                all_results.append(paper_info)
            
            # Get next cursor from meta
            cursor = data.get('meta', {}).get('next_cursor')
            if cursor:
                time.sleep(1)  # Add delay to respect API rate limits
                
        except Exception as e:
            print(f"Error fetching papers for author {author_id} with cursor {cursor}: {str(e)}")
            break
    
    print(f"Total papers fetched for author {author_id}: {len(all_results)}")
    return all_results

if __name__ == "__main__":
    print(json.dumps(get_article_info_by_author_id("A5071864357"), indent=4))
    
    