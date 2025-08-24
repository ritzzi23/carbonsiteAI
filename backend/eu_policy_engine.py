"""
EU Policy Integration Engine for Turnover Labs
Handles EU ETS, CBAM, Green Deal, and regional incentives analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from datetime import datetime, date
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EUPolicyMetrics:
    """EU policy and incentive metrics for a site"""
    site_id: str
    country: str
    region: str
    
    # EU ETS Metrics
    eu_ets_price_eur_ton: float
    eu_ets_allowance_volume: float  # tons CO₂
    eu_ets_compliance_status: str  # Compliant, Non-compliant, Pending
    
    # CBAM Metrics
    cbam_applicable: bool
    cbam_scope: List[str]  # List of applicable sectors
    cbam_carbon_intensity: float  # kg CO₂/unit of product
    
    # Green Deal Metrics
    green_deal_alignment_score: float  # 0-100
    renewable_energy_target: float  # percentage
    energy_efficiency_target: float  # percentage
    
    # Regional Incentives
    regional_grants_available: bool
    grant_amount_eur: float
    grant_eligibility_criteria: List[str]
    tax_incentives_percentage: float
    
    # Policy Risk Assessment
    policy_stability_score: float  # 0-100
    regulatory_uncertainty: str  # Low, Medium, High
    compliance_complexity: str  # Low, Medium, High

class EUPolicyEngine:
    """Main engine for EU policy analysis and integration"""
    
    def __init__(self):
        self.eu_countries = [
            'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DE', 'DK', 'EE', 'FI',
            'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT',
            'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
        ]
        
        # EU ETS price trends (historical and projected)
        self.ets_price_trends = {
            '2023': 85.0,
            '2024': 88.0,
            '2025': 92.0,
            '2026': 96.0,
            '2027': 100.0,
            '2028': 105.0,
            '2029': 110.0,
            '2030': 115.0
        }
        
        # CBAM scope by sector
        self.cbam_sectors = {
            'cement': ['clinker', 'cement', 'lime'],
            'iron_steel': ['iron_ore', 'pig_iron', 'steel_products'],
            'aluminium': ['alumina', 'aluminium'],
            'fertilisers': ['ammonia', 'nitric_acid', 'urea'],
            'electricity': ['electricity'],
            'hydrogen': ['hydrogen'],
            'chemicals': ['ethylene', 'propylene', 'benzene', 'methanol']
        }
        
        # Regional incentive programs
        self.regional_incentives = {
            'DE': {
                'grants': ['KfW Energy Efficiency', 'BMWK Innovation'],
                'tax_benefits': 15.0,
                'policy_stability': 90
            },
            'NL': {
                'grants': ['SDE++', 'Topsector Energy'],
                'tax_benefits': 20.0,
                'policy_stability': 85
            },
            'BE': {
                'grants': ['Wallonia Green Deal', 'Flanders Innovation'],
                'tax_benefits': 18.0,
                'policy_stability': 80
            },
            'FR': {
                'grants': ['ADEME', 'France Relance'],
                'tax_benefits': 12.0,
                'policy_stability': 75
            },
            'IT': {
                'grants': ['Piano Nazionale', 'Transizione 4.0'],
                'tax_benefits': 10.0,
                'policy_stability': 70
            }
        }
    
    def calculate_eu_ets_impact(self, 
                               site_data: Dict,
                               project_co2_reduction: float) -> Dict:
        """Calculate EU ETS impact and benefits"""
        
        country = site_data.get('country', '')
        if country not in self.eu_countries:
            return {'error': 'Site not in EU'}
        
        # Get current ETS price
        current_year = str(datetime.now().year)
        ets_price = self.ets_price_trends.get(current_year, 85.0)
        
        # Calculate annual ETS savings
        annual_ets_savings = project_co2_reduction * ets_price
        
        # Project future savings (assuming price increases)
        future_savings = {}
        for year, price in self.ets_price_trends.items():
            if int(year) > datetime.now().year:
                future_savings[year] = project_co2_reduction * price
        
        # Calculate total 5-year savings
        total_5yr_savings = sum(future_savings.values())
        
        ets_impact = {
            'current_ets_price_eur_ton': ets_price,
            'annual_ets_savings_eur': annual_ets_savings,
            'future_ets_savings': future_savings,
            'total_5yr_savings_eur': total_5yr_savings,
            'ets_compliance_benefit': 'Reduces compliance burden',
            'carbon_market_exposure': 'Direct exposure to EU carbon pricing'
        }
        
        logger.info(f"EU ETS impact calculated for {site_data.get('name', 'Unknown site')}")
        logger.info(f"  Annual savings: €{annual_ets_savings:,.0f}")
        logger.info(f"  5-year savings: €{total_5yr_savings:,.0f}")
        
        return ets_impact
    
    def assess_cbam_applicability(self, 
                                 site_data: Dict,
                                 product_type: str,
                                 carbon_intensity: float) -> Dict:
        """Assess CBAM applicability and impact"""
        
        country = site_data.get('country', '')
        if country not in self.eu_countries:
            return {'error': 'Site not in EU'}
        
        # Check if product is in CBAM scope
        cbam_applicable = False
        applicable_sectors = []
        
        for sector, products in self.cbam_sectors.items():
            if product_type.lower() in [p.lower() for p in products]:
                cbam_applicable = True
                applicable_sectors.append(sector)
        
        # Calculate CBAM impact
        cbam_impact = {
            'cbam_applicable': cbam_applicable,
            'applicable_sectors': applicable_sectors,
            'carbon_intensity_kg_co2_unit': carbon_intensity,
            'cbam_scope': 'In scope' if cbam_applicable else 'Not in scope',
            'competitive_advantage': 'Yes' if cbam_applicable else 'No',
            'border_adjustment_benefit': 'Reduces import competition' if cbam_applicable else 'No direct benefit'
        }
        
        if cbam_applicable:
            logger.info(f"CBAM applicable for {site_data.get('name', 'Unknown site')}")
            logger.info(f"  Applicable sectors: {', '.join(applicable_sectors)}")
        else:
            logger.info(f"CBAM not applicable for {site_data.get('name', 'Unknown site')}")
        
        return cbam_impact
    
    def calculate_green_deal_alignment(self, 
                                     site_data: Dict,
                                     renewable_energy_share: float,
                                     energy_efficiency_score: float) -> Dict:
        """Calculate Green Deal alignment score and benefits"""
        
        country = site_data.get('country', '')
        if country not in self.eu_countries:
            return {'error': 'Site not in EU'}
        
        # Green Deal targets
        renewable_target_2030 = 42.5  # 42.5% by 2030
        renewable_target_2050 = 100.0  # 100% by 2050
        efficiency_target_2030 = 32.5  # 32.5% improvement by 2030
        
        # Calculate alignment scores
        renewable_score = min(100, (renewable_energy_share / renewable_target_2030) * 100)
        efficiency_score = min(100, (energy_efficiency_score / efficiency_target_2030) * 100)
        
        # Overall alignment score (weighted average)
        overall_alignment = (renewable_score * 0.6) + (efficiency_score * 0.4)
        
        # Determine alignment level
        if overall_alignment >= 80:
            alignment_level = 'High'
            funding_priority = 'High'
        elif overall_alignment >= 60:
            alignment_level = 'Medium'
            funding_priority = 'Medium'
        else:
            alignment_level = 'Low'
            funding_priority = 'Low'
        
        green_deal_analysis = {
            'overall_alignment_score': overall_alignment,
            'alignment_level': alignment_level,
            'renewable_energy_score': renewable_score,
            'energy_efficiency_score': efficiency_score,
            'funding_priority': funding_priority,
            'eu_funding_eligibility': 'Yes' if overall_alignment >= 60 else 'No',
            'green_deal_benefits': [
                'Access to EU Innovation Fund',
                'Eligible for regional green grants',
                'Enhanced market positioning',
                'Regulatory compliance advantage'
            ] if overall_alignment >= 60 else ['Limited benefits available']
        }
        
        logger.info(f"Green Deal alignment calculated for {site_data.get('name', 'Unknown site')}")
        logger.info(f"  Overall alignment: {overall_alignment:.1f}/100 ({alignment_level})")
        logger.info(f"  Funding priority: {funding_priority}")
        
        return green_deal_analysis
    
    def assess_regional_incentives(self, site_data: Dict) -> Dict:
        """Assess available regional incentives and grants"""
        
        country = site_data.get('country', '')
        if country not in self.regional_incentives:
            return {'error': 'No incentive data available for this country'}
        
        country_incentives = self.regional_incentives[country]
        
        # Calculate potential grant amounts (example calculation)
        potential_grant = 0
        if country_incentives['grants']:
            # Assume grants cover 20-40% of project costs
            base_grant_rate = 0.30
            potential_grant = base_grant_rate * 1000000  # €1M base project
        
        # Assess tax benefits
        tax_benefits = country_incentives['tax_benefits']
        policy_stability = country_incentives['policy_stability']
        
        # Determine incentive attractiveness
        if policy_stability >= 85 and tax_benefits >= 15:
            attractiveness = 'Very High'
        elif policy_stability >= 75 and tax_benefits >= 10:
            attractiveness = 'High'
        elif policy_stability >= 65 and tax_benefits >= 8:
            attractiveness = 'Medium'
        else:
            attractiveness = 'Low'
        
        regional_analysis = {
            'country': country,
            'available_grants': country_incentives['grants'],
            'potential_grant_amount_eur': potential_grant,
            'tax_incentives_percentage': tax_benefits,
            'policy_stability_score': policy_stability,
            'incentive_attractiveness': attractiveness,
            'grant_eligibility': 'Likely' if potential_grant > 0 else 'Unlikely',
            'total_incentive_value_eur': potential_grant + (tax_benefits / 100 * 1000000),
            'application_complexity': 'Medium' if len(country_incentives['grants']) > 1 else 'Low'
        }
        
        logger.info(f"Regional incentives assessed for {site_data.get('name', 'Unknown site')}")
        logger.info(f"  Country: {country}")
        logger.info(f"  Available grants: {len(country_incentives['grants'])}")
        logger.info(f"  Potential grant: €{potential_grant:,.0f}")
        logger.info(f"  Attractiveness: {attractiveness}")
        
        return regional_analysis
    
    def calculate_policy_risk_score(self, 
                                   site_data: Dict,
                                   project_lifetime_years: int = 20) -> Dict:
        """Calculate policy risk assessment score"""
        
        country = site_data.get('country', '')
        if country not in self.eu_countries:
            return {'error': 'Site not in EU'}
        
        # Base policy stability
        base_stability = self.regional_incentives.get(country, {}).get('policy_stability', 70)
        
        # Policy risk factors
        risk_factors = {
            'eu_parliament_elections': 5,  # Elections every 5 years
            'national_elections': 3,       # National elections
            'regulatory_changes': 8,      # EU regulatory updates
            'market_volatility': 4        # Carbon market fluctuations
        }
        
        # Calculate risk over project lifetime
        total_risk_score = 0
        for factor, risk_weight in risk_factors.items():
            factor_occurrences = project_lifetime_years // 5  # Assume major changes every 5 years
            total_risk_score += factor_occurrences * risk_weight
        
        # Normalize risk score to 0-100
        normalized_risk = min(100, max(0, total_risk_score))
        
        # Determine risk level
        if normalized_risk <= 25:
            risk_level = 'Low'
            risk_description = 'Stable policy environment'
        elif normalized_risk <= 50:
            risk_level = 'Medium'
            risk_description = 'Moderate policy uncertainty'
        elif normalized_risk <= 75:
            risk_level = 'High'
            risk_description = 'Significant policy risk'
        else:
            risk_level = 'Very High'
            risk_description = 'Highly uncertain policy environment'
        
        # Mitigation strategies
        mitigation_strategies = [
            'Diversify across multiple EU markets',
            'Engage with policymakers early',
            'Build regulatory compliance buffers',
            'Monitor policy developments closely',
            'Consider shorter project timelines'
        ]
        
        risk_assessment = {
            'policy_risk_score': normalized_risk,
            'risk_level': risk_level,
            'risk_description': risk_description,
            'base_policy_stability': base_stability,
            'project_lifetime_risk_factors': risk_factors,
            'mitigation_strategies': mitigation_strategies,
            'recommended_actions': [
                'Regular policy monitoring',
                'Stakeholder engagement',
                'Flexible project design',
                'Risk contingency planning'
            ]
        }
        
        logger.info(f"Policy risk assessment for {site_data.get('name', 'Unknown site')}")
        logger.info(f"  Risk score: {normalized_risk:.1f}/100 ({risk_level})")
        logger.info(f"  Risk description: {risk_description}")
        
        return risk_assessment
    
    def generate_comprehensive_policy_analysis(self, 
                                             site_data: Dict,
                                             project_data: Dict) -> Dict:
        """Generate comprehensive EU policy analysis for a site"""
        
        logger.info(f"Generating comprehensive EU policy analysis for {site_data.get('name', 'Unknown site')}")
        
        # Extract project parameters
        co2_reduction = project_data.get('co2_reduction_tpy', 100)
        product_type = project_data.get('product_type', 'chemicals')
        carbon_intensity = project_data.get('carbon_intensity', 500)
        renewable_energy = project_data.get('renewable_energy_share', 25)
        energy_efficiency = project_data.get('energy_efficiency_score', 70)
        project_lifetime = project_data.get('project_lifetime_years', 20)
        
        # Run all analyses
        ets_analysis = self.calculate_eu_ets_impact(site_data, co2_reduction)
        cbam_analysis = self.assess_cbam_applicability(site_data, product_type, carbon_intensity)
        green_deal_analysis = self.calculate_green_deal_alignment(site_data, renewable_energy, energy_efficiency)
        regional_analysis = self.assess_regional_incentives(site_data)
        risk_analysis = self.calculate_policy_risk_score(site_data, project_lifetime)
        
        # Calculate overall policy score
        policy_scores = [
            green_deal_analysis.get('overall_alignment_score', 0),
            regional_analysis.get('policy_stability_score', 0),
            (100 - risk_analysis.get('policy_risk_score', 0))  # Invert risk to score
        ]
        
        overall_policy_score = sum(policy_scores) / len(policy_scores)
        
        # Compile comprehensive analysis
        comprehensive_analysis = {
            'site_information': {
                'name': site_data.get('name', 'Unknown'),
                'country': site_data.get('country', 'Unknown'),
                'region': site_data.get('region', 'Unknown')
            },
            'overall_policy_score': overall_policy_score,
            'eu_ets_analysis': ets_analysis,
            'cbam_analysis': cbam_analysis,
            'green_deal_analysis': green_deal_analysis,
            'regional_incentives': regional_analysis,
            'policy_risk_assessment': risk_analysis,
            'policy_recommendations': [
                'Leverage EU ETS savings for project financing',
                'Position project for CBAM competitive advantage',
                'Apply for available regional grants and incentives',
                'Implement risk mitigation strategies',
                'Monitor EU policy developments closely'
            ],
            'next_steps': [
                'Engage with regional development agencies',
                'Prepare grant applications',
                'Develop policy monitoring framework',
                'Establish stakeholder engagement plan'
            ]
        }
        
        logger.info(f"Comprehensive policy analysis complete")
        logger.info(f"  Overall policy score: {overall_policy_score:.1f}/100")
        
        return comprehensive_analysis
    
    def export_policy_analysis(self, 
                               analysis: Dict, 
                               filename: str = None) -> str:
        """Export policy analysis to Excel file"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            site_name = analysis['site_information']['name'].replace(' ', '_')
            filename = f"eu_policy_analysis_{site_name}_{timestamp}.xlsx"
        
        # Create summary DataFrame
        summary_data = {
            'Metric': [
                'Site Name', 'Country', 'Overall Policy Score',
                'EU ETS Annual Savings (€)', 'CBAM Applicable',
                'Green Deal Alignment', 'Regional Grant Potential (€)',
                'Policy Risk Level'
            ],
            'Value': [
                analysis['site_information']['name'],
                analysis['site_information']['country'],
                f"{analysis['overall_policy_score']:.1f}/100",
                f"€{analysis['eu_ets_analysis'].get('annual_ets_savings_eur', 0):,.0f}",
                'Yes' if analysis['cbam_analysis']['cbam_applicable'] else 'No',
                analysis['green_deal_analysis']['alignment_level'],
                f"€{analysis['regional_incentives'].get('potential_grant_amount_eur', 0):,.0f}",
                analysis['policy_risk_assessment']['risk_level']
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        
        # Export to Excel
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Add detailed sheets
            pd.DataFrame([analysis['eu_ets_analysis']]).to_excel(writer, sheet_name='EU_ETS_Analysis', index=False)
            pd.DataFrame([analysis['cbam_analysis']]).to_excel(writer, sheet_name='CBAM_Analysis', index=False)
            pd.DataFrame([analysis['green_deal_analysis']]).to_excel(writer, sheet_name='Green_Deal_Analysis', index=False)
            pd.DataFrame([analysis['regional_incentives']]).to_excel(writer, sheet_name='Regional_Incentives', index=False)
            pd.DataFrame([analysis['policy_risk_assessment']]).to_excel(writer, sheet_name='Policy_Risk_Assessment', index=False)
        
        logger.info(f"Policy analysis exported to {filename}")
        return filename

# Example usage and testing
if __name__ == "__main__":
    # Initialize policy engine
    policy_engine = EUPolicyEngine()
    
    # Sample site data
    sample_site = {
        'name': 'BASF Ludwigshafen',
        'country': 'DE',
        'region': 'Rhineland-Palatinate'
    }
    
    # Sample project data
    sample_project = {
        'co2_reduction_tpy': 100,
        'product_type': 'chemicals',
        'carbon_intensity': 500,
        'renewable_energy_share': 25,
        'energy_efficiency_score': 70,
        'project_lifetime_years': 20
    }
    
    # Generate comprehensive analysis
    analysis = policy_engine.generate_comprehensive_policy_analysis(sample_site, sample_project)
    
    # Export results
    filename = policy_engine.export_policy_analysis(analysis)
    print(f"Policy analysis exported to: {filename}")
