import arxiv

def get_arxiv_papers(query, max_results=3):
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    return list(search.results())

query = "Ranking Outliers Using Symmetric Neighborhood Relationship"
papers = get_arxiv_papers(query)

for paper in papers:
    print(f"Title: {paper.title}")
    print(f"Abstract: {paper.summary}")
    print(f"PDF: {paper.pdf_url}")
    print("-" * 80)