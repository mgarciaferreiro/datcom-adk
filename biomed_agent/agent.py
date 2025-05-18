from google.adk.agents import Agent
import requests
from dotenv import load_dotenv
import os
import pathlib

# Get the root directory path
root_dir = pathlib.Path(__file__).parent.parent.absolute()

# Load environment variables from root .env file
load_dotenv(dotenv_path=os.path.join(root_dir, '.env'))

# Data Commons API endpoints
BASE_URL = "https://api.datacommons.org"
API_KEY = os.getenv("DATCOM_API_KEY")

def get_entity_dcids(entities: list[str]) -> dict:
    """Retrieves the DCIDs for specified entities using Data Commons API v1 bulk find entities endpoint.
    
    The entities can be biomedical entities, places, or other entities in the Data Commons knowledge graph.
    
    Args:
        entities (list[str]): List of entity names to get DCIDs for.
        
    Returns:
        dict: status and dcids or error message. 
    """
    
    try:
        # Prepare entities data for bulk request
        # entities_data = []
        # for entity in entities:
        #     entity_data = {"description": entity}
        #     entities_data.append(entity_data)
        
        # Create request payload
        payload = {"queries": entities}
        
        # Make POST request to recognize entities endpoint
        resolve_url = f"{BASE_URL}/v1/recognize/entities"
        headers = {"X-API-Key": API_KEY}
        
        response = requests.post(resolve_url, headers=headers, json=payload)
        response.raise_for_status()
        
        resolve_data = response.json()
        # print("***")
        # print(resolve_data)
        # print("***")
            
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
            "data": result
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Error fetching DCIDs: {str(e)}"
        }


root_agent = Agent(
    name="biomed_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about biomedical topics."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about biomedical research. Note that you are a blank template "
        "and your functionality will be expanded with actual API integrations."
    ),
    tools=[get_entity_dcids],
) 