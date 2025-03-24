import requests
import json

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
    url = f"https://api.openalex.org/works?filter=author.id:{author_id}&per-page=10"

    response = requests.get(url)
    data = response.json()

    result = []
    for work in data['results']:
        result.append({
            "title": work.get("title", ""),
            "doi": work.get("doi", ""),
            "openalex_id": get_id_from_openc(work.get("id", "")),
            "author_id": author_id,
            "publication_date": work.get("publication_date", ""),
            "publication_year": work.get("publication_year", ""),
            "display_name": work.get("display_name", ""),
            "abstract": decode_abstract(work.get("abstract_inverted_index", "")),
            "topics": get_topics_from_openalex(work.get("topics", "")),
        })
    return result

if __name__ == "__main__":
    print(json.dumps(get_article_info_by_author_id("A5071864357"), indent=4))
    
    