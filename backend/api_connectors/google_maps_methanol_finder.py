#!/usr/bin/env python3
"""
Google Maps Methanol Buyer Finder
Uses Google Maps API to find chemical companies and calculate distances
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import os
from math import radians, cos, sin, asin, sqrt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MethanolBuyer:
    """Data structure for methanol buyer information from Google Maps"""
    company_name: str
    address: str
    coordinates: Tuple[float, float]
    phone: Optional[str]
    website: Optional[str]
    rating: Optional[float]
    reviews_count: Optional[int]
    business_type: str
    distance_km: float
    estimated_methanol_demand: Optional[str]
    last_updated: datetime
    data_source: str = "Google Maps API"

class GoogleMapsMethanolFinder:
    """Finder for methanol buyers using Google Maps API"""
    
    def __init__(self, api_key: str = None):
        """Initialize the Google Maps finder"""
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("Google Maps API key required. Set GOOGLE_MAPS_API_KEY environment variable.")
        
        self.session = requests.Session()
        self.base_url = "https://maps.googleapis.com/maps/api"
        
        # Cache for storing search results
        self.cache = {}
        self.cache_duration = 24 * 60 * 60  # 24 hours in seconds
    
    def _make_api_request(self, endpoint: str, params: Dict) -> Dict:
        """Make a request to Google Maps API"""
        params['key'] = self.api_key
        
        try:
            response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') != 'OK':
                logger.warning(f"Google Maps API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                return {}
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making Google Maps API request: {e}")
            return {}
    
    def search_chemical_companies(self, location: str, radius_km: int = 100) -> List[MethanolBuyer]:
        """Search for chemical companies in a specific area"""
        
        cache_key = f"chemical_companies_{location}_{radius_km}"
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_duration:
                logger.info(f"Using cached chemical companies data for {location}")
                return cache_data
        
        logger.info(f"Searching for chemical companies in {location} within {radius_km}km")
        
        # Search queries for chemical companies
        search_queries = [
            "chemical company",
            "industrial chemicals",
            "chemical manufacturing",
            "formaldehyde production",
            "acetic acid manufacturer",
            "methanol supplier",
            "industrial facility",
            "manufacturing plant",
            "chemical industrial park"
        ]
        
        all_companies = []
        
        for query in search_queries:
            # First, get coordinates for the location
            geocode_data = self._make_api_request("geocode/json", {
                'address': location,
                'components': 'country:DE'  # Focus on Germany
            })
            
            if not geocode_data.get('results'):
                continue
            
            location_coords = geocode_data['results'][0]['geometry']['location']
            lat, lng = location_coords['lat'], location_coords['lng']
            
            # Search for businesses
            places_data = self._make_api_request("place/nearbysearch/json", {
                'location': f"{lat},{lng}",
                'radius': radius_km * 1000,  # Convert to meters
                'keyword': query,
                'type': 'establishment'
            })
            
            if not places_data.get('results'):
                continue
            
            # Process each company found
            for place in places_data['results']:
                company = self._process_place_result(place, (lat, lng), query)
                if company:
                    all_companies.append(company)
            
            # Rate limiting - Google allows 100 requests per 100 seconds
            time.sleep(0.1)
        
        # Remove duplicates and sort by distance
        unique_companies = self._remove_duplicates(all_companies)
        unique_companies.sort(key=lambda x: x.distance_km)
        
        # Cache the results
        self.cache[cache_key] = (time.time(), unique_companies)
        
        return unique_companies
    
    def _process_place_result(self, place: Dict, origin_coords: Tuple[float, float], search_query: str) -> Optional[MethanolBuyer]:
        """Process a place result from Google Maps API"""
        
        try:
            # Get detailed place information
            place_id = place['place_id']
            details_data = self._make_api_request("place/details/json", {
                'place_id': place_id,
                'fields': 'name,formatted_address,geometry,formatted_phone_number,website,rating,user_ratings_total,types,business_status'
            })
            
            if not details_data.get('result'):
                return None
            
            details = details_data['result']
            
            # Calculate distance
            company_coords = (
                details['geometry']['location']['lat'],
                details['geometry']['location']['lng']
            )
            distance_km = self._calculate_distance(origin_coords, company_coords)
            
            # Determine business type and estimated methanol demand
            business_type, methanol_demand = self._classify_business(details, search_query)
            
            # Create MethanolBuyer object
            buyer = MethanolBuyer(
                company_name=details.get('name', 'Unknown'),
                address=details.get('formatted_address', 'Address not available'),
                coordinates=company_coords,
                phone=details.get('formatted_phone_number'),
                website=details.get('website'),
                rating=details.get('rating'),
                reviews_count=details.get('user_ratings_total'),
                business_type=business_type,
                distance_km=round(distance_km, 1),
                estimated_methanol_demand=methanol_demand,
                last_updated=datetime.now()
            )
            
            return buyer
            
        except Exception as e:
            logger.error(f"Error processing place result: {e}")
            return None
    
    def _classify_business(self, details: Dict, search_query: str) -> Tuple[str, str]:
        """Classify business type and estimate methanol demand"""
        
        types = details.get('types', [])
        name = details.get('name', '').lower()
        
        # High methanol demand businesses
        if any(keyword in name for keyword in ['basf', 'bayer', 'evonik', 'covestro', 'celanese']):
            return "Major Chemical Company", "High (500-1000 kt/year)"
        
        if any(keyword in name for keyword in ['formaldehyde', 'acetic acid', 'methanol']):
            return "Methanol-Dependent Manufacturer", "High (200-500 kt/year)"
        
        if 'chemical' in name or 'chemical' in search_query:
            return "Chemical Company", "Medium (50-200 kt/year)"
        
        if 'manufacturing' in name or 'manufacturing' in search_query:
            return "Manufacturing Facility", "Medium (20-100 kt/year)"
        
        if 'industrial' in name or 'industrial' in search_query:
            return "Industrial Facility", "Low-Medium (10-50 kt/year)"
        
        return "General Business", "Unknown"
    
    def _calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Earth's radius in kilometers
        R = 6371
        
        return R * c
    
    def _remove_duplicates(self, companies: List[MethanolBuyer]) -> List[MethanolBuyer]:
        """Remove duplicate companies based on name and coordinates"""
        
        seen = set()
        unique_companies = []
        
        for company in companies:
            # Create a unique identifier
            identifier = f"{company.company_name}_{company.coordinates[0]:.3f}_{company.coordinates[1]:.3f}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique_companies.append(company)
        
        return unique_companies
    
    def get_route_info(self, origin: Tuple[float, float], destination: Tuple[float, float], 
                       transport_mode: str = 'driving') -> Dict:
        """Get route information between two points"""
        
        cache_key = f"route_{origin}_{destination}_{transport_mode}"
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_duration:
                return cache_data
        
        # Get directions
        directions_data = self._make_api_request("directions/json", {
            'origin': f"{origin[0]},{origin[1]}",
            'destination': f"{destination[0]},{destination[1]}",
            'mode': transport_mode,
            'units': 'metric'
        })
        
        if not directions_data.get('routes'):
            return {}
        
        route = directions_data['routes'][0]
        leg = route['legs'][0]
        
        route_info = {
            'distance_km': leg['distance']['value'] / 1000,
            'duration_minutes': leg['duration']['value'] / 60,
            'transport_mode': transport_mode,
            'steps': [step['html_instructions'] for step in leg['steps']],
            'polyline': route['overview_polyline']['points']
        }
        
        # Cache the results
        self.cache[cache_key] = (time.time(), route_info)
        
        return route_info
    
    def find_methanol_buyers_near_site(self, site_coordinates: Tuple[float, float], 
                                      search_radius_km: int = 100) -> List[MethanolBuyer]:
        """Find methanol buyers near a specific site"""
        
        # Convert coordinates to address for search
        reverse_geocode_data = self._make_api_request("geocode/json", {
            'latlng': f"{site_coordinates[0]},{site_coordinates[1]}",
            'result_type': 'locality'
        })
        
        if not reverse_geocode_data.get('results'):
            logger.warning("Could not reverse geocode site coordinates")
            return []
        
        location_name = reverse_geocode_data['results'][0]['formatted_address']
        
        # Search for chemical companies in the area
        companies = self.search_chemical_companies(location_name, search_radius_km)
        
        # Filter for companies that are likely methanol buyers
        methanol_buyers = []
        for company in companies:
            if any(keyword in company.business_type.lower() for keyword in 
                   ['chemical', 'manufacturing', 'industrial']):
                methanol_buyers.append(company)
        
        return methanol_buyers
    
    def export_buyer_data(self, buyers: List[MethanolBuyer], format: str = 'excel') -> str:
        """Export buyer data in specified format"""
        
        if format.lower() == 'json':
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'google_maps_methanol_buyers_{timestamp}.json'
            
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'total_buyers': len(buyers),
                'buyers': [
                    {
                        'company_name': b.company_name,
                        'address': b.address,
                        'coordinates': b.coordinates,
                        'phone': b.phone,
                        'website': b.website,
                        'rating': b.rating,
                        'reviews_count': b.reviews_count,
                        'business_type': b.business_type,
                        'distance_km': b.distance_km,
                        'estimated_methanol_demand': b.estimated_methanol_demand,
                        'data_source': b.data_source
                    } for b in buyers
                ]
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Exported Google Maps methanol buyer data to {filename}")
            return filename
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_business_insights(self, buyers: List[MethanolBuyer]) -> Dict:
        """Generate insights from the buyer data"""
        
        if not buyers:
            return {}
        
        total_buyers = len(buyers)
        avg_distance = sum(b.distance_km for b in buyers) / total_buyers
        avg_rating = sum(b.rating or 0 for b in buyers) / sum(1 for b in buyers if b.rating)
        
        # Distance distribution
        distance_ranges = {
            '0-25 km': len([b for b in buyers if b.distance_km <= 25]),
            '25-50 km': len([b for b in buyers if 25 < b.distance_km <= 50]),
            '50-100 km': len([b for b in buyers if 50 < b.distance_km <= 100]),
            '100+ km': len([b for b in buyers if b.distance_km > 100])
        }
        
        # Business type distribution
        business_types = {}
        for buyer in buyers:
            business_types[buyer.business_type] = business_types.get(buyer.business_type, 0) + 1
        
        # Demand estimation
        total_estimated_demand = 0
        for buyer in buyers:
            if buyer.estimated_methanol_demand:
                if 'High' in buyer.estimated_methanol_demand:
                    total_estimated_demand += 500
                elif 'Medium' in buyer.estimated_methanol_demand:
                    total_estimated_demand += 100
                elif 'Low' in buyer.estimated_methanol_demand:
                    total_estimated_demand += 25
        
        return {
            'total_buyers': total_buyers,
            'average_distance_km': round(avg_distance, 1),
            'average_rating': round(avg_rating, 1) if avg_rating > 0 else None,
            'distance_distribution': distance_ranges,
            'business_type_distribution': business_types,
            'total_estimated_demand_kt': total_estimated_demand,
            'search_radius_km': max(b.distance_km for b in buyers) if buyers else 0
        }

def main():
    """Test the Google Maps methanol finder"""
    
    # You need to set your Google Maps API key
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("❌ Please set GOOGLE_MAPS_API_KEY environment variable")
        print("Get your API key from: https://console.cloud.google.com/apis/credentials")
        return
    
    finder = GoogleMapsMethanolFinder(api_key)
    
    print("🗺️ Google Maps Methanol Buyer Finder Test")
    print("=" * 50)
    
    # Test coordinates (example: Ruhr Valley, Germany)
    test_site = (51.4556, 7.0117)  # Essen, Germany
    
    print(f"\n1. Searching for methanol buyers near coordinates: {test_site}")
    print("   (Essen, Ruhr Valley - major chemical industry area)")
    
    try:
        buyers = finder.find_methanol_buyers_near_site(test_site, search_radius_km=50)
        
        if buyers:
            print(f"\n✅ Found {len(buyers)} potential methanol buyers!")
            
            # Show top 5 closest buyers
            print("\n2. Top 5 Closest Buyers:")
            for i, buyer in enumerate(buyers[:5], 1):
                print(f"   {i}. {buyer.company_name}")
                print(f"      📍 {buyer.address}")
                print(f"      🚗 {buyer.distance_km} km away")
                print(f"      🏭 {buyer.business_type}")
                print(f"      📊 Estimated demand: {buyer.estimated_methanol_demand}")
                if buyer.rating:
                    print(f"      ⭐ Rating: {buyer.rating}/5 ({buyer.reviews_count} reviews)")
                print()
            
            # Generate insights
            print("3. Business Insights:")
            insights = finder.get_business_insights(buyers)
            for key, value in insights.items():
                if key not in ['distance_distribution', 'business_type_distribution']:
                    print(f"   • {key.replace('_', ' ').title()}: {value}")
            
            # Export data
            print("\n4. Exporting Data:")
            json_file = finder.export_buyer_data(buyers, 'json')
            print(f"   • JSON file: {json_file}")
            
        else:
            print("❌ No methanol buyers found in the area")
            print("   This might be due to:")
            print("   • Limited chemical industry in the area")
            print("   • API rate limiting")
            print("   • Search radius too small")
    
    except Exception as e:
        print(f"❌ Error during search: {e}")
        print("   Common issues:")
        print("   • Invalid API key")
        print("   • API quota exceeded")
        print("   • Network connectivity issues")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()
