import requests

# ✅ 使用 Semantic Scholar API 查询论文信息（通过 DOI）
def get_paper_info_dict_from_doi(doi):
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,abstract,authors,year,venue"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return {
            "title": data.get("title", "N/A"),
            "abstract": data.get("abstract", "N/A"),
            "authors": [author.get("name", "") for author in data.get("authors", [])],
            "year": data.get("year", "N/A"),
            "venue": data.get("venue", "N/A"),
        }
    except Exception as e:
        print(f"❌ Semantic Scholar DOI 查询失败: {e}")
        return None

# ✅ 使用 Semantic Scholar API 查询摘要（通过标题）
def get_paper_abstract_str_from_title(title):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={title}&fields=title,abstract&limit=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        papers = data.get("data", [])
        if papers:
            return papers[0].get("abstract", None)
        return None
    except Exception as e:
        print(f"❌ Semantic Scholar 标题查询失败: {e}")
        return None

# ✅ 测试
if __name__ == "__main__":
    doi = "10.1109/icde.2007.367924"
    paper = get_paper_info_dict_from_doi(doi)
    
    if paper:
        print("✅ 查询成功：")
        for k, v in paper.items():
            print(f"{k}: {v}")
        print(f"\n📝 摘要：{paper.get('abstract', 'No abstract available.')}")
    else:
        print("❌ Paper not found.")