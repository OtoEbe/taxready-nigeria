"""
Tax Calculator for Independent Contractors / Self-Employed
Nigeria Tax Act 2025 - Effective January 1, 2026
"""

from utils.constants import (
    TAX_BANDS_2026, RENT_RELIEF_RATE, RENT_RELIEF_CAP,
    LIFE_ASSURANCE_CAP, PENSION_RATE, WHT_RATES,
    SMALL_COMPANY_TURNOVER_LIMIT, VAT_REGISTRATION_THRESHOLD
)


def calculate_tax_on_income(taxable_income: float) -> dict:
    """Calculate tax using 2026 progressive bands."""
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
    
    return {"breakdown": breakdown, "total_tax": total_tax}


def calculate_contractor_tax(
    gross_revenue: float,
    business_expenses: dict = None,
    voluntary_pension: float = 0,
    life_assurance: float = 0,
    wht_credits: float = 0
) -> dict:
    """
    Calculate tax for independent contractor/self-employed person.
    
    Args:
        gross_revenue: Total annual business revenue
        business_expenses: Dict of expense category -> amount
        voluntary_pension: Voluntary pension contribution
        life_assurance: Life assurance premium paid
        wht_credits: Withholding tax already deducted by clients
    
    Returns:
        Complete calculation breakdown
    """
    if business_expenses is None:
        business_expenses = {}
    
    # Total business expenses
    total_expenses = sum(business_expenses.values())
    
    # Gross Profit
    gross_profit = gross_revenue - total_expenses
    
    # Personal Reliefs
    reliefs = {}
    total_reliefs = 0
    
    # Rent Relief (20% of gross revenue, max ₦500k)
    rent_relief = min(gross_revenue * RENT_RELIEF_RATE, RENT_RELIEF_CAP)
    reliefs["Rent Relief (20%, max ₦500k)"] = rent_relief
    total_reliefs += rent_relief
    
    # Voluntary Pension (max 8% of income)
    max_pension = gross_revenue * PENSION_RATE
    pension_relief = min(voluntary_pension, max_pension)
    if pension_relief > 0:
        reliefs["Voluntary Pension"] = pension_relief
        total_reliefs += pension_relief
    
    # Life Assurance (max ₦100k)
    life_relief = min(life_assurance, LIFE_ASSURANCE_CAP)
    if life_relief > 0:
        reliefs["Life Assurance"] = life_relief
        total_reliefs += life_relief
    
    # Taxable Income
    taxable_income = max(gross_profit - total_reliefs, 0)
    
    # Calculate Tax
    tax_result = calculate_tax_on_income(taxable_income)
    tax_before_credits = tax_result["total_tax"]
    
    # Apply WHT Credits
    net_tax_payable = max(tax_before_credits - wht_credits, 0)
    wht_refund = max(wht_credits - tax_before_credits, 0)
    
    # Effective Rates
    effective_rate_revenue = (net_tax_payable / gross_revenue * 100) if gross_revenue > 0 else 0
    effective_rate_profit = (net_tax_payable / gross_profit * 100) if gross_profit > 0 else 0
    
    # VAT Status
    vat_registration_required = gross_revenue > VAT_REGISTRATION_THRESHOLD
    
    # Small Company Status (if incorporated)
    qualifies_small_company = gross_revenue <= SMALL_COMPANY_TURNOVER_LIMIT
    
    return {
        "revenue": {
            "gross_revenue": gross_revenue,
        },
        "expenses": {
            "breakdown": business_expenses,
            "total": total_expenses,
        },
        "gross_profit": gross_profit,
        "reliefs": reliefs,
        "total_reliefs": total_reliefs,
        "taxable_income": taxable_income,
        "tax_breakdown": tax_result["breakdown"],
        "tax_before_credits": tax_before_credits,
        "wht_credits": wht_credits,
        "net_tax_payable": net_tax_payable,
        "wht_refund": wht_refund,
        "effective_rate_revenue": effective_rate_revenue,
        "effective_rate_profit": effective_rate_profit,
        "vat_registration_required": vat_registration_required,
        "qualifies_small_company": qualifies_small_company,
        "profit_margin": (gross_profit / gross_revenue * 100) if gross_revenue > 0 else 0,
    }


def calculate_wht_on_payment(amount: float, payment_type: str) -> dict:
    """
    Calculate WHT to be deducted on a payment.
    
    Args:
        amount: Payment amount
        payment_type: Type of payment (from WHT_RATES keys)
    
    Returns:
        WHT amount and net payment
    """
    rate = WHT_RATES.get(payment_type, 0.05)
    wht_amount = amount * rate
    net_payment = amount - wht_amount
    
    return {
        "gross_amount": amount,
        "wht_rate": rate,
        "wht_amount": wht_amount,
        "net_payment": net_payment,
    }


def compare_salary_vs_contractor(
    gross_amount: float,
    expense_ratio: float = 0.3
) -> dict:
    """
    Compare tax implications of receiving income as salary vs contractor.
    
    Args:
        gross_amount: Annual gross amount
        expense_ratio: Estimated business expenses as % of revenue (for contractor)
    
    Returns:
        Comparison of both scenarios
    """
    from calculators.paye import calculate_paye
    
    # Scenario 1: As Employee (assume standard structure)
    monthly = gross_amount / 12
    basic = monthly * 0.5
    housing = monthly * 0.25
    transport = monthly * 0.15
    other = monthly * 0.10
    
    employee_result = calculate_paye(
        basic_monthly=basic,
        housing_monthly=housing,
        transport_monthly=transport,
        other_allowances_monthly=other
    )
    
    # Scenario 2: As Contractor
    expenses = {"Estimated Business Expenses": gross_amount * expense_ratio}
    contractor_result = calculate_contractor_tax(
        gross_revenue=gross_amount,
        business_expenses=expenses,
        voluntary_pension=gross_amount * PENSION_RATE,
        wht_credits=gross_amount * 0.05  # Assume 5% WHT deducted
    )
    
    # Calculate difference
    employee_tax = employee_result["annual_tax"]
    contractor_tax = contractor_result["net_tax_payable"]
    tax_difference = employee_tax - contractor_tax
    
    return {
        "gross_amount": gross_amount,
        "employee": {
            "annual_tax": employee_tax,
            "effective_rate": employee_result["effective_rate"],
            "net_income": employee_result["net_annual"],
        },
        "contractor": {
            "annual_tax": contractor_tax,
            "effective_rate": contractor_result["effective_rate_revenue"],
            "net_income": gross_amount - contractor_tax,
            "expenses_claimed": gross_amount * expense_ratio,
        },
        "tax_savings_as_contractor": tax_difference,
        "recommendation": "Contractor" if tax_difference > 0 else "Employee",
    }
