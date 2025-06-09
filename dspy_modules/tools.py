import dspy

def search_wikipedia(query: str):
    """
    Searches Wikipedia abstracts using ColBERTv2 retrieval model.
    
    Args:
        query (str): The search query string to find relevant Wikipedia articles.
        
    Returns:
        list: A list of dictionary results where each dictionary contains:
            - text (str): The title and abstract snippet
            - pid (int): Page identifier
            - rank (int): Ranking position in search results
            - score (float): Relevance score
            - prob (float): Probability score
            - long_text (str): Full abstract text (may be identical to text)
    """
    results = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')(query, k=3)
    return [x for x in results]

if __name__ == "__main__":
    query = "Python programming language"
    results = search_wikipedia(query)
    for result in results:
        print(result)
