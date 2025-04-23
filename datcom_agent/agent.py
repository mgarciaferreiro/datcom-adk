import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


def get_dcid(place: str) -> dict:
    """Retrieves the DCID for a specified place using Data Commons API v2.
    
    Args:
        place (str): The name of the place to get DCID for.
        
    Returns:
        dict: status and dcid or error message. 
    """
    # Data Commons API v2 endpoints
    base_url = "https://api.datacommons.org/v2"
    api_key = os.getenv("DATCOM_API_KEY")
    
    try:
        # First resolve the place name to a DCID
        resolve_url = f"{base_url}/resolve"
        resolve_params = {
            "key": api_key,
            "nodes": [place],
            "property": "<-description->dcid"
        }
        
        response = requests.get(resolve_url, params=resolve_params)
        response.raise_for_status()
        
        resolve_data = response.json()
        print(resolve_data)
        if not resolve_data.get("entities"):
            return {
                "status": "error",
                "error_message": f"Could not find place data for '{place}'"
            }
            
        # Get the first DCID for the place
        dcid = resolve_data["entities"][0]["candidates"][0]["dcid"]
        
        return {
            "status": "success",
            "report": (
                f"DCID for {place}: {dcid}"
            )
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Error fetching dcid for {place}: {str(e)}"
        }


def get_available_variables(place_dcids: str) -> dict:
    """Retrieves available statistical variables for one or more entity DCIDs.
    
    Args:
        place_dcids (str): Comma-separated DCIDs of places to query.
        
    Returns:
        dict: status and available variables or error message.
              Note: Results are limited to the first 10 variables per place.
    """
    # Data Commons API v2 endpoints
    base_url = "https://api.datacommons.org/v2"
    api_key = os.getenv("DATCOM_API_KEY")
    
    # Convert comma-separated string to list
    dcid_list = [dcid.strip() for dcid in place_dcids.split(",")]
    
    try:
        # Use observation API to get available variables using GET request
        observation_url = f"{base_url}/observation"
        url = f"{observation_url}?key={api_key}&date=LATEST"
        
        # Add entity.dcids parameters, properly URL encoded
        for dcid in dcid_list:
            url += f"&entity.dcids={requests.utils.quote(dcid)}"
        url += "&select=entity&select=variable"
        
        # Make the request
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Process the results to extract available variables
        result = {}
        
        # Initialize result with empty lists for each entity
        for entity_dcid in dcid_list:
            result[entity_dcid] = []
        
        # If there's data for variables, extract them
        if "byVariable" in data:
            for variable_dcid, variable_data in data["byVariable"].items():
                if "byEntity" in variable_data:
                    for entity_dcid, entity_data in variable_data["byEntity"].items():
                        if entity_dcid in result and len(result[entity_dcid]) < 10:
                            result[entity_dcid].append(variable_dcid)
        
        # Format for human-readable output
        report = "Available variables (limited to first 10 per place):\n"
        for entity, vars in result.items():
            if vars:
                report += f"\nFor place {entity}:\n"
                for var in vars:
                    report += f"  - {var}\n"
            else:
                report += f"\nNo variables found for place {entity}\n"
        
        return {
            "status": "success",
            "report": report,
            "data": result  # Include raw data for programmatic use
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Error fetching variables for {place_dcids}: {str(e)}"
        }


def get_population_count(place_dcids: str, date: str = "LATEST") -> dict:
    """Retrieves population count (Count_Person) for one or more entity DCIDs.
    
    Args:
        place_dcids (str): Comma-separated DCIDs of places to query.
        date (str, optional): Date to query. Defaults to "LATEST".
                             Can be "LATEST" or a specific year like "2020".
        
    Returns:
        dict: status and population counts or error message.
    """
    # Data Commons API v2 endpoints
    base_url = "https://api.datacommons.org/v2"
    api_key = os.getenv("DATCOM_API_KEY")
    
    # Convert comma-separated string to list
    dcid_list = [dcid.strip() for dcid in place_dcids.split(",")]
    
    try:
        # Use observation API to get population count
        observation_url = f"{base_url}/observation"
        url = f"{observation_url}?key={api_key}&date={requests.utils.quote(date)}"
        
        # Add entity.dcids parameters, properly URL encoded
        for dcid in dcid_list:
            url += f"&entity.dcids={requests.utils.quote(dcid)}"
        
        # Add variable.dcids parameter for Count_Person
        url += f"&variable.dcids=Count_Person"
        
        # Add select parameters for entity, variable, value, and date
        url += "&select=entity&select=variable&select=value&select=date"
        
        # Make the request
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Process the results to extract population counts
        result = {}
        
        # Check if Count_Person data exists in the response
        if "byVariable" in data and "Count_Person" in data["byVariable"]:
            variable_data = data["byVariable"]["Count_Person"]
            
            if "byEntity" in variable_data:
                for entity_dcid, entity_data in variable_data["byEntity"].items():
                    if "orderedFacets" in entity_data and entity_data["orderedFacets"]:
                        # Get the most recent observation from the first facet
                        # (Different facets represent different data sources)
                        facet = entity_data["orderedFacets"][0]
                        
                        if "observations" in facet and facet["observations"]:
                            # Get the population and its date
                            obs = facet["observations"][0]
                            population = obs.get("value")
                            obs_date = obs.get("date")
                            
                            result[entity_dcid] = {
                                "population": population,
                                "date": obs_date
                            }
        
        # Format for human-readable output
        report = "Population counts:\n"
        if result:
            for entity, data in result.items():
                population = data.get("population")
                obs_date = data.get("date")
                report += f"\n{entity}: {population:,} (as of {obs_date})"
        else:
            report += "\nNo population data found for the requested places."
        
        return {
            "status": "success",
            "report": report,
            "data": result  # Include raw data for programmatic use
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Error fetching population for {place_dcids}: {str(e)}"
        }


root_agent = Agent(
    name="datcom_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about public data about places using the Data Commons API."
    ),
    instruction=(
        "You are a helpful agent who can access Data Commons to provide information about "
        "places. You can help "
        "users find data about specific cities, states, and countries by first looking up "
        "their Data Commons IDs (DCIDs), retrieving available statistics for the place, and "
        "retrieving population counts."
    ),
    tools=[get_dcid, get_available_variables, get_population_count],
)