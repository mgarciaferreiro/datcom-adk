from google.adk.agents import Agent
import requests
from dotenv import load_dotenv
import os
import pathlib
from urllib.parse import quote

# Get the root directory path
root_dir = pathlib.Path(__file__).parent.parent.absolute()

# Load environment variables from root .env file
load_dotenv(dotenv_path=os.path.join(root_dir, '.env'))

# Data Commons API endpoints
BASE_URL = "https://api.datacommons.org"
API_KEY = os.getenv("DATCOM_API_KEY")

# PubMed API endpoints
PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def get_pubmed_articles(query: str, max_results: int = 5) -> dict:
    """Retrieves scientific articles from PubMed related to the given query.
    
    Args:
        query (str): The search query for PubMed (e.g., "Alzheimer's disease treatment").
        max_results (int, optional): Maximum number of results to return. Defaults to 5.
        
    Returns:
        dict: Status and article data including titles, links, and abstracts.
    """
    try:
        # Step 1: Search for article IDs using the esearch endpoint
        search_url = f"{PUBMED_BASE_URL}/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": max_results,
            "sort": "relevance"
        }
        
        search_response = requests.get(search_url, params=search_params)
        search_response.raise_for_status()
        search_data = search_response.json()
        
        # Extract the PMIDs (PubMed IDs) from the search results
        pmids = search_data.get("esearchresult", {}).get("idlist", [])
        
        if not pmids:
            return {
                "status": "success",
                "result": f"No PubMed articles found for query: {query}",
                "articles": []
            }
        
        # Step 2: Fetch article details using the efetch endpoint
        fetch_url = f"{PUBMED_BASE_URL}/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "rettype": "abstract"
        }
        
        fetch_response = requests.get(fetch_url, params=fetch_params)
        fetch_response.raise_for_status()
        xml_content = fetch_response.text
        
        # Step 3: Parse the XML content to extract article details
        # Note: XML parsing is complex, so we'll use a simplified approach
        # For production use, consider using a proper XML parser
        
        # Simple extraction using string operations (not ideal but functional)
        articles = []
        xml_articles = xml_content.split("<PubmedArticle>")[1:]  # Skip the first split which is header
        
        for xml_article in xml_articles[:max_results]:
            # Extract PMID
            pmid_start = xml_article.find("<PMID Version=")
            pmid_end = xml_article.find("</PMID>", pmid_start)
            pmid = xml_article[pmid_start:pmid_end].split(">")[1] if pmid_start != -1 else "Unknown"
            
            # Extract title
            title_start = xml_article.find("<ArticleTitle>")
            title_end = xml_article.find("</ArticleTitle>", title_start)
            title = xml_article[title_start + 14:title_end] if title_start != -1 else "Unknown Title"
            
            # Extract abstract
            abstract_start = xml_article.find("<AbstractText")
            if abstract_start != -1:
                abstract_close_tag = xml_article.find(">", abstract_start)
                abstract_end = xml_article.find("</AbstractText>", abstract_close_tag)
                abstract = xml_article[abstract_close_tag + 1:abstract_end] if abstract_end != -1 else "No abstract available"
            else:
                abstract = "No abstract available"
            
            # Create PubMed URL
            pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            
            articles.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "url": pubmed_url
            })
        
        # Format the results for display
        report = f"Found {len(articles)} articles related to '{query}':\n\n"
        
        for i, article in enumerate(articles, 1):
            report += f"{i}. {article['title']}\n"
            report += f"   URL: {article['url']}\n"
            report += f"   Abstract: {article['abstract'][:200]}...\n\n"
        
        return {
            "status": "success",
            "result": report,
            "articles": articles
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Error fetching PubMed articles: {str(e)}"
        }

def get_entity_dcids(entities: list[str]) -> dict:
    """Retrieves the DCIDs for specified entities using Data Commons API v1 bulk find entities endpoint.
    
    The entities can be biomedical entities, places, or other entities in the Data Commons knowledge graph.
    
    Args:
        entities (list[str]): List of entity names to get DCIDs for.
        
    Returns:
        dict: status and dcids or error message. 
    """
    
    try:
        # Create request payload
        payload = {"queries": entities}
        
        # Make POST request to recognize entities endpoint
        resolve_url = f"{BASE_URL}/v1/recognize/entities"
        headers = {"X-API-Key": API_KEY}
        
        response = requests.post(resolve_url, headers=headers, json=payload)
        response.raise_for_status()
        
        resolve_data = response.json()
        
        # Process results for each entity
        result = {}
        report = "DCIDs for entities:\n"
        
        for query in resolve_data.get("queryItems", []):
            for item in resolve_data["queryItems"][query].get('items', []):
                dcids = []
                entity_name = item["span"]
                for entity in item.get("entities", []):
                    if 'dcid' in entity:
                        dcids.append(entity['dcid'])
                
                result[entity_name] = dcids
                report += f"{entity_name}: {dcids}\n"
            
        return {
            "status": "success",
            "report": report,
            "result": result
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Error fetching DCIDs: {str(e)}"
        }

def get_browser_link(dcids: list[str]) -> dict:
    """Retrieves the browser link for specified DCIDs.
    
    Args:
        dcids (list[str]): List of DCIDs to get browser link for.

    Returns:
        dict: status and links.
        
    """
    result = "Links:\n"
    for dcid in dcids:
        result += f"https://datacommons.org/browser/{dcid}\n"
    return {
            "status": "success",
            "result": result
        }

def get_entity_property(dcid: str, propName: str) -> dict:
    """Retrieves the properties for specified DCID.
    
    Args:
        dcid (str): DCID to get properties for.
        propName (str): Property name to get.
        
    Returns:
        dict: status and property value.
    """
    try:
        url = f"{BASE_URL}/v2/node?key={API_KEY}&nodes={dcid}&property=-%3E{propName}"
        response = requests.get(url).json()
        value = response.get("data", {})
        return {
            "status": "success",
            "result": value
        }
    
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Error fetching property: {str(e)}"
        }

root_agent = Agent(
    name="biomed_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about biomedical topics."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about biomedical research. For each question, identify what entities are being asked about, find what properties are available for those entities, and then use the available properties to answer the question. Then, search for scientific articles on PubMed to provide the latest research information. Finally, ALWAYS return all the browser links and PubMed links that you used to answer the question at the end .\n" +
        "Capitalize the start of sentences as appropriate, even when it's an entity name"
    ),
    tools=[get_entity_dcids, get_entity_property, get_browser_link, get_pubmed_articles],
)