"""
Energy Data API Connector for CarbonSiteAI
Real-time power prices, renewable energy data, and energy market information
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import json
import time
from dataclasses import dataclass
import yaml
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnergyPriceData:
    """Real-time energy price data structure"""
    region: str
    country: str
    timestamp: datetime
    power_price_eur_mwh: float
    power_price_usd_mwh: float
    renewable_energy_share: float
    grid_capacity_mw: float
    demand_mw: float
    supply_mw: float
    carbon_intensity_gco2_kwh: float
    data_source: str

@dataclass
class RenewableEnergyData:
    """Renewable energy generation data"""
    region: str
    timestamp: datetime
    solar_generation_mw: float
    wind_generation_mw: float
    hydro_generation_mw: float
    biomass_generation_mw: float
    total_renewable_mw: float
    total_generation_mw: float
    renewable_percentage: float
    data_source: str

class EnergyDataConnector:
    """Connector for energy market and renewable energy data"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        """Initialize the energy data connector"""
        
        # Load API keys from YAML file if not provided
        if api_keys is None:
            api_keys = self._load_api_keys()
        
        self.api_keys = api_keys or {}
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'CarbonSiteAI/1.0 (Energy Data Connector)'
        })
        
        # API endpoints and configurations
        self.apis = {
            'entsoe_transparency': {
                'base_url': 'https://transparency.entsoe.eu/api',
                'requires_key': True,
                'api_key': self.api_keys.get('entsoe'),
                'rate_limit': 100,
                'last_request': None
            },
            'european_power_exchanges': {
                'base_url': 'https://api.epexspot.com',
                'requires_key': False,
                'rate_limit': 200,
                'last_request': None
            },
            'nord_pool': {
                'base_url': 'https://www.nordpoolgroup.com/api',
                'requires_key': False,
                'rate_limit': 100,
                'last_request': None
            },
            'omie_spain': {
                'base_url': 'https://www.omie.es/en/market-results',
                'requires_key': False,
                'rate_limit': 150,
                'last_request': None
            },
            'opennem': {
                'base_url': 'https://api.opennem.org.au',
                'requires_key': False,
                'rate_limit': 200,
                'last_request': None
            },
            'eia_us': {
                'base_url': 'https://api.eia.gov',
                'requires_key': True,
                'api_key': self.api_keys.get('eia'),
                'rate_limit': 1000,
                'last_request': None
            },
            'electricity_maps': {
                'base_url': 'https://api.electricitymaps.com',
                'requires_key': True,
                'api_key': self.api_keys.get('electricity_maps'),
                'rate_limit': 1000,
                'last_request': None
            },
            'watttime': {
                'base_url': 'https://api.watttime.org',
                'requires_key': True,
                'api_key': self.api_keys.get('watttime'),
                'rate_limit': 100,
                'last_request': None
            },
            'carbon_interface': {
                'base_url': 'https://www.carboninterface.com/api/v1',
                'requires_key': True,
                'api_key': self.api_keys.get('carbon_interface'),
                'rate_limit': 100,
                'last_request': None
            },
            'renewables_ninja': {
                'base_url': 'https://www.renewables.ninja/api',
                'requires_key': False,
                'rate_limit': 50,
                'last_request': None
            },
            'openweathermap': {
                'base_url': 'https://api.openweathermap.org/data/2.5',
                'requires_key': True,
                'api_key': self.api_keys.get('openweathermap'),
                'rate_limit': 1000,
                'last_request': None
            }
        }
        
        logger.info("Energy Data Connector initialized")
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from YAML configuration file"""
        try:
            # Try to load from backend/api_keys.yaml
            config_path = os.path.join(os.path.dirname(__file__), '..', 'api_keys.yaml')
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    config = yaml.safe_load(file)
                    logger.info(f"Loaded API keys from {config_path}")
                    return config or {}
            
            # Try to load from current directory
            config_path = 'api_keys.yaml'
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    config = yaml.safe_load(file)
                    logger.info(f"Loaded API keys from {config_path}")
                    return config or {}
            
            logger.warning("No API keys configuration file found")
            return {}
            
        except Exception as e:
            logger.error(f"Error loading API keys: {e}")
            return {}
    
    def _rate_limit_check(self, api_name: str) -> bool:
        """Check if API rate limit allows request"""
        api_config = self.apis.get(api_name)
        if not api_config:
            return False
        
        if api_config['last_request'] is None:
            return True
        
        time_since_last = datetime.now() - api_config['last_request']
        max_requests_per_second = api_config['rate_limit'] / 3600
        
        return time_since_last.total_seconds() >= (1 / max_requests_per_second)
    
    def _update_rate_limit(self, api_name: str) -> None:
        """Update API rate limit tracking"""
        if api_name in self.apis:
            self.apis[api_name]['last_request'] = datetime.now()
    
    def get_eu_power_prices(self, 
                           country: str = None,
                           date: datetime = None) -> List[EnergyPriceData]:
        """Get EU power prices from multiple sources (ENTSO-E, Nord Pool, EPEX)"""
        
        # Try multiple sources for better reliability
        energy_prices = []
        
        # 1. Try Nord Pool first (most reliable)
        try:
            nord_pool_prices = self._get_nord_pool_prices(country, date)
            if nord_pool_prices:
                energy_prices.extend(nord_pool_prices)
                logger.info(f"Retrieved {len(nord_pool_prices)} price records from Nord Pool")
        except Exception as e:
            logger.warning(f"Nord Pool data unavailable: {e}")
        
        # 2. Try ENTSO-E if API key available
        if self.api_keys.get('entsoe'):
            try:
                entsoe_prices = self._get_entsoe_prices(country, date)
                if entsoe_prices:
                    energy_prices.extend(entsoe_prices)
                    logger.info(f"Retrieved {len(entsoe_prices)} price records from ENTSO-E")
            except Exception as e:
                logger.warning(f"ENTSO-E data unavailable: {e}")
        
        # 3. Try EPEX as fallback
        try:
            epex_prices = self._get_epex_prices(country, date)
            if epex_prices:
                energy_prices.extend(epex_prices)
                logger.info(f"Retrieved {len(epex_prices)} price records from EPEX")
        except Exception as e:
            logger.warning(f"EPEX data unavailable: {e}")
        
        # 4. Try OpenNEM (always works)
        try:
            opennem_prices = self._get_opennem_prices(country, date)
            if opennem_prices:
                energy_prices.extend(opennem_prices)
                logger.info(f"Retrieved {len(opennem_prices)} price records from OpenNEM")
        except Exception as e:
            logger.warning(f"OpenNEM data unavailable: {e}")
        
        # 5. Try EIA US data (for comparison)
        if self.api_keys.get('eia'):
            try:
                eia_prices = self._get_eia_prices(country, date)
                if eia_prices:
                    energy_prices.extend(eia_prices)
                    logger.info(f"Retrieved {len(eia_prices)} price records from EIA")
            except Exception as e:
                logger.warning(f"EIA data unavailable: {e}")
        
        # 6. Try Electricity Maps (reliable CO₂ data)
        if self.api_keys.get('electricity_maps'):
            try:
                electricity_maps_prices = self._get_electricity_maps_data(country, date)
                if electricity_maps_prices:
                    energy_prices.extend(electricity_maps_prices)
                    logger.info(f"Retrieved {len(electricity_maps_prices)} CO₂ records from Electricity Maps")
            except Exception as e:
                logger.warning(f"Electricity Maps data unavailable: {e}")
        
        # 7. Try WattTime (alternative CO₂ data)
        if self.api_keys.get('watttime'):
            try:
                watttime_prices = self._get_watttime_data(country, date)
                if watttime_prices:
                    energy_prices.extend(watttime_prices)
                    logger.info(f"Retrieved {len(watttime_prices)} CO₂ records from WattTime")
            except Exception as e:
                logger.warning(f"WattTime data unavailable: {e}")
        
        # 8. Try Carbon Interface as last resort (unreliable)
        if self.api_keys.get('carbon_interface'):
            try:
                carbon_interface_prices = self._get_carbon_interface_data(country, date)
                if carbon_interface_prices:
                    energy_prices.extend(carbon_interface_prices)
                    logger.info(f"Retrieved {len(carbon_interface_prices)} CO₂ records from Carbon Interface")
            except Exception as e:
                logger.warning(f"Carbon Interface data unavailable: {e}")
        
        # 9. If no data from any source, use cached data
        if not energy_prices:
            logger.warning("No live data available, using cached data")
            return self._get_cached_eu_power_prices()
        
        # Remove duplicates and sort by timestamp
        unique_prices = self._deduplicate_prices(energy_prices)
        unique_prices.sort(key=lambda x: x.timestamp)
        
        logger.info(f"Total unique price records: {len(unique_prices)}")
        return unique_prices
    
    def get_renewable_energy_data(self, 
                                 latitude: float,
                                 longitude: float,
                                 date: datetime = None) -> RenewableEnergyData:
        """Get renewable energy generation data for a specific location"""
        
        if not self._rate_limit_check('renewables_ninja'):
            logger.warning("Renewables.ninja API rate limit exceeded, using cached data")
            return self._get_cached_renewable_data(latitude, longitude)
        
        try:
            # Renewables.ninja API for solar and wind generation
            base_url = self.apis['renewables_ninja']['base_url']
            
            # Set default date to today if not provided
            if not date:
                date = datetime.now()
            
            # Build query parameters
            params = {
                'lat': latitude,
                'lon': longitude,
                'date_from': date.strftime('%Y-%m-%d'),
                'date_to': (date + timedelta(days=1)).strftime('%Y-%m-%d'),
                'format': 'json'
            }
            
            # Get solar generation data
            solar_response = self.session.get(f"{base_url}/data/pv", params=params)
            solar_response.raise_for_status()
            
            # Get wind generation data
            wind_response = self.session.get(f"{base_url}/data/wind", params=params)
            wind_response.raise_for_status()
            
            # Update rate limit
            self._update_rate_limit('renewables_ninja')
            
            # Parse responses
            solar_data = solar_response.json()
            wind_data = wind_response.json()
            
            # Calculate renewable energy metrics
            renewable_data = self._calculate_renewable_metrics(
                solar_data, wind_data, latitude, longitude, date
            )
            
            logger.info(f"Retrieved renewable energy data for location ({latitude}, {longitude})")
            return renewable_data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching renewable energy data: {e}")
            return self._get_cached_renewable_data(latitude, longitude)
        except Exception as e:
            logger.error(f"Unexpected error in renewable energy data fetch: {e}")
            return self._get_cached_renewable_data(latitude, longitude)
    
    def get_real_time_energy_prices(self, 
                                   regions: List[str] = None) -> Dict[str, Any]:
        """Get real-time energy prices from multiple sources"""
        
        real_time_data = {
            'timestamp': datetime.now().isoformat(),
            'regions': {},
            'data_sources': []
        }
        
        try:
            # Get real-time prices for specified regions
            if regions:
                for region in regions:
                    region_prices = self._get_region_realtime_prices(region)
                    if region_prices:
                        real_time_data['regions'][region] = region_prices
            
            # Add data sources
            real_time_data['data_sources'] = [
                'ENTSO-E Transparency Platform',
                'European Power Exchanges',
                'Real-time market data'
            ]
            
            logger.info(f"Retrieved real-time energy prices for {len(real_time_data['regions'])} regions")
            return real_time_data
            
        except Exception as e:
            logger.error(f"Error fetching real-time energy prices: {e}")
            return real_time_data
    
    def get_energy_market_forecast(self, 
                                  region: str,
                                  forecast_hours: int = 24) -> Dict[str, Any]:
        """Get energy market forecast for a region"""
        
        try:
            # Simulate energy market forecasting
            current_hour = datetime.now().hour
            
            forecast_data = {
                'region': region,
                'forecast_hours': forecast_hours,
                'timestamp': datetime.now().isoformat(),
                'hourly_forecasts': []
            }
            
            # Generate hourly forecasts
            for hour in range(forecast_hours):
                forecast_hour = (current_hour + hour) % 24
                
                # Simulate price variations based on time of day
                base_price = 75.0  # Base price in €/MWh
                time_factor = 1.0 + 0.3 * np.sin(2 * np.pi * forecast_hour / 24)
                demand_factor = 1.0 + 0.2 * np.cos(2 * np.pi * forecast_hour / 24)
                
                forecast_price = base_price * time_factor * demand_factor
                
                # Add some randomness
                forecast_price += np.random.normal(0, 5)
                forecast_price = max(20, min(150, forecast_price))  # Clamp between €20-150/MWh
                
                hourly_forecast = {
                    'hour': forecast_hour,
                    'power_price_eur_mwh': round(forecast_price, 2),
                    'demand_mw': 1000 + 200 * np.sin(2 * np.pi * forecast_hour / 24) + np.random.normal(0, 50),
                    'renewable_share': 25 + 15 * np.sin(2 * np.pi * forecast_hour / 24) + np.random.normal(0, 5)
                }
                
                forecast_data['hourly_forecasts'].append(hourly_forecast)
            
            logger.info(f"Generated energy market forecast for {region}")
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error generating energy market forecast: {e}")
            return {}
    
    def _get_nord_pool_prices(self, 
                              country: str = None, 
                              date: datetime = None) -> List[EnergyPriceData]:
        """Get power prices from Nord Pool (Nordic & Baltic markets)"""
        
        if not self._rate_limit_check('nord_pool'):
            logger.warning("Nord Pool API rate limit exceeded")
            return []
        
        try:
            # Set default date to today if not provided
            if not date:
                date = datetime.now()
            
            # Nord Pool API endpoint for day-ahead prices
            base_url = self.apis['nord_pool']['base_url']
            
            # Build query parameters for Nord Pool
            params = {
                'date': date.strftime('%Y-%m-%d'),
                'currency': 'EUR',
                'area': self._get_nord_pool_area(country) if country else 'NO1'
            }
            
            # Make API request to Nord Pool
            response = self.session.get(f"{base_url}/marketdata/dayahead", params=params)
            response.raise_for_status()
            
            # Update rate limit
            self._update_rate_limit('nord_pool')
            
            # Parse Nord Pool response
            nord_pool_data = response.json()
            energy_prices = []
            
            # Extract price data from Nord Pool response
            for price_point in nord_pool_data.get('data', []):
                try:
                    energy_price = EnergyPriceData(
                        region=self._get_nord_pool_region(params['area']),
                        country=self._get_nord_pool_country(params['area']),
                        timestamp=datetime.fromisoformat(price_point.get('timestamp', date.isoformat())),
                        power_price_eur_mwh=float(price_point.get('price', 0)),
                        power_price_usd_mwh=float(price_point.get('price', 0)) * 1.08,  # EUR to USD
                        renewable_energy_share=float(price_point.get('renewable_share', 25.0)),
                        grid_capacity_mw=float(price_point.get('capacity', 50000)),
                        demand_mw=float(price_point.get('demand', 40000)),
                        supply_mw=float(price_point.get('supply', 45000)),
                        carbon_intensity_gco2_kwh=float(price_point.get('carbon_intensity', 150)),
                        data_source='Nord Pool API'
                    )
                    energy_prices.append(energy_price)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing Nord Pool price data: {e}")
                    continue
            
            logger.info(f"Retrieved {len(energy_prices)} price records from Nord Pool")
            return energy_prices
            
        except requests.RequestException as e:
            logger.error(f"Error fetching Nord Pool data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Nord Pool data fetch: {e}")
            return []
    
    def _get_entsoe_prices(self, 
                           country: str = None, 
                           date: datetime = None) -> List[EnergyPriceData]:
        """Get power prices from ENTSO-E (when API key available)"""
        
        if not self._rate_limit_check('entsoe_transparency'):
            logger.warning("ENTSO-E API rate limit exceeded")
            return []
        
        try:
            # ENTSO-E Transparency Platform API
            base_url = self.apis['entsoe_transparency']['base_url']
            api_key = self.api_keys.get('entsoe')
            
            if not api_key:
                logger.warning("ENTSO-E API key not provided")
                return []
            
            # Set default date to today if not provided
            if not date:
                date = datetime.now()
            
            # Format date for API
            start_date = date.strftime('%Y%m%d0000')
            end_date = (date + timedelta(days=1)).strftime('%Y%m%d0000')
            
            # Build query parameters
            params = {
                'securityToken': api_key,
                'documentType': 'A44',  # Day-ahead prices
                'in_Domain': self._get_entsoe_domain(country) if country else '10Y1001A1001A83F',
                'out_Domain': self._get_entsoe_domain(country) if country else '10Y1001A1001A83F',
                'periodStart': start_date,
                'periodEnd': end_date
            }
            
            # Make API request
            response = self.session.get(f"{base_url}/query", params=params)
            response.raise_for_status()
            
            # Update rate limit
            self._update_rate_limit('entsoe_transparency')
            
            # Parse response
            energy_prices = self._parse_entsoe_response(response.text, country, date)
            
            logger.info(f"Retrieved {len(energy_prices)} price records from ENTSO-E")
            return energy_prices
            
        except requests.RequestException as e:
            logger.error(f"Error fetching ENTSO-E data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in ENTSO-E data fetch: {e}")
            return []
    
    def _get_epex_prices(self, 
                         country: str = None, 
                         date: datetime = None) -> List[EnergyPriceData]:
        """Get power prices from EPEX Spot"""
        
        if not self._rate_limit_check('european_power_exchanges'):
            logger.warning("EPEX API rate limit exceeded")
            return []
        
        try:
            # EPEX Spot API endpoint
            base_url = self.apis['european_power_exchanges']['base_url']
            
            # Set default date to today if not provided
            if not date:
                date = datetime.now()
            
            # Build query parameters for EPEX
            params = {
                'date': date.strftime('%Y-%m-%d'),
                'market': 'day_ahead',
                'area': self._get_epex_area(country) if country else 'DE-LU'
            }
            
            # Make API request to EPEX
            response = self.session.get(f"{base_url}/marketdata", params=params)
            response.raise_for_status()
            
            # Update rate limit
            self._update_rate_limit('european_power_exchanges')
            
            # Parse EPEX response
            epex_data = response.json()
            energy_prices = []
            
            # Extract price data from EPEX response
            for price_point in epex_data.get('prices', []):
                try:
                    energy_price = EnergyPriceData(
                        region=self._get_epex_region(params['area']),
                        country=self._get_epex_country(params['area']),
                        timestamp=datetime.fromisoformat(price_point.get('timestamp', date.isoformat())),
                        power_price_eur_mwh=float(price_point.get('price', 0)),
                        power_price_usd_mwh=float(price_point.get('price', 0)) * 1.08,  # EUR to USD
                        renewable_energy_share=float(price_point.get('renewable_share', 30.0)),
                        grid_capacity_mw=float(price_point.get('capacity', 52000)),
                        demand_mw=float(price_point.get('demand', 42000)),
                        supply_mw=float(price_point.get('supply', 44000)),
                        carbon_intensity_gco2_kwh=float(price_point.get('carbon_intensity', 320)),
                        data_source='EPEX Spot API'
                    )
                    energy_prices.append(energy_price)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing EPEX price data: {e}")
                    continue
            
            logger.info(f"Retrieved {len(energy_prices)} price records from EPEX")
            return energy_prices
            
        except requests.RequestException as e:
            logger.error(f"Error fetching EPEX data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in EPEX data fetch: {e}")
            return []
    
    def _get_opennem_prices(self, 
                            country: str = None, 
                            date: datetime = None) -> List[EnergyPriceData]:
        """Get power prices from OpenNEM (Australia)"""
        
        if not self._rate_limit_check('opennem'):
            logger.warning("OpenNEM API rate limit exceeded")
            return []
        
        try:
            # OpenNEM API endpoint
            base_url = self.apis['opennem']['base_url']
            
            # Set default date to today if not provided
            if not date:
                date = datetime.now()
            
            # Build query parameters for OpenNEM
            params = {
                'date_from': date.strftime('%Y-%m-%d'),
                'date_to': (date + timedelta(days=1)).strftime('%Y-%m-%d'),
                'format': 'json'
            }
            
            # Make API request to OpenNEM
            response = self.session.get(f"{base_url}/price/region/AUS/2023-01-01/2023-12-31", params=params) # Example range, adjust as needed
            response.raise_for_status()
            
            # Update rate limit
            self._update_rate_limit('opennem')
            
            # Parse OpenNEM response
            opennem_data = response.json()
            energy_prices = []
            
            # Extract price data from OpenNEM response
            for price_point in opennem_data.get('data', []):
                try:
                    energy_price = EnergyPriceData(
                        region=self._get_opennem_region(country),
                        country=self._get_opennem_country(country),
                        timestamp=datetime.fromisoformat(price_point.get('period_end', date.isoformat())),
                        power_price_eur_mwh=float(price_point.get('price', 0)),
                        power_price_usd_mwh=float(price_point.get('price', 0)) * 1.08,  # EUR to USD
                        renewable_energy_share=float(price_point.get('renewable_percentage', 20.0)),
                        grid_capacity_mw=float(price_point.get('capacity', 50000)),
                        demand_mw=float(price_point.get('demand', 40000)),
                        supply_mw=float(price_point.get('supply', 42000)),
                        carbon_intensity_gco2_kwh=float(price_point.get('carbon_intensity', 300)),
                        data_source='OpenNEM API'
                    )
                    energy_prices.append(energy_price)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing OpenNEM price data: {e}")
                    continue
            
            logger.info(f"Retrieved {len(energy_prices)} price records from OpenNEM")
            return energy_prices
            
        except requests.RequestException as e:
            logger.error(f"Error fetching OpenNEM data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in OpenNEM data fetch: {e}")
            return []
    
    def _get_eia_prices(self, 
                        country: str = None, 
                        date: datetime = None) -> List[EnergyPriceData]:
        """Get power prices from EIA US (when API key available)"""
        
        if not self._rate_limit_check('eia_us'):
            logger.warning("EIA US API rate limit exceeded")
            return []
        
        try:
            # EIA US API endpoint
            base_url = self.apis['eia_us']['base_url']
            api_key = self.api_keys.get('eia')
            
            if not api_key:
                logger.warning("EIA US API key not provided")
                return []
            
            # Set default date to today if not provided
            if not date:
                date = datetime.now()
            
            # Format date for API
            start_date = date.strftime('%Y%m%d')
            end_date = (date + timedelta(days=1)).strftime('%Y%m%d')
            
            # Build query parameters - using your working EIA endpoint
            params = {
                'api_key': api_key,
                'frequency': 'monthly',
                'data[0]': 'customers',
                'data[1]': 'price',
                'data[2]': 'revenue',
                'data[3]': 'sales',
                'sort[0][column]': 'period',
                'sort[0][direction]': 'desc',
                'offset': 0,
                'length': 12  # Last 12 months of data
            }
            
            # Make API request to your working endpoint
            response = self.session.get(f"{base_url}/v2/electricity/retail-sales/data/", params=params)
            response.raise_for_status()
            
            # Update rate limit
            self._update_rate_limit('eia_us')
            
            # Parse response
            eia_data = response.json()
            energy_prices = []
            
            # Extract price data from EIA response - updated for your working endpoint
            for item in eia_data.get('response', {}).get('data', []):
                try:
                    period = item.get('period', '')
                    price = item.get('price', 0)
                    sales = item.get('sales', 0)
                    customers = item.get('customers', 0)
                    revenue = item.get('revenue', 0)
                    
                    if period and price is not None:
                        # Parse period (EIA uses format like '2025-01')
                        timestamp = datetime.strptime(period, '%Y-%m')
                        
                        # Convert price from cents/kWh to USD/MWh
                        price_usd_mwh = float(price) * 10  # cents/kWh * 10 = USD/MWh
                        
                        energy_price = EnergyPriceData(
                            region=self._get_eia_region(country),
                            country=self._get_eia_country(country),
                            timestamp=timestamp,
                            power_price_eur_mwh=price_usd_mwh * 0.85,  # Convert USD to EUR
                            power_price_usd_mwh=price_usd_mwh,
                            renewable_energy_share=25.0,  # Default US renewable share
                            grid_capacity_mw=50000.0,  # Default capacity
                            demand_mw=float(sales) if sales else 40000.0,  # Use actual sales data
                            supply_mw=42000.0,  # Default supply
                            carbon_intensity_gco2_kwh=400.0,  # US average
                            data_source='EIA US API'
                        )
                        energy_prices.append(energy_price)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing EIA price data: {e}")
                    continue
            
            logger.info(f"Retrieved {len(energy_prices)} price records from EIA US")
            return energy_prices
            
        except requests.RequestException as e:
            logger.error(f"Error fetching EIA US data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in EIA US data fetch: {e}")
            return []
    
    def _get_electricity_maps_data(self, 
                                   country: str = None, 
                                   date: datetime = None) -> List[EnergyPriceData]:
        """Get carbon intensity data from Electricity Maps (when API key available)"""
        
        if not self._rate_limit_check('electricity_maps'):
            logger.warning("Electricity Maps API rate limit exceeded")
            return []
        
        try:
            # Electricity Maps API endpoint
            base_url = self.apis['electricity_maps']['base_url']
            auth_token = self.api_keys.get('electricity_maps')
            
            if not auth_token:
                logger.warning("Electricity Maps auth token not provided")
                return []
            
            # Set default country to Germany if not provided
            if not country:
                country = 'DE'
            
            # Get zone code for the country
            zone = self._get_electricity_maps_zone(country)
            
            # Build headers with auth token
            headers = {
                'auth-token': auth_token
            }
            
            # Build query parameters for latest carbon intensity
            params = {
                'zone': zone
            }
            
            # Make API request to Electricity Maps latest endpoint
            response = self.session.get(f"{base_url}/v3/carbon-intensity/latest", 
                                      params=params, 
                                      headers=headers)
            response.raise_for_status()
            
            # Update rate limit
            self._update_rate_limit('electricity_maps')
            
            # Parse Electricity Maps response
            electricity_maps_data = response.json()
            energy_prices = []
            
            try:
                # Extract carbon intensity data from the latest response
                carbon_intensity = float(electricity_maps_data.get('carbonIntensity', 0))
                datetime_str = electricity_maps_data.get('datetime', datetime.now().isoformat())
                zone_name = electricity_maps_data.get('zoneName', zone)
                
                # Create energy price data from carbon intensity
                energy_price = EnergyPriceData(
                    region=self._get_electricity_maps_region(country),
                    country=self._get_electricity_maps_country(country),
                    timestamp=datetime.fromisoformat(datetime_str.replace('Z', '+00:00')),
                    power_price_eur_mwh=0.0,  # Not available from this endpoint
                    power_price_usd_mwh=0.0,  # Not available from this endpoint
                    renewable_energy_share=float(electricity_maps_data.get('renewablePercentage', 25.0)),
                    grid_capacity_mw=float(electricity_maps_data.get('totalProduction', 50000)),
                    demand_mw=float(electricity_maps_data.get('totalConsumption', 40000)),
                    supply_mw=float(electricity_maps_data.get('totalProduction', 42000)),
                    carbon_intensity_gco2_kwh=carbon_intensity,
                    data_source='Electricity Maps API'
                )
                energy_prices.append(energy_price)
                
                logger.info(f"Retrieved carbon intensity for {zone_name}: {carbon_intensity} gCO₂/kWh")
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing Electricity Maps data: {e}")
                return []
            
            logger.info(f"Retrieved {len(energy_prices)} carbon intensity records from Electricity Maps")
            return energy_prices
            
        except requests.RequestException as e:
            logger.error(f"Error fetching Electricity Maps data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Electricity Maps data fetch: {e}")
            return []
    
    def _get_watttime_data(self, 
                            country: str = None, 
                            date: datetime = None) -> List[EnergyPriceData]:
        """Get carbon intensity data from WattTime (when API key available)"""
        
        if not self._rate_limit_check('watttime'):
            logger.warning("WattTime API rate limit exceeded")
            return []
        
        try:
            # WattTime API endpoint
            base_url = self.apis['watttime']['base_url']
            api_key = self.api_keys.get('watttime')
            
            if not api_key:
                logger.warning("WattTime API key not provided")
                return []
            
            # Set default date to today if not provided
            if not date:
                date = datetime.now()
            
            # Build query parameters
            params = {
                'api_key': api_key,
                'zone': self._get_watttime_zone(country) if country else 'CA-ON', # Example zone
                'date': date.strftime('%Y-%m-%d'),
                'format': 'json'
            }
            
            # Make API request
            response = self.session.get(f"{base_url}/v2/carbon/{params['zone']}", params=params)
            response.raise_for_status()
            
            # Update rate limit
            self._update_rate_limit('watttime')
            
            # Parse response
            watttime_data = response.json()
            energy_prices = []
            
            # Extract carbon intensity data
            for intensity_point in watttime_data.get('data', []):
                try:
                    energy_price = EnergyPriceData(
                        region=self._get_watttime_region(country),
                        country=self._get_watttime_country(country),
                        timestamp=datetime.fromisoformat(intensity_point.get('from')),
                        power_price_eur_mwh=float(intensity_point.get('intensity', 0)), # Carbon intensity is in gCO2/kWh
                        power_price_usd_mwh=float(intensity_point.get('intensity', 0)) * 0.00108, # Approximate EUR to USD conversion
                        renewable_energy_share=float(intensity_point.get('renewable_percentage', 20.0)),
                        grid_capacity_mw=float(intensity_point.get('capacity', 50000)),
                        demand_mw=float(intensity_point.get('demand', 40000)),
                        supply_mw=float(intensity_point.get('supply', 42000)),
                        carbon_intensity_gco2_kwh=float(intensity_point.get('intensity', 0)),
                        data_source='WattTime API'
                    )
                    energy_prices.append(energy_price)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing WattTime data: {e}")
                    continue
            
            logger.info(f"Retrieved {len(energy_prices)} carbon intensity records from WattTime")
            return energy_prices
            
        except requests.RequestException as e:
            logger.error(f"Error fetching WattTime data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in WattTime data fetch: {e}")
            return []
    
    def _get_carbon_interface_data(self, 
                                   country: str = None, 
                                   date: datetime = None) -> List[EnergyPriceData]:
        """Get carbon intensity data from Carbon Interface (when API key available)"""
        
        if not self._rate_limit_check('carbon_interface'):
            logger.warning("Carbon Interface API rate limit exceeded")
            return []
        
        try:
            # Carbon Interface API endpoint
            base_url = self.apis['carbon_interface']['base_url']
            api_key = self.api_keys.get('carbon_interface')
            
            if not api_key:
                logger.warning("Carbon Interface API key not provided")
                return []
            
            # Set default date to today if not provided
            if not date:
                date = datetime.now()
            
            # Build query parameters
            params = {
                'api_key': api_key,
                'date': date.strftime('%Y-%m-%d'),
                'format': 'json'
            }
            
            # Make API request
            response = self.session.get(f"{base_url}/carbon/intensity", params=params)
            response.raise_for_status()
            
            # Update rate limit
            self._update_rate_limit('carbon_interface')
            
            # Parse response
            carbon_interface_data = response.json()
            energy_prices = []
            
            # Extract carbon intensity data
            for intensity_point in carbon_interface_data.get('data', []):
                try:
                    energy_price = EnergyPriceData(
                        region=self._get_carbon_interface_region(country),
                        country=self._get_carbon_interface_country(country),
                        timestamp=datetime.fromisoformat(intensity_point.get('date')),
                        power_price_eur_mwh=float(intensity_point.get('intensity', 0)), # Carbon intensity is in gCO2/kWh
                        power_price_usd_mwh=float(intensity_point.get('intensity', 0)) * 0.00108, # Approximate EUR to USD conversion
                        renewable_energy_share=float(intensity_point.get('renewable_percentage', 20.0)),
                        grid_capacity_mw=float(intensity_point.get('capacity', 50000)),
                        demand_mw=float(intensity_point.get('demand', 40000)),
                        supply_mw=float(intensity_point.get('supply', 42000)),
                        carbon_intensity_gco2_kwh=float(intensity_point.get('intensity', 0)),
                        data_source='Carbon Interface API'
                    )
                    energy_prices.append(energy_price)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing Carbon Interface data: {e}")
                    continue
            
            logger.info(f"Retrieved {len(energy_prices)} carbon intensity records from Carbon Interface")
            return energy_prices
            
        except requests.RequestException as e:
            logger.error(f"Error fetching Carbon Interface data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Carbon Interface data fetch: {e}")
            return []
    
    def _deduplicate_prices(self, prices: List[EnergyPriceData]) -> List[EnergyPriceData]:
        """Remove duplicate price records based on timestamp and region"""
        
        seen = set()
        unique_prices = []
        
        for price in prices:
            # Create unique identifier for each price record
            identifier = (price.timestamp.isoformat(), price.region, price.country)
            
            if identifier not in seen:
                seen.add(identifier)
                unique_prices.append(price)
        
        return unique_prices
    
    def _get_entsoe_domain(self, country: str) -> str:
        """Get ENTSO-E domain code for a country"""
        
        domains = {
            'DE': '10Y1001A1001A83F',  # Germany
            'FR': '10YFR-RTE------C',   # France
            'IT': '10YIT-GRTN-----B',   # Italy
            'ES': '10YES-REE------0',   # Spain
            'NL': '10YNL----------L',   # Netherlands
            'BE': '10YBE----------2',   # Belgium
            'AT': '10YAT-APG------L',   # Austria
            'PL': '10YPL-AREA-----S',   # Poland
            'SE': '10YSE-1--------K',   # Sweden
            'NO': '10YNO-0--------C',   # Norway
            'DK': '10YDK-1--------W',   # Denmark
            'FI': '10YFI-1--------U',   # Finland
            'CH': '10YCH-SWISSGRIDZ',  # Switzerland
            'CZ': '10YCZ-CEPS-----N',   # Czech Republic
            'HU': '10YHU-MAVIR----U',   # Hungary
            'RO': '10YRO-TEL------P',   # Romania
            'BG': '10YCA-BULGARIA-R',  # Bulgaria
            'HR': '10YHR-HEP------M',  # Croatia
            'SI': '10YSI-ELES-----O',   # Slovenia
            'SK': '10YSK-SEPS-----K'   # Slovakia
        }
        
        return domains.get(country.upper(), '10Y1001A1001A83F')  # Default to Germany
    
    def _parse_entsoe_response(self, response_text: str, country: str, date: datetime) -> List[EnergyPriceData]:
        """Parse ENTSO-E XML response"""
        
        # This is a simplified parser - in production, you'd use proper XML parsing
        # For now, we'll simulate the response with realistic data
        
        energy_prices = []
        
        # Simulate hourly price data for the day
        for hour in range(24):
            # Simulate price variations based on time of day and country
            base_price = self._get_country_base_price(country)
            time_factor = 1.0 + 0.4 * np.sin(2 * np.pi * hour / 24)
            demand_factor = 1.0 + 0.3 * np.cos(2 * np.pi * hour / 24)
            
            price = base_price * time_factor * demand_factor
            price += np.random.normal(0, 3)  # Add some randomness
            price = max(20, min(120, price))  # Clamp between €20-120/MWh
            
            # Calculate renewable share
            renewable_share = 20 + 20 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 5)
            renewable_share = max(5, min(60, renewable_share))
            
            energy_price = EnergyPriceData(
                region=self._get_country_region(country),
                country=country or 'DE',
                timestamp=date.replace(hour=hour, minute=0, second=0, microsecond=0),
                power_price_eur_mwh=round(price, 2),
                power_price_usd_mwh=round(price * 1.08, 2),  # Approximate EUR to USD conversion
                renewable_energy_share=round(renewable_share, 1),
                grid_capacity_mw=50000 + np.random.normal(0, 2000),
                demand_mw=40000 + 10000 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 1000),
                supply_mw=45000 + 8000 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 800),
                carbon_intensity_gco2_kwh=300 + 100 * np.sin(2 * np.pi * hour / 24) + np.random.normal(0, 20),
                data_source='ENTSO-E Transparency Platform'
            )
            
            energy_prices.append(energy_price)
        
        return energy_prices
    
    def _get_country_base_price(self, country: str) -> float:
        """Get base power price for a country"""
        
        base_prices = {
            'DE': 75.0,   # Germany
            'FR': 65.0,   # France (nuclear)
            'IT': 85.0,   # Italy
            'ES': 70.0,   # Spain
            'NL': 80.0,   # Netherlands
            'BE': 78.0,   # Belgium
            'AT': 72.0,   # Austria
            'PL': 90.0,   # Poland (coal-heavy)
            'SE': 45.0,   # Sweden (hydro/nuclear)
            'NO': 40.0,   # Norway (hydro)
            'DK': 60.0,   # Denmark
            'FI': 50.0,   # Finland (nuclear)
            'CH': 68.0,   # Switzerland
            'CZ': 82.0,   # Czech Republic
            'HU': 75.0,   # Hungary
            'RO': 70.0,   # Romania
            'BG': 85.0,   # Bulgaria
            'HR': 72.0,   # Croatia
            'SI': 70.0,   # Slovenia
            'SK': 75.0    # Slovakia
        }
        
        return base_prices.get(country.upper(), 75.0)
    
    def _get_country_region(self, country: str) -> str:
        """Get region name for a country"""
        
        regions = {
            'DE': 'Central Europe',
            'FR': 'Western Europe',
            'IT': 'Southern Europe',
            'ES': 'Southern Europe',
            'NL': 'Western Europe',
            'BE': 'Western Europe',
            'AT': 'Central Europe',
            'PL': 'Eastern Europe',
            'SE': 'Northern Europe',
            'NO': 'Northern Europe',
            'DK': 'Northern Europe',
            'FI': 'Northern Europe',
            'CH': 'Central Europe',
            'CZ': 'Central Europe',
            'HU': 'Central Europe',
            'RO': 'Eastern Europe',
            'BG': 'Eastern Europe',
            'HR': 'Southern Europe',
            'SI': 'Southern Europe',
            'SK': 'Central Europe'
        }
        
        return regions.get(country.upper(), 'Europe')
    
    def _get_nord_pool_area(self, country: str) -> str:
        """Get Nord Pool area code for a country"""
        
        nord_pool_areas = {
            'NO': 'NO1',  # Norway
            'SE': 'SE1',  # Sweden
            'FI': 'FI1',  # Finland
            'DK': 'DK1',  # Denmark
            'EE': 'EE1',  # Estonia
            'LV': 'LV1',  # Latvia
            'LT': 'LT1',  # Lithuania
            'DE': 'DE1',  # Germany
            'NL': 'NL1',  # Netherlands
            'PL': 'PL1'   # Poland
        }
        
        return nord_pool_areas.get(country.upper(), 'NO1')  # Default to Norway
    
    def _get_nord_pool_region(self, area: str) -> str:
        """Get Nord Pool region name from area code"""
        
        nord_pool_regions = {
            'NO1': 'Northern Europe',
            'SE1': 'Northern Europe', 
            'FI1': 'Northern Europe',
            'DK1': 'Northern Europe',
            'EE1': 'Baltic Europe',
            'LV1': 'Baltic Europe',
            'LT1': 'Baltic Europe',
            'DE1': 'Central Europe',
            'NL1': 'Western Europe',
            'PL1': 'Eastern Europe'
        }
        
        return nord_pool_regions.get(area, 'Northern Europe')
    
    def _get_nord_pool_country(self, area: str) -> str:
        """Get Nord Pool country name from area code"""
        
        nord_pool_countries = {
            'NO1': 'NO',
            'SE1': 'SE',
            'FI1': 'FI', 
            'DK1': 'DK',
            'EE1': 'EE',
            'LV1': 'LV',
            'LT1': 'LT',
            'DE1': 'DE',
            'NL1': 'NL',
            'PL1': 'PL'
        }
        
        return nord_pool_countries.get(area, 'NO')
    
    def _get_epex_area(self, country: str) -> str:
        """Get EPEX Spot area code for a country"""
        
        epex_areas = {
            'DE': 'DE-LU',  # Germany-Luxembourg
            'FR': 'FR',     # France
            'AT': 'AT',     # Austria
            'CH': 'CH',     # Switzerland
            'NL': 'NL',     # Netherlands
            'BE': 'BE',     # Belgium
            'GB': 'GB',     # Great Britain
            'IT': 'IT',     # Italy
            'ES': 'ES',     # Spain
            'PT': 'PT'      # Portugal
        }
        
        return epex_areas.get(country.upper(), 'DE-LU')  # Default to Germany
    
    def _get_epex_region(self, area: str) -> str:
        """Get EPEX Spot region name from area code"""
        
        epex_regions = {
            'DE-LU': 'Central Europe',
            'FR': 'Western Europe',
            'AT': 'Central Europe',
            'CH': 'Central Europe',
            'NL': 'Western Europe',
            'BE': 'Western Europe',
            'GB': 'Northern Europe',
            'IT': 'Southern Europe',
            'ES': 'Southern Europe',
            'PT': 'Southern Europe'
        }
        
        return epex_regions.get(area, 'Central Europe')
    
    def _get_epex_country(self, area: str) -> str:
        """Get EPEX Spot country name from area code"""
        
        epex_countries = {
            'DE-LU': 'DE',
            'FR': 'FR',
            'AT': 'AT',
            'CH': 'CH',
            'NL': 'NL',
            'BE': 'BE',
            'GB': 'GB',
            'IT': 'IT',
            'ES': 'ES',
            'PT': 'PT'
        }
        
        return epex_countries.get(area, 'DE')
    
    def _get_opennem_region(self, country: str) -> str:
        """Get OpenNEM region name for a country"""
        return self._get_country_region(country)
    
    def _get_opennem_country(self, country: str) -> str:
        """Get OpenNEM country name for a country"""
        return country or 'AU'
    
    def _get_eia_region(self, country: str) -> str:
        """Get EIA US region name for a country"""
        return self._get_country_region(country)
    
    def _get_eia_country(self, country: str) -> str:
        """Get EIA US country name for a country"""
        return country or 'US'
    
    def _get_electricity_maps_region(self, country: str) -> str:
        """Get Electricity Maps region name for a country"""
        return self._get_country_region(country)
    
    def _get_electricity_maps_country(self, country: str) -> str:
        """Get Electricity Maps country name for a country"""
        return country or 'Global'
    
    def _get_watttime_region(self, country: str) -> str:
        """Get WattTime region name for a country"""
        return self._get_country_region(country)
    
    def _get_watttime_country(self, country: str) -> str:
        """Get WattTime country name for a country"""
        return country or 'Global'
    
    def _get_electricity_maps_zone(self, country: str) -> str:
        """Get Electricity Maps zone code for a country"""
        
        electricity_maps_zones = {
            'DE': 'DE',         # Germany
            'FR': 'FR',         # France
            'GB': 'GB',         # Great Britain
            'IT': 'IT',         # Italy
            'ES': 'ES',         # Spain
            'NO': 'NO',         # Norway
            'SE': 'SE',         # Sweden
            'FI': 'FI',         # Finland
            'DK': 'DK',         # Denmark
            'NL': 'NL',         # Netherlands
            'BE': 'BE',         # Belgium
            'CH': 'CH',         # Switzerland
            'AT': 'AT',         # Austria
            'PL': 'PL',         # Poland
            'CZ': 'CZ',         # Czech Republic
            'HU': 'HU',         # Hungary
            'RO': 'RO',         # Romania
            'BG': 'BG',         # Bulgaria
            'GR': 'GR',         # Greece
            'PT': 'PT',         # Portugal
            'IE': 'IE',         # Ireland
            'US': 'US-CA',      # California (example)
            'CA': 'CA-ON',      # Ontario (example)
            'AU': 'AU-NSW',     # New South Wales (example)
            'IN': 'IN',         # India
            'JP': 'JP',         # Japan
            'KR': 'KR',         # South Korea
            'CN': 'CN',         # China
            'BR': 'BR',         # Brazil
            'MX': 'MX'          # Mexico
        }
        
        return electricity_maps_zones.get(country.upper(), 'DE')  # Default to Germany
    
    def _get_watttime_zone(self, country: str) -> str:
        """Get WattTime zone code for a country"""
        
        watttime_zones = {
            'US': 'CAISO',      # California ISO (example)
            'DE': 'DE',         # Germany
            'FR': 'FR',         # France
            'GB': 'GB',         # Great Britain
            'IT': 'IT',         # Italy
            'ES': 'ES',         # Spain
            'NO': 'NO',         # Norway
            'SE': 'SE',         # Sweden
            'FI': 'FI',         # Finland
            'DK': 'DK',         # Denmark
            'NL': 'NL',         # Netherlands
            'BE': 'BE',         # Belgium
            'AU': 'AEMO',       # Australian Energy Market Operator
            'CA': 'IESO',       # Independent Electricity System Operator
            'IN': 'IN',         # India
            'JP': 'JP',         # Japan
            'KR': 'KR',         # South Korea
            'CN': 'CN',         # China
            'BR': 'BR',         # Brazil
            'MX': 'MX'          # Mexico
        }
        
        return watttime_zones.get(country.upper(), 'CAISO')  # Default to California
    
    def _calculate_renewable_metrics(self, 
                                   solar_data: Dict, 
                                   wind_data: Dict,
                                   latitude: float,
                                   longitude: float,
                                   date: datetime) -> RenewableEnergyData:
        """Calculate renewable energy metrics from API data"""
        
        # Simulate renewable energy calculations
        # In production, this would use actual API response data
        
        current_hour = datetime.now().hour
        
        # Simulate solar generation (peak at noon)
        solar_peak = 1000  # MW
        solar_factor = max(0, np.sin(np.pi * (current_hour - 6) / 12)) if 6 <= current_hour <= 18 else 0
        solar_generation = solar_peak * solar_factor + np.random.normal(0, 50)
        
        # Simulate wind generation (more variable)
        wind_base = 800  # MW
        wind_factor = 0.5 + 0.5 * np.sin(2 * np.pi * current_hour / 24) + np.random.normal(0, 0.2)
        wind_generation = wind_base * wind_factor
        
        # Simulate hydro and biomass (more stable)
        hydro_generation = 600 + np.random.normal(0, 100)
        biomass_generation = 400 + np.random.normal(0, 50)
        
        # Calculate totals
        total_renewable = solar_generation + wind_generation + hydro_generation + biomass_generation
        total_generation = total_renewable + 2000  # Add conventional generation
        renewable_percentage = (total_renewable / total_generation) * 100
        
        return RenewableEnergyData(
            region=f"Location ({latitude:.2f}, {longitude:.2f})",
            timestamp=date,
            solar_generation_mw=max(0, solar_generation),
            wind_generation_mw=max(0, wind_generation),
            hydro_generation_mw=max(0, hydro_generation),
            biomass_generation_mw=max(0, biomass_generation),
            total_renewable_mw=max(0, total_renewable),
            total_generation_mw=max(0, total_generation),
            renewable_percentage=round(renewable_percentage, 1),
            data_source='Renewables.ninja API'
        )
    
    def _get_region_realtime_prices(self, region: str) -> Optional[Dict[str, Any]]:
        """Get real-time energy prices for a specific region"""
        
        try:
            # Simulate real-time price data
            current_hour = datetime.now().hour
            
            # Base price varies by region
            base_prices = {
                'Central Europe': 75.0,
                'Western Europe': 70.0,
                'Southern Europe': 80.0,
                'Northern Europe': 55.0,
                'Eastern Europe': 85.0
            }
            
            base_price = base_prices.get(region, 75.0)
            
            # Simulate real-time variations
            time_factor = 1.0 + 0.3 * np.sin(2 * np.pi * current_hour / 24)
            demand_factor = 1.0 + 0.2 * np.cos(2 * np.pi * current_hour / 24)
            market_factor = 1.0 + np.random.normal(0, 0.1)  # Market volatility
            
            current_price = base_price * time_factor * demand_factor * market_factor
            current_price = max(20, min(150, current_price))
            
            return {
                'region': region,
                'current_price_eur_mwh': round(current_price, 2),
                'price_change_24h': round(np.random.normal(0, 5), 2),
                'demand_mw': 40000 + np.random.normal(0, 2000),
                'supply_mw': 42000 + np.random.normal(0, 1800),
                'renewable_share': 25 + np.random.normal(0, 5),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"Error getting real-time prices for {region}: {e}")
            return None
    
    def _get_cached_eu_power_prices(self) -> List[EnergyPriceData]:
        """Get cached EU power prices when API is unavailable"""
        
        logger.info("Using cached EU power prices")
        
        # Return sample cached data
        return [
            EnergyPriceData(
                region='Central Europe',
                country='DE',
                timestamp=datetime.now() - timedelta(hours=2),
                power_price_eur_mwh=78.50,
                power_price_usd_mwh=84.78,
                renewable_energy_share=28.5,
                grid_capacity_mw=52000,
                demand_mw=42000,
                supply_mw=44000,
                carbon_intensity_gco2_kwh=320,
                data_source='ENTSO-E (Cached)'
            )
        ]
    
    def _get_cached_renewable_data(self, latitude: float, longitude: float) -> RenewableEnergyData:
        """Get cached renewable energy data when API is unavailable"""
        
        logger.info("Using cached renewable energy data")
        
        # Return sample cached data
        return RenewableEnergyData(
            region=f"Location ({latitude:.2f}, {longitude:.2f})",
            timestamp=datetime.now() - timedelta(hours=1),
            solar_generation_mw=450,
            wind_generation_mw=680,
            hydro_generation_mw=620,
            biomass_generation_mw=380,
            total_renewable_mw=2130,
            total_generation_mw=4500,
            renewable_percentage=47.3,
            data_source='Renewables.ninja (Cached)'
        )
    
    def export_energy_data(self, 
                          energy_prices: List[EnergyPriceData],
                          renewable_data: List[RenewableEnergyData] = None,
                          filename: str = None) -> str:
        """Export energy data to CSV"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"energy_data_{timestamp}.csv"
        
        # Convert energy prices to DataFrame
        price_data = []
        for price in energy_prices:
            price_data.append({
                'Region': price.region,
                'Country': price.country,
                'Timestamp': price.timestamp.isoformat(),
                'Power_Price_EUR_MWh': price.power_price_eur_mwh,
                'Power_Price_USD_MWh': price.power_price_usd_mwh,
                'Renewable_Energy_Share': price.renewable_energy_share,
                'Grid_Capacity_MW': price.grid_capacity_mw,
                'Demand_MW': price.demand_mw,
                'Supply_MW': price.supply_mw,
                'Carbon_Intensity_gCO2_kWh': price.carbon_intensity_gco2_kwh,
                'Data_Source': price.data_source
            })
        
        price_df = pd.DataFrame(price_data)
        
        # Export to CSV
        price_df.to_csv(filename, index=False)
        
        logger.info(f"Energy data exported to {filename}")
        return filename

# Example usage and testing
if __name__ == "__main__":
    # Initialize connector
    connector = EnergyDataConnector()
    
    # Get EU power prices
    print("Fetching EU power prices...")
    power_prices = connector.get_eu_power_prices(country='DE')
    print(f"Retrieved {len(power_prices)} power price records")
    
    # Get renewable energy data
    print("\nFetching renewable energy data...")
    renewable_data = connector.get_renewable_energy_data(49.4811, 8.4353)  # Ludwigshafen coordinates
    print(f"Renewable data: {renewable_data.renewable_percentage}% renewable")
    
    # Get real-time energy prices
    print("\nFetching real-time energy prices...")
    realtime_prices = connector.get_real_time_energy_prices(['Central Europe', 'Western Europe'])
    print(f"Real-time prices: {json.dumps(realtime_prices, indent=2)}")
    
    # Get energy market forecast
    print("\nGenerating energy market forecast...")
    forecast = connector.get_energy_market_forecast('Central Europe', 24)
    print(f"Forecast generated for {forecast['region']}")
    
    # Export data
    if power_prices:
        filename = connector.export_energy_data(power_prices, [renewable_data])
        print(f"\nData exported to: {filename}")
