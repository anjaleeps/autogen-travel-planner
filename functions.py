import os
from serpapi import GoogleSearch
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

SEARCH_GOOGLE_MAPS_SCHEMA = {
    "name": "search_google_maps",
    "description": "Search google maps using Google Maps API",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A concise search query for searching places on Google Maps"
            }
        },
        "required": ["query"]
    }
}


def search_google_maps(query):
    params = {
        "engine": "google_maps",
        "q": query,
        "type": "search",
        "api_key": os.getenv("SERP_API_KEY")
    }

    results = _search(params)
    results = results["local_results"]
    top_results = results[:10] if len(results) > 10 else results
    data = []
    for place in top_results:
        data.append(_populate_place_data(place["place_id"]))
    return data


def _populate_place_data(place_id: str):
    params = {
        "engine": "google_maps",
        "type": "place",
        "place_id": place_id,
        "api_key": os.getenv("SERP_API_KEY")
    }

    data = _search(params)
    return _prepare_place_data(data["place_results"])


def _prepare_place_data(place: Dict):
    return {
        "name": place.get("title"),
        "rating": place.get("rating"),
        "price": place.get("price"),
        "type": place.get("type"),
        "address": place.get("address"),
        "phone": place.get("phone"),
        "website": place.get("website"),
        "description": place.get("description"),
        "operating_hours": place.get("operating_hours"),
        "amenities": place.get("amenities"),
        "service_options": place.get("service_options")
    }


def _search(params: Dict[str, str]):
    search = GoogleSearch(params)
    results = search.get_dict()
    return results
