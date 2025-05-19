# Biomedical Agent

An AI agent that leverages the [Data Commons](https://datacommons.org/) knowledge graph to answer questions about biomedical entities, including diseases, drugs, genes, and more.

## Overview

This agent is built on Google's ADK (Agent Development Kit) and provides access to biomedical information through the Data Commons knowledge graph. The agent can:

1. **Identify biomedical entities** from user queries
2. **Retrieve DCIDs** (Data Commons IDs) for biomedical entities
3. **Access properties** of biomedical entities in the knowledge graph
4. **Search scientific literature** via PubMed for the latest research
5. **Provide browser links** to view entities in the Data Commons browser

## Current Capabilities

The agent currently includes these core functionalities:

- **Entity Recognition**: Identifies biomedical entities mentioned in queries using Data Commons' entity recognition API
- **Property Retrieval**: Fetches specific properties of biomedical entities from the knowledge graph
- **PubMed Integration**: Searches PubMed for scientific articles related to biomedical queries
- **Browser Link Generation**: Creates links to the Data Commons browser for further exploration

## Technical Details

The agent uses four main functions to interact with Data Commons and PubMed APIs:

1. `get_entity_dcids(entities)` - Recognizes entities in text and returns their DCIDs
2. `get_entity_property(dcid, propName)` - Retrieves specific properties for an entity by its DCID
3. `get_browser_link(dcids)` - Generates browser links to view entities in the Data Commons interface
4. `get_pubmed_articles(query, max_results)` - Searches PubMed for scientific articles related to a query

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Google AI API key
- Data Commons API key

### Installation

1. Make sure you have the project cloned:
   ```
   git clone https://github.com/yourusername/datcom-adk.git
   cd datcom-adk
   ```

2. Create a virtual environment if you haven't already:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Update the `.env` file in the root directory with your API keys.

## Usage

Run the following command to launch the agent:

```
adk web
```

### Example Queries

- "What's the mechanism of action of atorvastatin?"
- "What is Alzheimer's disease?"
- "Find recent research on COVID-19 treatments"
- "Show me the latest studies on diabetes management"
- "What do recent papers say about CRISPR gene editing?"

## How It Works

1. When a user asks a question about a biomedical topic, the agent identifies relevant entities using `get_entity_dcids`
2. It then retrieves properties for those entities using `get_entity_property`
3. For queries about recent research, it searches PubMed using `get_pubmed_articles`
4. The agent formulates a response based on the available information
5. Finally, it provides links to the Data Commons browser for more detailed exploration using `get_browser_link`

## Development Roadmap

The agent can be extended to include:

1. **Improved property identification and retrieval** - Identify all properties available for a given entity
2. **Enhanced entity relationship detection** - Identify relationships between biomedical entities
3. **Additional scientific databases** - Integrate with ClinicalTrials.gov, DrugBank, and other resources
4. **Full-text article retrieval** - Add capability to access full-text articles where available
5. **Citation formatting** - Format article citations in standard scientific styles (APA, MLA, etc.)

## Disclaimer

This agent is intended for informational purposes only and not as a replacement for professional medical advice, diagnosis, or treatment. The scientific literature provided through PubMed integration should be evaluated by qualified healthcare professionals.