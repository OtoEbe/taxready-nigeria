"""
PAYE Calculator for Salary Earners
Nigeria Tax Act 2025 - Effective January 1, 2026
"""

from utils.constants import (
    TAX_BANDS_2026, PENSION_RATE, NHF_RATE, NHF_ANNUAL_CAP,
    NHIS_RATE, RENT_RELIEF_RATE, RENT_RELIEF_CAP, LIFE_ASSURANCE_CAP
)


def calculate_pension(basic: float, housing: float, transport: float) -> float:
    """Calculate employee pension contribution (8% of pensionable earnings)"""
    pensionable = basic + housing + transport
    return pensionable * PENSION_RATE


def calculate_nhf(basic: float) -> float:
    """Calculate National Housing Fund (2.5% of basic, capped at ₦2,400/year)"""
    nhf = basic * NHF_RATE
    return min(nhf, NHF_ANNUAL_CAP)


def calculate_nhis(basic: float) -> float:
    """Calculate NHIS contribution (5% of basic)"""
    return basic * NHIS_RATE


def calculate_rent_relief(gross_income: float) -> float:
    """Calculate Rent Relief (20% of gross, max ₦500,000)"""
    relief = gross_income * RENT_RELIEF_RATE
    return min(relief, RENT_RELIEF_CAP)


def calculate_tax_on_income(taxable_income: float) -> dict:
    """
    Calculate tax using 2026 progressive bands.
    Returns breakdown by band and total tax.
    """
    remaining = taxable_income
    total_tax = 0
    breakdown = []
    
    for band in TAX_BANDS_2026:
        if remaining <= 0:
            breakdown.append({
                "band": band["label"],
                "rate": f"{band['rate']*100:.0f}%",
                "taxable_amount": 0,
                "tax": 0
            })
            continue
            
        # Calculate amount in this band
        band_size = band["max"] - band["min"]
        amount_in_band = min(remaining, band_size)
        tax_in_band = amount_in_band * band["rate"]
        
        breakdown.append({
            "band": band["label"],
            "rate": f"{band['rate']*100:.0f}%",
            "taxable_amount": amount_in_band,
            "tax": tax_in_band
        })
        
        total_tax += tax_in_band
        remaining -= amount_in_band
    
    return {
        "breakdown": breakdown,
        "total_tax": total_tax
    }


def calculate_paye(
    basic_monthly: float,
    housing_monthly: float = 0,
    transport_monthly: float = 0,
    other_allowances_monthly: float = 0,
    bonus_annual: float = 0,
    life_assurance: float = 0,
    mortgage_interest: float = 0,
    include_pension: bool = True,
    include_nhf: bool = True,
    include_nhis: bool = True
) -> dict:
    """
    Calculate complete PAYE for an employee.
    
    Args:
        basic_monthly: Monthly basic salary
        housing_monthly: Monthly housing allowance
        transport_monthly: Monthly transport allowance
        other_allowances_monthly: Other monthly allowances
        bonus_annual: Annual bonus
        life_assurance: Annual life assurance premium paid
        mortgage_interest: Annual mortgage interest paid
        include_pension: Whether employee contributes to pension
        include_nhf: Whether NHF applies
        include_nhis: Whether NHIS applies
    
    Returns:
        Complete calculation breakdown
    """
    # Convert to annual
    basic_annual = basic_monthly * 12
    housing_annual = housing_monthly * 12
    transport_annual = transport_monthly * 12
    other_annual = other_allowances_monthly * 12
    
    # Gross income
    gross_annual = basic_annual + housing_annual + transport_annual + other_annual + bonus_annual
    gross_monthly = gross_annual / 12
    
    # Calculate deductions
    deductions = {}
    total_deductions = 0
    
    # Pension
    if include_pension:
        pension = calculate_pension(basic_annual, housing_annual, transport_annual)
        deductions["Pension (8%)"] = pension
        total_deductions += pension
    
    # NHF
    if include_nhf:
        nhf = calculate_nhf(basic_annual)
        deductions["NHF (2.5%, capped)"] = nhf
        total_deductions += nhf
    
    # NHIS
    if include_nhis:
        nhis = calculate_nhis(basic_annual)
        deductions["NHIS (5%)"] = nhis
        total_deductions += nhis
    
    # Rent Relief (automatic under 2026 rules)
    rent_relief = calculate_rent_relief(gross_annual)
    deductions["Rent Relief (20%, max ₦500k)"] = rent_relief
    total_deductions += rent_relief
    
    # Life Assurance
    life_assurance_relief = min(life_assurance, LIFE_ASSURANCE_CAP)
    if life_assurance_relief > 0:
        deductions["Life Assurance"] = life_assurance_relief
        total_deductions += life_assurance_relief
    
    # Mortgage Interest
    if mortgage_interest > 0:
        deductions["Mortgage Interest"] = mortgage_interest
        total_deductions += mortgage_interest
    
    # Taxable Income
    taxable_income = max(gross_annual - total_deductions, 0)
    
    # Calculate tax
    tax_result = calculate_tax_on_income(taxable_income)
    annual_tax = tax_result["total_tax"]
    monthly_tax = annual_tax / 12
    
    # Effective rate
    effective_rate = (annual_tax / gross_annual * 100) if gross_annual > 0 else 0
    
    # Net income
    net_annual = gross_annual - annual_tax
    net_monthly = net_annual / 12
    
    return {
        "income": {
            "basic_annual": basic_annual,
            "housing_annual": housing_annual,
            "transport_annual": transport_annual,
            "other_annual": other_annual,
            "bonus_annual": bonus_annual,
            "gross_annual": gross_annual,
            "gross_monthly": gross_monthly,
        },
        "deductions": deductions,
        "total_deductions": total_deductions,
        "taxable_income": taxable_income,
        "tax_breakdown": tax_result["breakdown"],
        "annual_tax": annual_tax,
        "monthly_tax": monthly_tax,
        "effective_rate": effective_rate,
        "net_annual": net_annual,
        "net_monthly": net_monthly,
    }
