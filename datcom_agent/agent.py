import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


def get_place_dcids(places: list[str]) -> dict:
    """Retrieves the DCIDs for specified places using Data Commons API v2.
    
    Args:
        places (list[str]): List of place names to get DCIDs for.
        
    Returns:
        dict: status and dcids or error message. 
    """
    # Data Commons API v2 endpoints
    base_url = "https://api.datacommons.org/v2"
    api_key = os.getenv("DATCOM_API_KEY")
    
    try:
        # Resolve place names to DCIDs
        resolve_url = f"{base_url}/resolve"
        resolve_params = {
            "key": api_key,
            "nodes": places,
            "property": "<-description->dcid"
        }
        
        response = requests.get(resolve_url, params=resolve_params)
        response.raise_for_status()
        
        resolve_data = response.json()
        if not resolve_data.get("entities"):
            return {
                "status": "error",
                "error_message": f"Could not find place data for any of the provided places"
            }
            
        # Process results for each place
        result = {}
        report = "DCIDs for places:\n"
        
        for entity in resolve_data["entities"]:
            place_name = entity["node"]
            candidates = entity.get("candidates", [])
            
            if candidates:
                dcid = candidates[0]["dcid"]
                result[place_name] = dcid
                report += f"{place_name}: {dcid}\n"
            else:
                result[place_name] = None
                report += f"{place_name}: No DCID found\n"
        
        return {
            "status": "success",
            "report": report,
            "data": result
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Error fetching dcids: {str(e)}"
        }


def get_available_variables(place_dcids: str) -> dict:
    """Retrieves available statistical variables for one or more entity DCIDs.
    
    Args:
        place_dcids (str): Comma-separated DCIDs of places to query.
        
    Returns:
        dict: status and available variables or error message.
              Note: Results are limited to the first 30 variables per place.
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
                        if entity_dcid in result and len(result[entity_dcid]) < 30:
                            result[entity_dcid].append(variable_dcid)
        
        # Format for human-readable output
        report = "Available variables (limited to first 30 per place):\n"
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


def get_observations(place_dcids: list[str], statvar_dcids: list[str], date: str = "LATEST") -> dict:
    """Retrieves statistical observations for given places and variables using Data Commons API v2.
    
    Args:
        place_dcids (list[str]): List of DCIDs for places to query.
        statvar_dcids (list[str]): List of DCIDs for statistical variables to query.
        date (str, optional): Date to query. Defaults to "LATEST".
                             Can be "LATEST" or a specific year like "2020".
        
    Returns:
        dict: status and observations or error message.
    """
    # Data Commons API v2 endpoints
    base_url = "https://api.datacommons.org/v2"
    api_key = os.getenv("DATCOM_API_KEY")
    
    try:
        # Use observation API to get observations
        observation_url = f"{base_url}/observation"
        url = f"{observation_url}?key={api_key}&date={requests.utils.quote(date)}"
        
        # Add entity.dcids parameters, properly URL encoded
        for dcid in place_dcids:
            url += f"&entity.dcids={requests.utils.quote(dcid)}"
        
        # Add variable.dcids parameters, properly URL encoded
        for dcid in statvar_dcids:
            url += f"&variable.dcids={requests.utils.quote(dcid)}"
        
        # Add select parameters for entity, variable, value, and date
        url += "&select=entity&select=variable&select=value&select=date"
        
        # Make the request
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Process the results to extract observations
        result = {}
        
        # Check if we have any variable data in the response
        if "byVariable" in data:
            for variable_dcid, variable_data in data["byVariable"].items():
                if "byEntity" in variable_data:
                    for entity_dcid, entity_data in variable_data["byEntity"].items():
                        if "orderedFacets" in entity_data and entity_data["orderedFacets"]:
                            # Get the most recent observation from the first facet
                            # (Different facets represent different data sources)
                            facet = entity_data["orderedFacets"][0]
                            
                            if "observations" in facet and facet["observations"]:
                                # Get the value and its date
                                obs = facet["observations"][0]
                                value = obs.get("value")
                                obs_date = obs.get("date")
                                
                                # Initialize result structure if needed
                                if entity_dcid not in result:
                                    result[entity_dcid] = {}
                                
                                result[entity_dcid][variable_dcid] = {
                                    "value": value,
                                    "date": obs_date
                                }
        
        # Format for human-readable output
        report = "Observations:\n"
        if result:
            for entity, variables in result.items():
                report += f"\nFor place {entity}:\n"
                for variable, data in variables.items():
                    value = data.get("value")
                    obs_date = data.get("date")
                    report += f"  - {variable}: {value:,} (as of {obs_date})\n"
        else:
            report += "\nNo observations found for the requested places and variables."
        
        return {
            "status": "success",
            "report": report,
            "data": result  # Include raw data for programmatic use
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Error fetching observations: {str(e)}"
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
        "their Data Commons IDs (DCIDs), retrieving available statistical variables (statvars) for the place, and "
        "retrieving the observations for those variables and places."
    ),
    tools=[get_place_dcids, get_available_variables, get_observations, get_population_count],
)