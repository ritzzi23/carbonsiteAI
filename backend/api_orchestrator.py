"""
API Orchestrator for CarbonSiteAI
Coordinates real-time data collection from multiple sources and provides unified interface
"""

import asyncio
import concurrent.futures
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np

# Import our API connectors
from api_connectors.industrial_data_api import IndustrialDataConnector, FacilityData
from api_connectors.energy_data_api import EnergyDataConnector, EnergyPriceData, RenewableEnergyData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIOrchestrator:
    """Main orchestrator for real-time API data collection"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        
        # Initialize API connectors
        self.industrial_connector = IndustrialDataConnector(api_keys)
        self.energy_connector = EnergyDataConnector(api_keys)
        
        # Data cache for performance
        self.data_cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
        
        # Rate limiting and throttling
        self.request_counts = {}
        self.max_requests_per_minute = 60
        
        logger.info("API Orchestrator initialized")
    
    def collect_real_time_data(self, 
                              target_regions: List[str] = None,
                              facility_ids: List[str] = None,
                              include_forecasts: bool = True) -> Dict[str, Any]:
        """Collect real-time data from all available sources"""
        
        logger.info("Starting real-time data collection...")
        
        # Set default regions if none specified
        if not target_regions:
            target_regions = ['Central Europe', 'Western Europe', 'Southern Europe']
        
        # Initialize results container
        real_time_data = {
            'timestamp': datetime.now().isoformat(),
            'data_sources': [],
            'industrial_data': {},
            'energy_data': {},
            'market_forecasts': {},
            'data_quality': {},
            'collection_errors': []
        }
        
        try:
            # Collect industrial facility data
            logger.info("Collecting industrial facility data...")
            industrial_data = self._collect_industrial_data(target_regions, facility_ids)
            real_time_data['industrial_data'] = industrial_data
            
            # Collect energy market data
            logger.info("Collecting energy market data...")
            energy_data = self._collect_energy_data(target_regions)
            real_time_data['energy_data'] = energy_data
            
            # Generate market forecasts if requested
            if include_forecasts:
                logger.info("Generating market forecasts...")
                forecasts = self._generate_market_forecasts(target_regions)
                real_time_data['market_forecasts'] = forecasts
            
            # Assess data quality
            real_time_data['data_quality'] = self._assess_data_quality(real_time_data)
            
            # Update data sources
            real_time_data['data_sources'] = [
                'EPA Facility Registry Service',
                'European Environment Agency',
                'ENTSO-E Transparency Platform',
                'European Power Exchanges',
                'Renewables.ninja',
                'Real-time market data'
            ]
            
            logger.info("Real-time data collection completed successfully")
            return real_time_data
            
        except Exception as e:
            error_msg = f"Error in real-time data collection: {str(e)}"
            logger.error(error_msg)
            real_time_data['collection_errors'].append(error_msg)
            return real_time_data
    
    def _collect_industrial_data(self, 
                                regions: List[str], 
                                facility_ids: List[str] = None) -> Dict[str, Any]:
        """Collect industrial facility and emissions data"""
        
        industrial_data = {
            'facilities': [],
            'regional_summaries': {},
            'co2_emissions_summary': {},
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            # Get European industrial data
            eu_facilities = self.industrial_connector.get_european_industrial_data()
            
            # Get EPA facility data for comparison
            us_facilities = self.industrial_connector.get_epa_facility_data(limit=50)
            
            # Combine and filter facilities
            all_facilities = eu_facilities + us_facilities
            
            # Filter by regions if specified
            if regions:
                all_facilities = [f for f in all_facilities if f.region in regions]
            
            # Filter by specific facility IDs if provided
            if facility_ids:
                all_facilities = [f for f in all_facilities if f.facility_id in facility_ids]
            
            # Get real-time CO₂ data for facilities
            facility_ids_list = [f.facility_id for f in all_facilities]
            real_time_co2 = self.industrial_connector.get_real_time_co2_data(
                facility_ids=facility_ids_list,
                regions=regions
            )
            
            # Process and enrich facility data
            for facility in all_facilities:
                facility_dict = {
                    'facility_id': facility.facility_id,
                    'name': facility.name,
                    'country': facility.country,
                    'region': facility.region,
                    'coordinates': {'lat': facility.latitude, 'lon': facility.longitude},
                    'industry_type': facility.industry_type,
                    'co2_emissions_tpy': facility.co2_emissions_tpy,
                    'co2_concentration': facility.co2_concentration,
                    'co2_impurities': facility.co2_impurities,
                    'power_consumption_mwh': facility.power_consumption_mwh,
                    'renewable_energy_share': facility.renewable_energy_share,
                    'last_updated': facility.last_updated.isoformat(),
                    'data_source': facility.data_source
                }
                
                # Add real-time CO₂ data if available
                if facility.facility_id in real_time_co2.get('facilities', {}):
                    real_time_info = real_time_co2['facilities'][facility.facility_id]
                    facility_dict['real_time_co2_tph'] = real_time_info.get('current_co2_emissions_tph', 0)
                    facility_dict['real_time_power_mw'] = real_time_info.get('power_consumption_mw', 0)
                    facility_dict['data_quality'] = real_time_info.get('data_quality', 'Medium')
                
                industrial_data['facilities'].append(facility_dict)
            
            # Generate regional summaries
            for region in regions:
                region_facilities = [f for f in all_facilities if f.region == region]
                if region_facilities:
                    industrial_data['regional_summaries'][region] = {
                        'total_facilities': len(region_facilities),
                        'total_co2_emissions_tpy': sum(f.co2_emissions_tpy for f in region_facilities),
                        'average_co2_concentration': np.mean([f.co2_concentration for f in region_facilities]),
                        'average_renewable_share': np.mean([f.renewable_energy_share for f in region_facilities]),
                        'industry_breakdown': self._get_industry_breakdown(region_facilities)
                    }
            
            # Generate CO₂ emissions summary
            if all_facilities:
                industrial_data['co2_emissions_summary'] = {
                    'total_facilities': len(all_facilities),
                    'total_co2_emissions_tpy': sum(f.co2_emissions_tpy for f in all_facilities),
                    'average_co2_concentration': np.mean([f.co2_concentration for f in all_facilities]),
                    'emissions_by_industry': self._get_emissions_by_industry(all_facilities),
                    'emissions_by_country': self._get_emissions_by_country(all_facilities)
                }
            
            logger.info(f"Collected industrial data for {len(all_facilities)} facilities")
            
        except Exception as e:
            logger.error(f"Error collecting industrial data: {e}")
            industrial_data['collection_error'] = str(e)
        
        return industrial_data
    
    def _collect_energy_data(self, regions: List[str]) -> Dict[str, Any]:
        """Collect energy market and renewable energy data"""
        
        energy_data = {
            'power_prices': [],
            'renewable_generation': [],
            'regional_summaries': {},
            'market_indicators': {},
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            # Get power prices for each region
            for region in regions:
                # Map region to country for API calls
                country = self._get_primary_country_for_region(region)
                
                if country:
                    # Get EU power prices
                    power_prices = self.energy_connector.get_eu_power_prices(country=country)
                    
                    # Get renewable energy data for region center
                    region_center = self._get_region_center(region)
                    if region_center:
                        renewable_data = self.energy_connector.get_renewable_energy_data(
                            region_center['lat'], region_center['lon']
                        )
                        
                        energy_data['renewable_generation'].append({
                            'region': region,
                            'country': country,
                            'solar_generation_mw': renewable_data.solar_generation_mw,
                            'wind_generation_mw': renewable_data.wind_generation_mw,
                            'hydro_generation_mw': renewable_data.hydro_generation_mw,
                            'biomass_generation_mw': renewable_data.biomass_generation_mw,
                            'total_renewable_mw': renewable_data.total_renewable_mw,
                            'total_generation_mw': renewable_data.total_generation_mw,
                            'renewable_percentage': renewable_data.renewable_percentage,
                            'timestamp': renewable_data.timestamp.isoformat(),
                            'data_source': renewable_data.data_source
                        })
                    
                    # Add power prices to collection
                    for price in power_prices:
                        energy_data['power_prices'].append({
                            'region': region,
                            'country': country,
                            'timestamp': price.timestamp.isoformat(),
                            'power_price_eur_mwh': price.power_price_eur_mwh,
                            'power_price_usd_mwh': price.power_price_usd_mwh,
                            'renewable_energy_share': price.renewable_energy_share,
                            'grid_capacity_mw': price.grid_capacity_mw,
                            'demand_mw': price.demand_mw,
                            'supply_mw': price.supply_mw,
                            'carbon_intensity_gco2_kwh': price.carbon_intensity_gco2_kwh,
                            'data_source': price.data_source
                        })
            
            # Get real-time energy prices
            real_time_prices = self.energy_connector.get_real_time_energy_prices(regions)
            energy_data['real_time_prices'] = real_time_prices
            
            # Generate regional summaries
            for region in regions:
                region_prices = [p for p in energy_data['power_prices'] if p['region'] == region]
                if region_prices:
                    energy_data['regional_summaries'][region] = {
                        'current_price_eur_mwh': region_prices[-1]['power_price_eur_mwh'],
                        'average_price_eur_mwh': np.mean([p['power_price_eur_mwh'] for p in region_prices]),
                        'price_volatility': np.std([p['power_price_eur_mwh'] for p in region_prices]),
                        'average_renewable_share': np.mean([p['renewable_energy_share'] for p in region_prices]),
                        'average_demand_mw': np.mean([p['demand_mw'] for p in region_prices]),
                        'data_points': len(region_prices)
                    }
            
            # Generate market indicators
            if energy_data['power_prices']:
                all_prices = [p['power_price_eur_mwh'] for p in energy_data['power_prices']]
                energy_data['market_indicators'] = {
                    'eu_average_price_eur_mwh': np.mean(all_prices),
                    'eu_price_range_eur_mwh': {'min': min(all_prices), 'max': max(all_prices)},
                    'eu_price_volatility': np.std(all_prices),
                    'total_data_points': len(energy_data['power_prices']),
                    'regions_covered': len(energy_data['regional_summaries'])
                }
            
            logger.info(f"Collected energy data for {len(regions)} regions")
            
        except Exception as e:
            logger.error(f"Error collecting energy data: {e}")
            energy_data['collection_error'] = str(e)
        
        return energy_data
    
    def _generate_market_forecasts(self, regions: List[str]) -> Dict[str, Any]:
        """Generate market forecasts for energy and CO₂ markets"""
        
        forecasts = {
            'energy_market': {},
            'co2_market': {},
            'renewable_energy': {},
            'generation_time': datetime.now().isoformat()
        }
        
        try:
            # Generate energy market forecasts
            for region in regions:
                energy_forecast = self.energy_connector.get_energy_market_forecast(region, 24)
                if energy_forecast:
                    forecasts['energy_market'][region] = energy_forecast
            
            # Generate CO₂ market forecasts
            for region in regions:
                co2_forecast = self._generate_co2_market_forecast(region)
                if co2_forecast:
                    forecasts['co2_market'][region] = co2_forecast
            
            # Generate renewable energy forecasts
            for region in regions:
                renewable_forecast = self._generate_renewable_forecast(region)
                if renewable_forecast:
                    forecasts['renewable_energy'][region] = renewable_forecast
            
            logger.info(f"Generated market forecasts for {len(regions)} regions")
            
        except Exception as e:
            logger.error(f"Error generating market forecasts: {e}")
            forecasts['generation_error'] = str(e)
        
        return forecasts
    
    def _generate_co2_market_forecast(self, region: str) -> Dict[str, Any]:
        """Generate CO₂ market forecast for a region"""
        
        try:
            # Simulate CO₂ market forecasting
            current_hour = datetime.now().hour
            
            forecast_data = {
                'region': region,
                'forecast_hours': 24,
                'timestamp': datetime.now().isoformat(),
                'hourly_forecasts': []
            }
            
            # Generate hourly CO₂ price forecasts
            for hour in range(24):
                forecast_hour = (current_hour + hour) % 24
                
                # Base CO₂ price varies by region
                base_prices = {
                    'Central Europe': 85.0,
                    'Western Europe': 88.0,
                    'Southern Europe': 84.0,
                    'Northern Europe': 82.0,
                    'Eastern Europe': 86.0
                }
                
                base_price = base_prices.get(region, 85.0)
                
                # Simulate price variations
                time_factor = 1.0 + 0.1 * np.sin(2 * np.pi * forecast_hour / 24)
                market_factor = 1.0 + np.random.normal(0, 0.05)
                
                forecast_price = base_price * time_factor * market_factor
                forecast_price = max(60, min(120, forecast_price))  # Clamp between €60-120/ton
                
                hourly_forecast = {
                    'hour': forecast_hour,
                    'co2_price_eur_ton': round(forecast_price, 2),
                    'demand_factor': 0.8 + 0.4 * np.sin(2 * np.pi * forecast_hour / 24) + np.random.normal(0, 0.1),
                    'supply_factor': 1.0 + 0.2 * np.cos(2 * np.pi * forecast_hour / 24) + np.random.normal(0, 0.1)
                }
                
                forecast_data['hourly_forecasts'].append(hourly_forecast)
            
            return forecast_data
            
        except Exception as e:
            logger.warning(f"Error generating CO₂ forecast for {region}: {e}")
            return None
    
    def _generate_renewable_forecast(self, region: str) -> Dict[str, Any]:
        """Generate renewable energy forecast for a region"""
        
        try:
            # Simulate renewable energy forecasting
            current_hour = datetime.now().hour
            
            forecast_data = {
                'region': region,
                'forecast_hours': 24,
                'timestamp': datetime.now().isoformat(),
                'hourly_forecasts': []
            }
            
            # Generate hourly renewable forecasts
            for hour in range(24):
                forecast_hour = (current_hour + hour) % 24
                
                # Solar generation (peak at noon)
                solar_factor = max(0, np.sin(np.pi * (forecast_hour - 6) / 12)) if 6 <= forecast_hour <= 18 else 0
                solar_generation = 1000 * solar_factor + np.random.normal(0, 50)
                
                # Wind generation (more variable)
                wind_base = 800
                wind_factor = 0.5 + 0.5 * np.sin(2 * np.pi * forecast_hour / 24) + np.random.normal(0, 0.2)
                wind_generation = wind_base * wind_factor
                
                # Hydro and biomass (stable)
                hydro_generation = 600 + np.random.normal(0, 100)
                biomass_generation = 400 + np.random.normal(0, 50)
                
                total_renewable = max(0, solar_generation + wind_generation + hydro_generation + biomass_generation)
                
                hourly_forecast = {
                    'hour': forecast_hour,
                    'solar_mw': max(0, solar_generation),
                    'wind_mw': max(0, wind_generation),
                    'hydro_mw': max(0, hydro_generation),
                    'biomass_mw': max(0, biomass_generation),
                    'total_renewable_mw': total_renewable,
                    'renewable_percentage': round((total_renewable / (total_renewable + 2000)) * 100, 1)
                }
                
                forecast_data['hourly_forecasts'].append(hourly_forecast)
            
            return forecast_data
            
        except Exception as e:
            logger.warning(f"Error generating renewable forecast for {region}: {e}")
            return None
    
    def _assess_data_quality(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality and reliability of collected data"""
        
        data_quality = {
            'overall_score': 0,
            'completeness': {},
            'freshness': {},
            'consistency': {},
            'reliability': {},
            'recommendations': []
        }
        
        try:
            # Assess industrial data quality
            industrial_data = collected_data.get('industrial_data', {})
            if industrial_data:
                facilities = industrial_data.get('facilities', [])
                if facilities:
                    # Completeness
                    completeness_score = self._calculate_completeness_score(facilities)
                    data_quality['completeness']['industrial'] = completeness_score
                    
                    # Freshness
                    freshness_score = self._calculate_freshness_score(facilities)
                    data_quality['freshness']['industrial'] = freshness_score
                    
                    # Consistency
                    consistency_score = self._calculate_consistency_score(facilities)
                    data_quality['consistency']['industrial'] = consistency_score
            
            # Assess energy data quality
            energy_data = collected_data.get('energy_data', {})
            if energy_data:
                power_prices = energy_data.get('power_prices', [])
                if power_prices:
                    # Completeness
                    completeness_score = self._calculate_completeness_score(power_prices)
                    data_quality['completeness']['energy'] = completeness_score
                    
                    # Freshness
                    freshness_score = self._calculate_freshness_score(power_prices)
                    data_quality['freshness']['energy'] = freshness_score
            
            # Calculate overall quality score
            scores = []
            for category in ['completeness', 'freshness', 'consistency']:
                if category in data_quality and isinstance(data_quality[category], dict):
                    category_scores = data_quality[category].values()
                    if category_scores:
                        scores.extend(category_scores)
            
            if scores:
                data_quality['overall_score'] = round(np.mean(scores), 1)
            else:
                data_quality['overall_score'] = 0
            
            # Generate recommendations
            data_quality['recommendations'] = self._generate_quality_recommendations(data_quality)
            
        except Exception as e:
            logger.error(f"Error assessing data quality: {e}")
            data_quality['assessment_error'] = str(e)
        
        return data_quality
    
    def _calculate_completeness_score(self, data_items: List[Dict]) -> float:
        """Calculate completeness score for data items"""
        
        if not data_items:
            return 0.0
        
        required_fields = ['timestamp', 'data_source']
        optional_fields = ['coordinates', 'last_updated']
        
        completeness_scores = []
        
        for item in data_items:
            # Check required fields
            required_score = sum(1 for field in required_fields if field in item and item[field]) / len(required_fields)
            
            # Check optional fields
            optional_score = sum(1 for field in optional_fields if field in item and item[field]) / len(optional_fields)
            
            # Weighted score (required fields more important)
            item_score = (required_score * 0.8) + (optional_score * 0.2)
            completeness_scores.append(item_score)
        
        return round(np.mean(completeness_scores) * 100, 1)
    
    def _calculate_freshness_score(self, data_items: List[Dict]) -> float:
        """Calculate freshness score for data items"""
        
        if not data_items:
            return 0.0
        
        current_time = datetime.now()
        freshness_scores = []
        
        for item in data_items:
            timestamp_str = item.get('timestamp') or item.get('last_updated')
            if timestamp_str:
                try:
                    if isinstance(timestamp_str, str):
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        timestamp = timestamp_str
                    
                    time_diff = current_time - timestamp
                    hours_old = time_diff.total_seconds() / 3600
                    
                    # Score based on how recent the data is
                    if hours_old <= 1:
                        score = 100
                    elif hours_old <= 6:
                        score = 80
                    elif hours_old <= 24:
                        score = 60
                    elif hours_old <= 72:
                        score = 40
                    else:
                        score = 20
                    
                    freshness_scores.append(score)
                except Exception:
                    freshness_scores.append(0)
            else:
                freshness_scores.append(0)
        
        return round(np.mean(freshness_scores), 1) if freshness_scores else 0.0
    
    def _calculate_consistency_score(self, data_items: List[Dict]) -> float:
        """Calculate consistency score for data items"""
        
        if not data_items:
            return 0.0
        
        # Check for consistent data types and ranges
        consistency_scores = []
        
        for item in data_items:
            score = 100
            
            # Check for reasonable values
            if 'co2_emissions_tpy' in item:
                emissions = item['co2_emissions_tpy']
                if not isinstance(emissions, (int, float)) or emissions < 0 or emissions > 10000000:
                    score -= 30
            
            if 'power_price_eur_mwh' in item:
                price = item['power_price_eur_mwh']
                if not isinstance(price, (int, float)) or price < 0 or price > 1000:
                    score -= 30
            
            if 'renewable_energy_share' in item:
                share = item['renewable_energy_share']
                if not isinstance(share, (int, float)) or share < 0 or share > 100:
                    score -= 30
            
            consistency_scores.append(max(0, score))
        
        return round(np.mean(consistency_scores), 1) if consistency_scores else 0.0
    
    def _generate_quality_recommendations(self, data_quality: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving data quality"""
        
        recommendations = []
        
        # Overall quality recommendations
        overall_score = data_quality.get('overall_score', 0)
        if overall_score < 50:
            recommendations.append("Data quality is poor. Consider implementing data validation and quality checks.")
        elif overall_score < 75:
            recommendations.append("Data quality is moderate. Focus on improving data completeness and freshness.")
        elif overall_score < 90:
            recommendations.append("Data quality is good. Minor improvements in consistency and validation needed.")
        else:
            recommendations.append("Data quality is excellent. Maintain current standards and monitoring.")
        
        # Specific recommendations based on scores
        for category, scores in data_quality.items():
            if isinstance(scores, dict):
                for data_type, score in scores.items():
                    if score < 60:
                        recommendations.append(f"Improve {category} for {data_type} data (current score: {score})")
        
        # General recommendations
        recommendations.extend([
            "Implement real-time data validation and error checking",
            "Establish data quality monitoring and alerting systems",
            "Regularly review and update data collection processes",
            "Consider implementing data quality scoring dashboards"
        ])
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _get_primary_country_for_region(self, region: str) -> Optional[str]:
        """Get primary country for a region"""
        
        region_country_map = {
            'Central Europe': 'DE',
            'Western Europe': 'FR',
            'Southern Europe': 'IT',
            'Northern Europe': 'SE',
            'Eastern Europe': 'PL'
        }
        
        return region_country_map.get(region)
    
    def _get_region_center(self, region: str) -> Optional[Dict[str, float]]:
        """Get approximate center coordinates for a region"""
        
        region_centers = {
            'Central Europe': {'lat': 50.8503, 'lon': 4.3517},  # Brussels
            'Western Europe': {'lat': 48.8566, 'lon': 2.3522},  # Paris
            'Southern Europe': {'lat': 41.9028, 'lon': 12.4964}, # Rome
            'Northern Europe': {'lat': 59.3293, 'lon': 18.0686}, # Stockholm
            'Eastern Europe': {'lat': 52.2297, 'lon': 21.0122}  # Warsaw
        }
        
        return region_centers.get(region)
    
    def _get_industry_breakdown(self, facilities: List[FacilityData]) -> Dict[str, int]:
        """Get industry breakdown for facilities"""
        
        industry_counts = {}
        for facility in facilities:
            industry = facility.industry_type
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        return industry_counts
    
    def _get_emissions_by_industry(self, facilities: List[FacilityData]) -> Dict[str, float]:
        """Get CO₂ emissions breakdown by industry"""
        
        industry_emissions = {}
        for facility in facilities:
            industry = facility.industry_type
            if industry not in industry_emissions:
                industry_emissions[industry] = 0
            industry_emissions[industry] += facility.co2_emissions_tpy
        
        return industry_emissions
    
    def _get_emissions_by_country(self, facilities: List[FacilityData]) -> Dict[str, float]:
        """Get CO₂ emissions breakdown by country"""
        
        country_emissions = {}
        for facility in facilities:
            country = facility.country
            if country not in country_emissions:
                country_emissions[country] = 0
            country_emissions[country] += facility.co2_emissions_tpy
        
        return country_emissions
    
    def export_real_time_data(self, 
                             real_time_data: Dict[str, Any], 
                             filename: str = None) -> str:
        """Export real-time data to Excel file"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"realtime_data_export_{timestamp}.xlsx"
        
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Export industrial data
                if real_time_data.get('industrial_data', {}).get('facilities'):
                    industrial_df = pd.DataFrame(real_time_data['industrial_data']['facilities'])
                    industrial_df.to_excel(writer, sheet_name='Industrial_Data', index=False)
                
                # Export energy data
                if real_time_data.get('energy_data', {}).get('power_prices'):
                    energy_df = pd.DataFrame(real_time_data['energy_data']['power_prices'])
                    energy_df.to_excel(writer, sheet_name='Energy_Data', index=False)
                
                # Export renewable data
                if real_time_data.get('energy_data', {}).get('renewable_generation'):
                    renewable_df = pd.DataFrame(real_time_data['energy_data']['renewable_generation'])
                    renewable_df.to_excel(writer, sheet_name='Renewable_Data', index=False)
                
                # Export market forecasts
                if real_time_data.get('market_forecasts'):
                    forecasts_data = []
                    for forecast_type, regions in real_time_data['market_forecasts'].items():
                        if isinstance(regions, dict):
                            for region, forecast in regions.items():
                                if isinstance(forecast, dict) and 'hourly_forecasts' in forecast:
                                    for hourly in forecast['hourly_forecasts']:
                                        forecasts_data.append({
                                            'forecast_type': forecast_type,
                                            'region': region,
                                            'hour': hourly.get('hour', 0),
                                            'data': json.dumps(hourly)
                                        })
                    
                    if forecasts_data:
                        forecasts_df = pd.DataFrame(forecasts_data)
                        forecasts_df.to_excel(writer, sheet_name='Market_Forecasts', index=False)
                
                # Export data quality assessment
                if real_time_data.get('data_quality'):
                    quality_data = []
                    for category, scores in real_time_data['data_quality'].items():
                        if isinstance(scores, dict):
                            for data_type, score in scores.items():
                                quality_data.append({
                                    'category': category,
                                    'data_type': data_type,
                                    'score': score
                                })
                        elif isinstance(scores, (int, float)):
                            quality_data.append({
                                'category': category,
                                'data_type': 'overall',
                                'score': scores
                            })
                    
                    if quality_data:
                        quality_df = pd.DataFrame(quality_data)
                        quality_df.to_excel(writer, sheet_name='Data_Quality', index=False)
            
            logger.info(f"Real-time data exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting real-time data: {e}")
            raise

# Example usage and testing
if __name__ == "__main__":
    # Initialize orchestrator
    orchestrator = APIOrchestrator()
    
    # Collect real-time data
    print("Collecting real-time data...")
    real_time_data = orchestrator.collect_real_time_data(
        target_regions=['Central Europe', 'Western Europe'],
        include_forecasts=True
    )
    
    print(f"Data collection complete. Overall quality score: {real_time_data.get('data_quality', {}).get('overall_score', 'N/A')}")
    
    # Export data
    filename = orchestrator.export_real_time_data(real_time_data)
    print(f"Data exported to: {filename}")
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Industrial facilities: {len(real_time_data.get('industrial_data', {}).get('facilities', []))}")
    print(f"  Energy data points: {len(real_time_data.get('energy_data', {}).get('power_prices', []))}")
    print(f"  Regions covered: {len(real_time_data.get('energy_data', {}).get('regional_summaries', {}))}")
    print(f"  Forecasts generated: {len(real_time_data.get('market_forecasts', {}))}")
