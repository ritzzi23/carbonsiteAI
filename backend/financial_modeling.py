"""
Financial Modeling Engine for Turnover Labs FOAK Pilot
Calculates ROI, NPV, host value stack, and commercial structure analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProjectParameters:
    """FOAK pilot project parameters"""
    project_name: str
    site_name: str
    co2_input_tpy: float  # tons CO₂ per year
    co_output_tpy: float  # tons CO per year
    project_lifetime_years: int = 20
    construction_period_years: int = 2
    ramp_up_period_years: int = 1
    
    # Financial parameters
    discount_rate: float = 0.10  # 10% WACC
    inflation_rate: float = 0.02  # 2% annual inflation
    tax_rate: float = 0.25  # 25% corporate tax rate
    
    # EU Policy parameters
    eu_ets_price_eur_ton: float = 85.0
    cbam_applicable: bool = True
    carbon_credit_price_eur_ton: float = 85.0

@dataclass
class CostStructure:
    """Detailed cost structure for the FOAK pilot"""
    # Capital costs (€)
    equipment_capex: float
    installation_capex: float
    engineering_capex: float
    contingency_capex: float
    total_capex: float
    
    # Operating costs (€/year)
    electricity_cost: float
    water_cost: float
    labor_cost: float
    maintenance_cost: float
    insurance_cost: float
    total_opex: float
    
    # Revenue streams (€/year)
    co_sales_revenue: float
    carbon_credits_revenue: float
    avoided_co2_costs: float
    total_revenue: float

class FinancialModel:
    """Main financial modeling engine"""
    
    def __init__(self, project_params: ProjectParameters):
        self.project_params = project_params
        self.cost_structure = None
        self.cash_flows = []
        self.financial_metrics = {}
        
    def calculate_capex(self, 
                       equipment_cost: float,
                       installation_factor: float = 0.15,
                       engineering_factor: float = 0.10,
                       contingency_factor: float = 0.20) -> CostStructure:
        """Calculate detailed capital expenditure structure"""
        
        installation_capex = equipment_cost * installation_factor
        engineering_capex = equipment_cost * engineering_factor
        contingency_capex = equipment_cost * contingency_factor
        total_capex = equipment_cost + installation_capex + engineering_capex + contingency_capex
        
        # Calculate annualized capex over construction period
        annual_capex = total_capex / self.project_params.construction_period_years
        
        logger.info(f"CAPEX breakdown for {self.project_params.project_name}:")
        logger.info(f"  Equipment: €{equipment_cost:,.0f}")
        logger.info(f"  Installation: €{installation_capex:,.0f}")
        logger.info(f"  Engineering: €{engineering_capex:,.0f}")
        logger.info(f"  Contingency: €{contingency_capex:,.0f}")
        logger.info(f"  Total CAPEX: €{total_capex:,.0f}")
        
        return CostStructure(
            equipment_capex=equipment_cost,
            installation_capex=installation_capex,
            engineering_capex=engineering_capex,
            contingency_capex=contingency_capex,
            total_capex=total_capex,
            electricity_cost=0,  # Will be calculated separately
            water_cost=0,
            labor_cost=0,
            maintenance_cost=0,
            insurance_cost=0,
            total_opex=0,
            co_sales_revenue=0,
            carbon_credits_revenue=0,
            avoided_co2_costs=0,
            total_revenue=0
        )
    
    def calculate_opex(self, 
                      power_price_eur_mwh: float,
                      power_consumption_mwh_per_ton_co: float,
                      water_consumption_m3_per_ton_co: float,
                      water_price_eur_m3: float,
                      labor_hours_per_ton_co: float,
                      labor_rate_eur_per_hour: float,
                      maintenance_factor: float = 0.03,
                      insurance_factor: float = 0.01) -> None:
        """Calculate operating expenditure structure"""
        
        if not self.cost_structure:
            raise ValueError("CAPEX must be calculated first")
        
        # Electricity costs
        total_power_consumption = self.project_params.co_output_tpy * power_consumption_mwh_per_ton_co
        electricity_cost = total_power_consumption * power_price_eur_mwh
        
        # Water costs
        total_water_consumption = self.project_params.co_output_tpy * water_consumption_m3_per_ton_co
        water_cost = total_water_consumption * water_price_eur_m3
        
        # Labor costs
        total_labor_hours = self.project_params.co_output_tpy * labor_hours_per_ton_co
        labor_cost = total_labor_hours * labor_rate_eur_per_hour
        
        # Maintenance and insurance (as % of total CAPEX)
        maintenance_cost = self.cost_structure.total_capex * maintenance_factor
        insurance_cost = self.cost_structure.total_capex * insurance_factor
        
        total_opex = electricity_cost + water_cost + labor_cost + maintenance_cost + insurance_cost
        
        # Update cost structure
        self.cost_structure.electricity_cost = electricity_cost
        self.cost_structure.water_cost = water_cost
        self.cost_structure.labor_cost = labor_cost
        self.cost_structure.maintenance_cost = maintenance_cost
        self.cost_structure.insurance_cost = insurance_cost
        self.cost_structure.total_opex = total_opex
        
        logger.info(f"OPEX breakdown for {self.project_params.project_name}:")
        logger.info(f"  Electricity: €{electricity_cost:,.0f}/year")
        logger.info(f"  Water: €{water_cost:,.0f}/year")
        logger.info(f"  Labor: €{labor_cost:,.0f}/year")
        logger.info(f"  Maintenance: €{maintenance_cost:,.0f}/year")
        logger.info(f"  Insurance: €{insurance_cost:,.0f}/year")
        logger.info(f"  Total OPEX: €{total_opex:,.0f}/year")
    
    def calculate_revenue(self, 
                         co_price_eur_per_ton: float,
                         carbon_credit_volume_tpy: float = None) -> None:
        """Calculate revenue streams"""
        
        if not self.cost_structure:
            raise ValueError("Cost structure must be calculated first")
        
        # CO sales revenue
        co_sales_revenue = self.project_params.co_output_tpy * co_price_eur_per_ton
        
        # Carbon credits revenue (if applicable)
        if carbon_credit_volume_tpy:
            carbon_credits_revenue = carbon_credit_volume_tpy * self.project_params.carbon_credit_price_eur_ton
        else:
            # Assume CO₂ avoidance equals CO₂ input
            carbon_credits_revenue = self.project_params.co2_input_tpy * self.project_params.carbon_credit_price_eur_ton
        
        # Avoided CO₂ costs (EU ETS savings)
        avoided_co2_costs = self.project_params.co2_input_tpy * self.project_params.eu_ets_price_eur_ton
        
        total_revenue = co_sales_revenue + carbon_credits_revenue + avoided_co2_costs
        
        # Update cost structure
        self.cost_structure.co_sales_revenue = co_sales_revenue
        self.cost_structure.carbon_credits_revenue = carbon_credits_revenue
        self.cost_structure.avoided_co2_costs = avoided_co2_costs
        self.cost_structure.total_revenue = total_revenue
        
        logger.info(f"Revenue breakdown for {self.project_params.project_name}:")
        logger.info(f"  CO Sales: €{co_sales_revenue:,.0f}/year")
        logger.info(f"  Carbon Credits: €{carbon_credits_revenue:,.0f}/year")
        logger.info(f"  Avoided CO₂ Costs: €{avoided_co2_costs:,.0f}/year")
        logger.info(f"  Total Revenue: €{total_revenue:,.0f}/year")
    
    def generate_cash_flows(self) -> List[Dict]:
        """Generate detailed cash flow projections"""
        
        if not self.cost_structure:
            raise ValueError("Cost structure must be calculated first")
        
        cash_flows = []
        current_year = 0
        
        # Construction period (negative cash flows)
        annual_capex = self.cost_structure.total_capex / self.project_params.construction_period_years
        for year in range(self.project_params.construction_period_years):
            cash_flows.append({
                'year': current_year,
                'period': f'Construction {year + 1}',
                'capex': -annual_capex,
                'opex': 0,
                'revenue': 0,
                'net_cash_flow': -annual_capex,
                'cumulative_cash_flow': -annual_capex * (year + 1)
            })
            current_year += 1
        
        # Ramp-up period (partial revenue)
        ramp_up_factor = 0.5  # 50% of full capacity
        for year in range(self.project_params.ramp_up_period_years):
            revenue = self.cost_structure.total_revenue * ramp_up_factor
            opex = self.cost_structure.total_opex * ramp_up_factor
            net_cash_flow = revenue - opex
            
            cash_flows.append({
                'year': current_year,
                'period': f'Ramp-up {year + 1}',
                'capex': 0,
                'opex': -opex,
                'revenue': revenue,
                'net_cash_flow': net_cash_flow,
                'cumulative_cash_flow': cash_flows[-1]['cumulative_cash_flow'] + net_cash_flow
            })
            current_year += 1
        
        # Full operation period
        for year in range(self.project_params.project_lifetime_years - 
                         self.project_params.construction_period_years - 
                         self.project_params.ramp_up_period_years):
            
            revenue = self.cost_structure.total_revenue
            opex = self.cost_structure.total_opex
            net_cash_flow = revenue - opex
            
            cash_flows.append({
                'year': current_year,
                'period': f'Operation {year + 1}',
                'capex': 0,
                'opex': -opex,
                'revenue': revenue,
                'net_cash_flow': net_cash_flow,
                'cumulative_cash_flow': cash_flows[-1]['cumulative_cash_flow'] + net_cash_flow
            })
            current_year += 1
        
        self.cash_flows = cash_flows
        return cash_flows
    
    def calculate_financial_metrics(self) -> Dict:
        """Calculate key financial metrics"""
        
        if not self.cash_flows:
            self.generate_cash_flows()
        
        # Extract cash flows
        net_cash_flows = [cf['net_cash_flow'] for cf in self.cash_flows]
        cumulative_cash_flows = [cf['cumulative_cash_flow'] for cf in self.cash_flows]
        
        # Net Present Value (NPV)
        npv = 0
        for i, cf in enumerate(net_cash_flows):
            npv += cf / ((1 + self.project_params.discount_rate) ** i)
        
        # Internal Rate of Return (IRR) - simplified calculation
        # For more accurate IRR, would need to use scipy.optimize.newton
        irr = self._estimate_irr(net_cash_flows)
        
        # Payback Period
        payback_period = self._calculate_payback_period(cumulative_cash_flows)
        
        # Profitability Index
        total_capex = self.cost_structure.total_capex
        profitability_index = (npv + total_capex) / total_capex if total_capex > 0 else 0
        
        # Annual metrics
        annual_revenue = self.cost_structure.total_revenue
        annual_opex = self.cost_structure.total_opex
        annual_profit = annual_revenue - annual_opex
        annual_roi = (annual_profit / total_capex) * 100 if total_capex > 0 else 0
        
        # CO₂ metrics
        co2_avoided_tpy = self.project_params.co2_input_tpy
        cost_per_ton_co2_avoided = -npv / (co2_avoided_tpy * self.project_params.project_lifetime_years)
        revenue_per_ton_co = self.cost_structure.co_sales_revenue / self.project_params.co_output_tpy
        
        self.financial_metrics = {
            'npv_eur': npv,
            'irr_percent': irr,
            'payback_period_years': payback_period,
            'profitability_index': profitability_index,
            'annual_roi_percent': annual_roi,
            'cost_per_ton_co2_avoided_eur': cost_per_ton_co2_avoided,
            'revenue_per_ton_co_eur': revenue_per_ton_co,
            'total_capex_eur': total_capex,
            'annual_revenue_eur': annual_revenue,
            'annual_opex_eur': annual_opex,
            'annual_profit_eur': annual_profit
        }
        
        logger.info(f"Financial metrics for {self.project_params.project_name}:")
        logger.info(f"  NPV: €{npv:,.0f}")
        logger.info(f"  IRR: {irr:.1f}%")
        logger.info(f"  Payback Period: {payback_period:.1f} years")
        logger.info(f"  Annual ROI: {annual_roi:.1f}%")
        logger.info(f"  Cost per ton CO₂ avoided: €{cost_per_ton_co2_avoided:.2f}")
        
        return self.financial_metrics
    
    def _estimate_irr(self, cash_flows: List[float]) -> float:
        """Estimate IRR using simplified calculation"""
        # This is a simplified IRR calculation
        # For production use, consider using scipy.optimize.newton
        
        if len(cash_flows) < 2:
            return 0.0
        
        # Simple estimation based on average return
        total_investment = abs(sum([cf for cf in cash_flows if cf < 0]))
        total_return = sum([cf for cf in cash_flows if cf > 0])
        
        if total_investment == 0:
            return 0.0
        
        # Rough IRR estimation
        avg_return_per_year = total_return / len(cash_flows)
        irr = (avg_return_per_year / total_investment) * 100
        
        return min(irr, 100.0)  # Cap at 100%
    
    def _calculate_payback_period(self, cumulative_cash_flows: List[float]) -> float:
        """Calculate payback period in years"""
        
        for i, cumulative in enumerate(cumulative_cash_flows):
            if cumulative >= 0:
                return i
        
        return len(cumulative_cash_flows)  # Never pays back
    
    def export_financial_analysis(self, filename: str = None) -> str:
        """Export comprehensive financial analysis to CSV"""
        
        if not self.cash_flows:
            self.generate_cash_flows()
        
        if not self.financial_metrics:
            self.calculate_financial_metrics()
        
        # Create cash flow DataFrame
        cf_df = pd.DataFrame(self.cash_flows)
        
        # Create financial metrics DataFrame
        metrics_df = pd.DataFrame([self.financial_metrics])
        
        # Create summary DataFrame
        summary_data = {
            'Metric': [
                'Project Name', 'Site Name', 'CO₂ Input (TPY)', 'CO Output (TPY)',
                'Total CAPEX (€)', 'Annual OPEX (€)', 'Annual Revenue (€)',
                'NPV (€)', 'IRR (%)', 'Payback Period (years)', 'Annual ROI (%)'
            ],
            'Value': [
                self.project_params.project_name,
                self.project_params.site_name,
                self.project_params.co2_input_tpy,
                self.project_params.co_output_tpy,
                self.cost_structure.total_capex,
                self.cost_structure.total_opex,
                self.cost_structure.total_revenue,
                self.financial_metrics['npv_eur'],
                self.financial_metrics['irr_percent'],
                self.financial_metrics['payback_period_years'],
                self.financial_metrics['annual_roi_percent']
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"financial_analysis_{self.project_params.project_name}_{timestamp}.xlsx"
        
        # Export to Excel with multiple sheets
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            cf_df.to_excel(writer, sheet_name='Cash_Flows', index=False)
            metrics_df.to_excel(writer, sheet_name='Financial_Metrics', index=False)
        
        logger.info(f"Financial analysis exported to {filename}")
        return filename

# Example usage and testing
if __name__ == "__main__":
    # Create sample project
    project_params = ProjectParameters(
        project_name="Turnover Labs FOAK Pilot",
        site_name="BASF Ludwigshafen",
        co2_input_tpy=100,  # 100 TPY CO₂ input
        co_output_tpy=50,   # 50 TPY CO output
        project_lifetime_years=20,
        construction_period_years=2,
        ramp_up_period_years=1
    )
    
    # Initialize financial model
    model = FinancialModel(project_params)
    
    # Calculate CAPEX
    cost_structure = model.calculate_capex(equipment_cost=2000000)  # €2M equipment
    
    # Calculate OPEX
    model.calculate_opex(
        power_price_eur_mwh=75,
        power_consumption_mwh_per_ton_co=2.5,
        water_consumption_m3_per_ton_co=5,
        water_price_eur_m3=2,
        labor_hours_per_ton_co=10,
        labor_rate_eur_per_hour=35
    )
    
    # Calculate revenue
    model.calculate_revenue(co_price_eur_per_ton=800)  # €800/ton CO
    
    # Generate financial analysis
    cash_flows = model.generate_cash_flows()
    metrics = model.calculate_financial_metrics()
    
    # Export results
    filename = model.export_financial_analysis()
    print(f"Analysis exported to: {filename}")
