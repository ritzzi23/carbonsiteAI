"""
Site Screening Engine for Turnover Labs FOAK Pilot
Evaluates potential sites based on CO₂ availability, power prices, emissions intensity, and EU policy alignment
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SiteMetrics:
    """Comprehensive site evaluation metrics"""
    site_id: str
    name: str
    country: str
    region: str
    latitude: float
    longitude: float
    
    # CO₂ Metrics
    co2_volume_tpy: float  # tons per year
    co2_concentration: float  # percentage (20-100%)
    co2_impurities: str  # description of impurities
    co2_availability_score: float  # 0-100
    
    # Power & Energy
    power_price_eur_mwh: float  # €/MWh
    power_availability: float  # percentage
    renewable_energy_share: float  # percentage
    energy_score: float  # 0-100
    
    # Emissions & Policy
    emissions_intensity: float  # kg CO₂/MWh
    eu_ets_price: float  # €/ton CO₂
    cbam_applicable: bool
    policy_score: float  # 0-100
    
    # Infrastructure
    industrial_zone: str
    utility_availability: str
    transport_access: str
    infrastructure_score: float  # 0-100
    
    # Financial
    labor_costs: float  # €/hour
    land_costs: float  # €/m²
    tax_incentives: float  # percentage
    financial_score: float  # 0-100
    
    # Overall Score
    total_score: float  # 0-100
    ranking: int

class SiteScreeningEngine:
    """Main engine for screening and ranking potential sites"""
    
    def __init__(self):
        self.sites = []
        self.weights = {
            'co2_availability': 0.25,
            'energy': 0.20,
            'policy': 0.20,
            'infrastructure': 0.15,
            'financial': 0.20
        }
        
    def add_site(self, site_data: Dict) -> None:
        """Add a new site to the screening database"""
        try:
            site = SiteMetrics(**site_data)
            self.sites.append(site)
            logger.info(f"Added site: {site.name}")
        except Exception as e:
            logger.error(f"Error adding site {site_data.get('name', 'Unknown')}: {e}")
    
    def calculate_co2_score(self, site: SiteMetrics) -> float:
        """Calculate CO₂ availability score (0-100)"""
        # Volume scoring (0-50 points)
        volume_score = min(50, (site.co2_volume_tpy / 1000) * 50)  # 1000 TPY = 50 points
        
        # Concentration scoring (0-30 points)
        # Higher concentration = better (20% = 0 points, 100% = 30 points)
        concentration_score = ((site.co2_concentration - 20) / 80) * 30
        
        # Impurity tolerance (0-20 points)
        # Assume lower impurities = higher score
        impurity_score = 20  # Placeholder - would need impurity analysis
        
        total_score = volume_score + concentration_score + impurity_score
        return min(100, max(0, total_score))
    
    def calculate_energy_score(self, site: SiteMetrics) -> float:
        """Calculate energy cost and availability score (0-100)"""
        # Power price scoring (0-50 points)
        # Lower price = higher score
        # Assume €50/MWh = 50 points, €150/MWh = 0 points
        if site.power_price_eur_mwh <= 50:
            price_score = 50
        elif site.power_price_eur_mwh >= 150:
            price_score = 0
        else:
            price_score = 50 - ((site.power_price_eur_mwh - 50) / 100) * 50
        
        # Renewable energy scoring (0-30 points)
        renewable_score = site.renewable_energy_share * 0.3
        
        # Availability scoring (0-20 points)
        availability_score = site.power_availability * 0.2
        
        total_score = price_score + renewable_score + availability_score
        return min(100, max(0, total_score))
    
    def calculate_policy_score(self, site: SiteMetrics) -> float:
        """Calculate EU policy alignment score (0-100)"""
        # EU ETS price scoring (0-40 points)
        # Higher ETS price = better for CO₂ reduction projects
        if site.eu_ets_price >= 80:
            ets_score = 40
        elif site.eu_ets_price <= 40:
            ets_score = 0
        else:
            ets_score = ((site.eu_ets_price - 40) / 40) * 40
        
        # CBAM applicability (0-30 points)
        cbam_score = 30 if site.cbam_applicable else 0
        
        # Emissions intensity scoring (0-30 points)
        # Lower intensity = better
        if site.emissions_intensity <= 200:
            intensity_score = 30
        elif site.emissions_intensity >= 800:
            intensity_score = 0
        else:
            intensity_score = 30 - ((site.emissions_intensity - 200) / 600) * 30
        
        total_score = ets_score + cbam_score + intensity_score
        return min(100, max(0, total_score))
    
    def calculate_infrastructure_score(self, site: SiteMetrics) -> float:
        """Calculate infrastructure availability score (0-100)"""
        # Industrial zone scoring (0-40 points)
        zone_scores = {
            'Chemical': 40,
            'Refinery': 35,
            'Steel': 30,
            'Cement': 25,
            'Power': 20,
            'Other': 15
        }
        zone_score = zone_scores.get(site.industrial_zone, 15)
        
        # Utility availability (0-30 points)
        utility_scores = {
            'Excellent': 30,
            'Good': 25,
            'Fair': 20,
            'Poor': 10
        }
        utility_score = utility_scores.get(site.utility_availability, 15)
        
        # Transport access (0-30 points)
        transport_scores = {
            'Excellent': 30,
            'Good': 25,
            'Fair': 20,
            'Poor': 10
        }
        transport_score = transport_scores.get(site.transport_access, 15)
        
        total_score = zone_score + utility_score + transport_score
        return min(100, max(0, total_score))
    
    def calculate_financial_score(self, site: SiteMetrics) -> float:
        """Calculate financial viability score (0-100)"""
        # Labor cost scoring (0-40 points)
        # Lower labor costs = higher score
        if site.labor_costs <= 25:
            labor_score = 40
        elif site.labor_costs >= 50:
            labor_score = 0
        else:
            labor_score = 40 - ((site.labor_costs - 25) / 25) * 40
        
        # Land cost scoring (0-30 points)
        if site.land_costs <= 100:
            land_score = 30
        elif site.land_costs >= 500:
            land_score = 0
        else:
            land_score = 30 - ((site.land_costs - 100) / 400) * 30
        
        # Tax incentives (0-30 points)
        incentive_score = min(30, site.tax_incentives * 0.3)
        
        total_score = labor_score + land_score + incentive_score
        return min(100, max(0, total_score))
    
    def evaluate_sites(self) -> List[SiteMetrics]:
        """Evaluate all sites and return ranked list"""
        logger.info(f"Evaluating {len(self.sites)} sites...")
        
        for site in self.sites:
            # Calculate individual scores
            site.co2_availability_score = self.calculate_co2_score(site)
            site.energy_score = self.calculate_energy_score(site)
            site.policy_score = self.calculate_policy_score(site)
            site.infrastructure_score = self.calculate_infrastructure_score(site)
            site.financial_score = self.calculate_financial_score(site)
            
            # Calculate weighted total score
            site.total_score = (
                site.co2_availability_score * self.weights['co2_availability'] +
                site.energy_score * self.weights['energy'] +
                site.policy_score * self.weights['policy'] +
                site.infrastructure_score * self.weights['infrastructure'] +
                site.financial_score * self.weights['financial']
            )
        
        # Sort by total score (descending)
        self.sites.sort(key=lambda x: x.total_score, reverse=True)
        
        # Add rankings
        for i, site in enumerate(self.sites):
            site.ranking = i + 1
        
        logger.info(f"Site evaluation complete. Top site: {self.sites[0].name} (Score: {self.sites[0].total_score:.1f})")
        return self.sites
    
    def get_top_sites(self, n: int = 5) -> List[SiteMetrics]:
        """Get top N ranked sites"""
        if not self.sites:
            self.evaluate_sites()
        return self.sites[:n]
    
    def filter_sites(self, 
                    min_co2_volume: Optional[float] = None,
                    max_power_price: Optional[float] = None,
                    countries: Optional[List[str]] = None,
                    min_score: Optional[float] = None) -> List[SiteMetrics]:
        """Filter sites based on criteria"""
        filtered = self.sites
        
        if min_co2_volume:
            filtered = [s for s in filtered if s.co2_volume_tpy >= min_co2_volume]
        
        if max_power_price:
            filtered = [s for s in filtered if s.power_price_eur_mwh <= max_power_price]
        
        if countries:
            filtered = [s for s in filtered if s.country in countries]
        
        if min_score:
            filtered = [s for s in filtered if s.total_score >= min_score]
        
        return filtered
    
    def export_results(self, filename: str = "site_screening_results.csv") -> None:
        """Export screening results to CSV"""
        if not self.sites:
            self.evaluate_sites()
        
        # Convert to DataFrame
        data = []
        for site in self.sites:
            data.append({
                'Ranking': site.ranking,
                'Name': site.name,
                'Country': site.country,
                'Total_Score': site.total_score,
                'CO2_Score': site.co2_availability_score,
                'Energy_Score': site.energy_score,
                'Policy_Score': site.policy_score,
                'Infrastructure_Score': site.infrastructure_score,
                'Financial_Score': site.financial_score,
                'CO2_Volume_TPY': site.co2_volume_tpy,
                'Power_Price_EUR_MWh': site.power_price_eur_mwh,
                'EU_ETS_Price': site.eu_ets_price,
                'Emissions_Intensity': site.emissions_intensity
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logger.info(f"Results exported to {filename}")

# Example usage and testing
if __name__ == "__main__":
    # Create sample sites for testing
    engine = SiteScreeningEngine()
    
    sample_sites = [
        {
            'site_id': 'DE001',
            'name': 'BASF Ludwigshafen',
            'country': 'DE',
            'region': 'Rhineland-Palatinate',
            'latitude': 49.4811,
            'longitude': 8.4353,
            'co2_volume_tpy': 3200000,
            'co2_concentration': 85,
            'co2_impurities': 'Low',
            'co2_availability_score': 0,
            'power_price_eur_mwh': 75,
            'power_availability': 99.5,
            'renewable_energy_share': 25,
            'energy_score': 0,
            'emissions_intensity': 450,
            'eu_ets_price': 85,
            'cbam_applicable': True,
            'policy_score': 0,
            'industrial_zone': 'Chemical',
            'utility_availability': 'Excellent',
            'transport_access': 'Excellent',
            'infrastructure_score': 0,
            'labor_costs': 35,
            'land_costs': 200,
            'tax_incentives': 15,
            'financial_score': 0,
            'total_score': 0,
            'ranking': 0
        }
    ]
    
    for site_data in sample_sites:
        engine.add_site(site_data)
    
    # Evaluate and get results
    results = engine.evaluate_sites()
    top_sites = engine.get_top_sites(3)
    
    print("Top 3 Sites:")
    for site in top_sites:
        print(f"{site.ranking}. {site.name} - Score: {site.total_score:.1f}")
    
    # Export results
    engine.export_results()
