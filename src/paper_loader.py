from scholarly import scholarly

def get_paper_info_dict_from_doi(doi):
    query = scholarly.search_pubs(doi)
    paper = next(query, None)

    if paper:
        return paper.get("bib", {})
    else:
        return None
    
def get_paper_abstract_str_from_title(title):
    query = scholarly.search_pubs(title)
    paper = next(query, None)

    if paper:
        return paper.get("bib", {}).get("abstract", None)
    else:
        return None
    
if __name__ == "__main__":
    doi = "10.1287/mnsc.1110.1325"
    paper = get_paper_info_dict_from_doi(doi)
    print(get_paper_abstract_str_from_title("Designing Sales Contests: Does the Prize Structure Matter?"))
    
    if paper:
        for i in paper:
            print(i, paper[i])
        
        print(paper.get("abstract", "No abstract available."))
    else:
        print("Paper not found.")