# Biomedical Agent

A blank template for creating an AI agent that can answer questions about biomedical topics.

## Overview

This agent is built on Google's ADK (Agent Development Kit) and is intended as a starting point for developing a biomedical information retrieval system. When fully implemented, the agent could:

1. **Provide basic medical information** about conditions, treatments, and drugs
2. **Search medical literature** from sources like PubMed
3. **Find clinical trials** related to specific conditions
4. **Answer general health questions** with proper citations

## Current Status

This is a blank template with placeholder functionality. The agent currently includes:

- A basic agent setup using Google's ADK
- A function for looking up DCIDs for biomedical entities and other entities using Data Commons API's bulk find endpoint
  - Supports optional entity type specification for disambiguation (e.g., "Disease", "Drug", "Country")
  - Efficiently handles multiple entity lookups in a single API call
- A placeholder function for returning information about medical conditions
- A template .env file for API credentials

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Google AI API key
- (Eventually) API keys for medical information services

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

## Extending the Agent

### API Integration Ideas

The agent could be extended to integrate with:

1. **PubMed API** - For searching medical literature
2. **ClinicalTrials.gov API** - For finding clinical trials
3. **MedlinePlus** - For general health information
4. **DrugBank** - For medication information
5. **UMLS (Unified Medical Language System)** - For standardized medical terminology

### Function Ideas

Consider implementing these functions:

1. `search_medical_literature(query)` - Search PubMed for relevant articles
2. `find_clinical_trials(condition)` - Find clinical trials for a condition
3. `get_drug_information(drug_name)` - Get information about medications
4. `translate_medical_terms(term)` - Explain complex medical terminology

## Usage

Once developed, the agent could be used by running:

```
adk web
```

## Development Status

⚠️ **IMPORTANT**: This agent is currently a blank template and does not yet provide actual biomedical information. It needs to be extended with real API integrations before it can be used for any medical purpose.

## Disclaimer

This agent is intended for informational purposes only and not as a replacement for professional medical advice, diagnosis, or treatment. 