"""
Main Backend Engine for CarbonSiteAI
Orchestrates site screening, financial modeling, and EU policy analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime
import json

# Import our modules
from site_screening import SiteScreeningEngine, SiteMetrics
from financial_modeling import FinancialModel, ProjectParameters, CostStructure
from eu_policy_engine import EUPolicyEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CarbonSiteAIEngine:
    """Main orchestrator for CarbonSiteAI backend operations"""
    
    def __init__(self):
        self.site_engine = SiteScreeningEngine()
        self.policy_engine = EUPolicyEngine()
        self.financial_models = {}
        self.analysis_results = {}
        
        logger.info("CarbonSiteAI Engine initialized")
    
    def load_sample_data(self) -> None:
        """Load sample European industrial sites for demonstration"""
        
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
            },
            {
                'site_id': 'NL001',
                'name': 'Shell Pernis Refinery',
                'country': 'NL',
                'region': 'South Holland',
                'latitude': 51.9225,
                'longitude': 4.4792,
                'co2_volume_tpy': 2800000,
                'co2_concentration': 90,
                'co2_impurities': 'Medium',
                'co2_availability_score': 0,
                'power_price_eur_mwh': 82,
                'power_availability': 99.8,
                'renewable_energy_share': 30,
                'energy_score': 0,
                'emissions_intensity': 520,
                'eu_ets_price': 88,
                'cbam_applicable': True,
                'policy_score': 0,
                'industrial_zone': 'Refinery',
                'utility_availability': 'Excellent',
                'transport_access': 'Excellent',
                'infrastructure_score': 0,
                'labor_costs': 38,
                'land_costs': 250,
                'tax_incentives': 20,
                'financial_score': 0,
                'total_score': 0,
                'ranking': 0
            },
            {
                'site_id': 'BE001',
                'name': 'Total Antwerp',
                'country': 'BE',
                'region': 'Antwerp',
                'latitude': 51.2194,
                'longitude': 4.4025,
                'co2_volume_tpy': 2100000,
                'co2_concentration': 88,
                'co2_impurities': 'Low',
                'co2_availability_score': 0,
                'power_price_eur_mwh': 78,
                'power_availability': 99.2,
                'renewable_energy_share': 22,
                'energy_score': 0,
                'emissions_intensity': 480,
                'eu_ets_price': 87,
                'cbam_applicable': True,
                'policy_score': 0,
                'industrial_zone': 'Refinery',
                'utility_availability': 'Excellent',
                'transport_access': 'Excellent',
                'infrastructure_score': 0,
                'labor_costs': 36,
                'land_costs': 220,
                'tax_incentives': 18,
                'financial_score': 0,
                'total_score': 0,
                'ranking': 0
            },
            {
                'site_id': 'FR001',
                'name': 'ExxonMobil Le Havre',
                'country': 'FR',
                'region': 'Normandy',
                'latitude': 49.4944,
                'longitude': 0.1079,
                'co2_volume_tpy': 1800000,
                'co2_concentration': 82,
                'co2_impurities': 'Medium',
                'co2_availability_score': 0,
                'power_price_eur_mwh': 68,
                'power_availability': 98.8,
                'renewable_energy_share': 35,
                'energy_score': 0,
                'emissions_intensity': 380,
                'eu_ets_price': 86,
                'cbam_applicable': True,
                'policy_score': 0,
                'industrial_zone': 'Refinery',
                'utility_availability': 'Good',
                'transport_access': 'Good',
                'infrastructure_score': 0,
                'labor_costs': 32,
                'land_costs': 180,
                'tax_incentives': 12,
                'financial_score': 0,
                'total_score': 0,
                'ranking': 0
            },
            {
                'site_id': 'IT001',
                'name': 'Eni Porto Marghera',
                'country': 'IT',
                'region': 'Veneto',
                'latitude': 45.4371,
                'longitude': 12.3326,
                'co2_volume_tpy': 1500000,
                'co2_concentration': 80,
                'co2_impurities': 'High',
                'co2_availability_score': 0,
                'power_price_eur_mwh': 95,
                'power_availability': 98.5,
                'renewable_energy_share': 28,
                'energy_score': 0,
                'emissions_intensity': 550,
                'eu_ets_price': 84,
                'cbam_applicable': True,
                'policy_score': 0,
                'industrial_zone': 'Refinery',
                'utility_availability': 'Good',
                'transport_access': 'Good',
                'infrastructure_score': 0,
                'labor_costs': 28,
                'land_costs': 150,
                'tax_incentives': 10,
                'financial_score': 0,
                'total_score': 0,
                'ranking': 0
            }
        ]
        
        for site_data in sample_sites:
            self.site_engine.add_site(site_data)
        
        logger.info(f"Loaded {len(sample_sites)} sample European sites")
    
    def run_comprehensive_analysis(self, 
                                  project_type: str = "CO₂ to Methanol",
                                  target_capacity: float = 100,
                                  priority_weights: Dict[str, float] = None) -> Dict[str, Any]:
        """Run comprehensive analysis for Turnover Labs FOAK pilot"""
        
        logger.info(f"Starting comprehensive analysis for {project_type} project")
        
        # Set default weights if not provided
        if not priority_weights:
            priority_weights = {
                'co2_availability': 0.25,
                'energy': 0.20,
                'policy': 0.20,
                'infrastructure': 0.15,
                'financial': 0.20
            }
        
        # Update site engine weights
        self.site_engine.weights = priority_weights
        
        # Run site screening
        logger.info("Running site screening analysis...")
        screened_sites = self.site_engine.evaluate_sites()
        top_sites = self.site_engine.get_top_sites(5)
        
        # Initialize results storage
        analysis_results = {
            'project_type': project_type,
            'target_capacity': target_capacity,
            'priority_weights': priority_weights,
            'analysis_timestamp': datetime.now().isoformat(),
            'top_sites': [],
            'financial_analysis': {},
            'policy_analysis': {},
            'recommendations': []
        }
        
        # Analyze top sites
        for i, site in enumerate(top_sites):
            logger.info(f"Analyzing site {i+1}: {site.name}")
            
            # Create financial model
            project_params = ProjectParameters(
                project_name=f"Turnover Labs FOAK - {site.name}",
                site_name=site.name,
                co2_input_tpy=target_capacity,
                co_output_tpy=target_capacity * 0.5,  # Assume 50% conversion efficiency
                project_lifetime_years=20
            )
            
            financial_model = FinancialModel(project_params)
            
            # Calculate costs (example values)
            cost_structure = financial_model.calculate_capex(
                equipment_cost=2000000 * (target_capacity / 100)  # Scale with capacity
            )
            
            # Calculate OPEX
            financial_model.calculate_opex(
                power_price_eur_mwh=site.power_price_eur_mwh,
                power_consumption_mwh_per_ton_co=2.5,
                water_consumption_m3_per_ton_co=5,
                water_price_eur_m3=2,
                labor_hours_per_ton_co=10,
                labor_rate_eur_per_hour=site.labor_costs
            )
            
            # Calculate revenue
            financial_model.calculate_revenue(co_price_eur_per_ton=800)
            
            # Generate financial metrics
            financial_metrics = financial_model.calculate_financial_metrics()
            
            # Run EU policy analysis
            site_data = {
                'name': site.name,
                'country': site.country,
                'region': site.region
            }
            
            project_data = {
                'co2_reduction_tpy': target_capacity,
                'product_type': 'chemicals',
                'carbon_intensity': 500,
                'renewable_energy_share': site.renewable_energy_share,
                'energy_efficiency_score': 70,
                'project_lifetime_years': 20
            }
            
            policy_analysis = self.policy_engine.generate_comprehensive_policy_analysis(
                site_data, project_data
            )
            
            # Compile site analysis
            site_analysis = {
                'ranking': site.ranking,
                'site_info': {
                    'name': site.name,
                    'country': site.country,
                    'region': site.region,
                    'coordinates': {'lat': site.latitude, 'lon': site.longitude}
                },
                'screening_scores': {
                    'total_score': site.total_score,
                    'co2_availability': site.co2_availability_score,
                    'energy': site.energy_score,
                    'policy': site.policy_score,
                    'infrastructure': site.infrastructure_score,
                    'financial': site.financial_score
                },
                'financial_analysis': financial_metrics,
                'policy_analysis': policy_analysis,
                'risk_assessment': {
                    'overall_risk': 'Low' if site.total_score >= 80 else 'Medium' if site.total_score >= 60 else 'High',
                    'key_risks': self._identify_key_risks(site, financial_metrics, policy_analysis),
                    'mitigation_strategies': self._generate_mitigation_strategies(site, financial_metrics, policy_analysis)
                }
            }
            
            analysis_results['top_sites'].append(site_analysis)
            
            # Store financial model for later use
            self.financial_models[site.site_id] = financial_model
        
        # Generate overall recommendations
        analysis_results['recommendations'] = self._generate_overall_recommendations(
            analysis_results['top_sites'], project_type, target_capacity
        )
        
        # Store results
        self.analysis_results = analysis_results
        
        logger.info("Comprehensive analysis complete")
        return analysis_results
    
    def _identify_key_risks(self, 
                           site: SiteMetrics, 
                           financial_metrics: Dict, 
                           policy_analysis: Dict) -> List[str]:
        """Identify key risks for a site"""
        
        risks = []
        
        # Financial risks
        if financial_metrics.get('payback_period_years', 0) > 5:
            risks.append("Long payback period may affect financing")
        
        if financial_metrics.get('irr_percent', 0) < 15:
            risks.append("Low IRR may not meet investor requirements")
        
        # Policy risks
        if policy_analysis.get('policy_risk_assessment', {}).get('risk_level') in ['High', 'Very High']:
            risks.append("High policy uncertainty in target region")
        
        # Infrastructure risks
        if site.infrastructure_score < 70:
            risks.append("Infrastructure limitations may increase costs")
        
        # Energy risks
        if site.energy_score < 70:
            risks.append("Energy costs and availability concerns")
        
        return risks
    
    def _generate_mitigation_strategies(self, 
                                      site: SiteMetrics, 
                                      financial_metrics: Dict, 
                                      policy_analysis: Dict) -> List[str]:
        """Generate mitigation strategies for identified risks"""
        
        strategies = []
        
        # Financial mitigation
        if financial_metrics.get('payback_period_years', 0) > 5:
            strategies.append("Consider phased deployment to reduce initial CAPEX")
            strategies.append("Explore government grants and incentives")
        
        # Policy mitigation
        if policy_analysis.get('policy_risk_assessment', {}).get('risk_level') in ['High', 'Very High']:
            strategies.append("Engage with local policymakers early")
            strategies.append("Develop flexible project design")
        
        # Infrastructure mitigation
        if site.infrastructure_score < 70:
            strategies.append("Partner with local infrastructure providers")
            strategies.append("Consider modular system design")
        
        return strategies
    
    def _generate_overall_recommendations(self, 
                                        top_sites: List[Dict], 
                                        project_type: str, 
                                        target_capacity: float) -> List[str]:
        """Generate overall project recommendations"""
        
        recommendations = []
        
        # Top site recommendation
        if top_sites:
            top_site = top_sites[0]
            recommendations.append(
                f"Primary recommendation: Deploy at {top_site['site_info']['name']} "
                f"({top_site['site_info']['country']}) with score {top_site['screening_scores']['total_score']:.1f}/100"
            )
        
        # Capacity recommendations
        if target_capacity <= 100:
            recommendations.append("Consider starting with smaller pilot to validate technology and market")
        elif target_capacity >= 500:
            recommendations.append("Large capacity may require additional financing and risk mitigation")
        
        # Policy recommendations
        recommendations.append("Leverage EU Green Deal and regional incentives for project financing")
        recommendations.append("Position project for CBAM competitive advantage in applicable sectors")
        
        # Financial recommendations
        recommendations.append("Explore EU Innovation Fund and regional grant opportunities")
        recommendations.append("Consider JDA/JV structure with host facility to share risks")
        
        # Risk management
        recommendations.append("Implement comprehensive policy monitoring and stakeholder engagement")
        recommendations.append("Develop contingency plans for regulatory changes")
        
        return recommendations
    
    def export_analysis_report(self, filename: str = None) -> str:
        """Export comprehensive analysis report to Excel"""
        
        if not self.analysis_results:
            raise ValueError("No analysis results available. Run analysis first.")
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"carbonsiteai_analysis_report_{timestamp}.xlsx"
        
        # Create summary sheet
        summary_data = {
            'Project Type': [self.analysis_results['project_type']],
            'Target Capacity (TPY)': [self.analysis_results['target_capacity']],
            'Analysis Date': [self.analysis_results['analysis_timestamp']],
            'Top Site': [self.analysis_results['top_sites'][0]['site_info']['name'] if self.analysis_results['top_sites'] else 'N/A'],
            'Top Site Score': [f"{self.analysis_results['top_sites'][0]['screening_scores']['total_score']:.1f}/100" if self.analysis_results['top_sites'] else 'N/A']
        }
        summary_df = pd.DataFrame(summary_data)
        
        # Create site comparison sheet
        site_comparison_data = []
        for site in self.analysis_results['top_sites']:
            site_comparison_data.append({
                'Ranking': site['ranking'],
                'Site Name': site['site_info']['name'],
                'Country': site['site_info']['country'],
                'Total Score': site['screening_scores']['total_score'],
                'CO2 Score': site['screening_scores']['co2_availability'],
                'Energy Score': site['screening_scores']['energy'],
                'Policy Score': site['screening_scores']['policy'],
                'Infrastructure Score': site['screening_scores']['infrastructure'],
                'Financial Score': site['screening_scores']['financial'],
                'NPV (€)': site['financial_analysis'].get('npv_eur', 0),
                'IRR (%)': site['financial_analysis'].get('irr_percent', 0),
                'Payback (years)': site['financial_analysis'].get('payback_period_years', 0),
                'Policy Risk': site['risk_assessment']['overall_risk']
            })
        site_comparison_df = pd.DataFrame(site_comparison_data)
        
        # Create recommendations sheet
        recommendations_df = pd.DataFrame({
            'Recommendation': self.analysis_results['recommendations']
        })
        
        # Export to Excel
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            site_comparison_df.to_excel(writer, sheet_name='Site_Comparison', index=False)
            recommendations_df.to_excel(writer, sheet_name='Recommendations', index=False)
            
            # Add detailed site sheets
            for i, site in enumerate(self.analysis_results['top_sites']):
                sheet_name = f'Site_{i+1}_{site["site_info"]["name"][:20]}'
                
                # Site details
                site_details = pd.DataFrame([{
                    'Metric': 'Value',
                    'Site Name': site['site_info']['name'],
                    'Country': site['site_info']['country'],
                    'Total Score': site['screening_scores']['total_score'],
                    'Financial NPV': f"€{site['financial_analysis'].get('npv_eur', 0):,.0f}",
                    'Policy Score': f"{site['policy_analysis'].get('overall_policy_score', 0):.1f}/100"
                }])
                site_details.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"Analysis report exported to {filename}")
        return filename
    
    def get_site_details(self, site_id: str) -> Optional[Dict]:
        """Get detailed information for a specific site"""
        
        for site in self.analysis_results.get('top_sites', []):
            if site['site_info']['name'] == site_id:
                return site
        
        return None
    
    def run_what_if_analysis(self, 
                             base_site: str,
                             parameter_changes: Dict[str, Any]) -> Dict[str, Any]:
        """Run what-if analysis for parameter changes"""
        
        logger.info(f"Running what-if analysis for {base_site}")
        
        # Get base site
        base_site_data = self.get_site_details(base_site)
        if not base_site_data:
            raise ValueError(f"Site {base_site} not found in analysis results")
        
        # Create modified project parameters
        modified_params = ProjectParameters(
            project_name=f"What-if Analysis - {base_site}",
            site_name=base_site,
            co2_input_tpy=parameter_changes.get('co2_input_tpy', 100),
            co_output_tpy=parameter_changes.get('co_output_tpy', 50),
            project_lifetime_years=parameter_changes.get('project_lifetime_years', 20)
        )
        
        # Run financial analysis with modified parameters
        financial_model = FinancialModel(modified_params)
        
        # Apply parameter changes
        if 'equipment_cost' in parameter_changes:
            financial_model.calculate_capex(parameter_changes['equipment_cost'])
        
        if 'power_price' in parameter_changes:
            financial_model.calculate_opex(
                power_price_eur_mwh=parameter_changes['power_price'],
                power_consumption_mwh_per_ton_co=2.5,
                water_consumption_m3_per_ton_co=5,
                water_price_eur_m3=2,
                labor_hours_per_ton_co=10,
                labor_rate_eur_per_hour=35
            )
        
        if 'co_price' in parameter_changes:
            financial_model.calculate_revenue(parameter_changes['co_price'])
        
        # Generate results
        financial_metrics = financial_model.calculate_financial_metrics()
        
        what_if_results = {
            'base_site': base_site,
            'parameter_changes': parameter_changes,
            'modified_financial_metrics': financial_metrics,
            'impact_analysis': self._calculate_parameter_impact(
                base_site_data['financial_analysis'], financial_metrics
            )
        }
        
        return what_if_results
    
    def _calculate_parameter_impact(self, 
                                   base_metrics: Dict, 
                                   modified_metrics: Dict) -> Dict[str, Any]:
        """Calculate impact of parameter changes"""
        
        impact = {}
        
        for key in ['npv_eur', 'irr_percent', 'payback_period_years', 'annual_roi_percent']:
            if key in base_metrics and key in modified_metrics:
                base_value = base_metrics[key]
                modified_value = modified_metrics[key]
                
                if isinstance(base_value, (int, float)) and isinstance(modified_value, (int, float)):
                    if base_value != 0:
                        change_percent = ((modified_value - base_value) / base_value) * 100
                        impact[f'{key}_change_percent'] = change_percent
                        impact[f'{key}_change_absolute'] = modified_value - base_value
        
        return impact

# Example usage and testing
if __name__ == "__main__":
    # Initialize main engine
    engine = CarbonSiteAIEngine()
    
    # Load sample data
    engine.load_sample_data()
    
    # Run comprehensive analysis
    results = engine.run_comprehensive_analysis(
        project_type="CO₂ to Methanol",
        target_capacity=100,
        priority_weights={
            'co2_availability': 0.30,
            'energy': 0.25,
            'policy': 0.20,
            'infrastructure': 0.15,
            'financial': 0.10
        }
    )
    
    # Export results
    filename = engine.export_analysis_report()
    print(f"Analysis report exported to: {filename}")
    
    # Print top recommendations
    print("\nTop Recommendations:")
    for i, rec in enumerate(results['recommendations'][:5], 1):
        print(f"{i}. {rec}")
