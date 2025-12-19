"""
TaxReady Nigeria - Tax Compliance Made Simple
MVP for Nigeria Tax Act 2025 (Effective January 1, 2026)

Single-file version for Streamlit Cloud deployment
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import json

# ============================================
# CONSTANTS (from utils/constants.py)
# ============================================

# 2026 Personal Income Tax Bands
TAX_BANDS_2026 = [
    {"min": 0, "max": 800_000, "rate": 0.00, "label": "First ₦800,000"},
    {"min": 800_000, "max": 3_000_000, "rate": 0.15, "label": "₦800,001 - ₦3,000,000"},
    {"min": 3_000_000, "max": 12_000_000, "rate": 0.18, "label": "₦3,000,001 - ₦12,000,000"},
    {"min": 12_000_000, "max": 25_000_000, "rate": 0.21, "label": "₦12,000,001 - ₦25,000,000"},
    {"min": 25_000_000, "max": 50_000_000, "rate": 0.23, "label": "₦25,000,001 - ₦50,000,000"},
    {"min": 50_000_000, "max": float('inf'), "rate": 0.25, "label": "Above ₦50,000,000"},
]

# Statutory Deduction Rates
PENSION_RATE = 0.08
NHF_RATE = 0.025
NHF_ANNUAL_CAP = 2_400
NHIS_RATE = 0.05

# Relief Caps
RENT_RELIEF_RATE = 0.20
RENT_RELIEF_CAP = 500_000
LIFE_ASSURANCE_CAP = 100_000

# Thresholds
SMALL_COMPANY_TURNOVER_LIMIT = 100_000_000
VAT_REGISTRATION_THRESHOLD = 25_000_000

# WHT Rates
WHT_RATES = {
    "professional_services": 0.10,
    "consultancy": 0.10,
    "technical_services": 0.10,
    "contracts": 0.05,
    "supplies": 0.05,
    "rent": 0.10,
}

# Penalties
PENALTIES = {
    "late_filing_first": 50_000,
    "late_filing_subsequent": 25_000,
    "unregistered_contractor": 5_000_000,
}

# Filing Deadlines
FILING_DEADLINES = {
    "paye_monthly": "10th of following month",
    "vat_monthly": "21st of following month",
    "annual_return": "Within 6 months of year end",
}

# Categories
EXPENSE_CATEGORIES = [
    "Office Rent/Workspace", "Utilities (Power, Water)", "Internet & Communications",
    "Equipment & Software", "Professional Subscriptions", "Accounting/Legal Fees",
    "Marketing & Advertising", "Travel & Transportation", "Subcontractor Payments",
    "Insurance", "Bank Charges", "Office Supplies", "Training & Development",
    "Other Business Expenses",
]

INCOME_CATEGORIES = [
    "Consulting/Professional Fees", "Contract Payments", "Retainer Income",
    "Project-Based Income", "Royalties/Licensing", "Training/Speaking Fees",
    "Other Business Income",
]

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


# ============================================
# PAYE CALCULATOR (from calculators/paye.py)
# ============================================

def calculate_pension(basic: float, housing: float, transport: float) -> float:
    pensionable = basic + housing + transport
    return pensionable * PENSION_RATE

def calculate_nhf(basic: float) -> float:
    nhf = basic * NHF_RATE
    return min(nhf, NHF_ANNUAL_CAP)

def calculate_nhis(basic: float) -> float:
    return basic * NHIS_RATE

def calculate_rent_relief(gross_income: float) -> float:
    relief = gross_income * RENT_RELIEF_RATE
    return min(relief, RENT_RELIEF_CAP)

def calculate_tax_on_income(taxable_income: float) -> dict:
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
    # Convert to annual
    basic_annual = basic_monthly * 12
    housing_annual = housing_monthly * 12
    transport_annual = transport_monthly * 12
    other_annual = other_allowances_monthly * 12
    
    gross_annual = basic_annual + housing_annual + transport_annual + other_annual + bonus_annual
    gross_monthly = gross_annual / 12
    
    deductions = {}
    total_deductions = 0
    
    if include_pension:
        pension = calculate_pension(basic_annual, housing_annual, transport_annual)
        deductions["Pension (8%)"] = pension
        total_deductions += pension
    
    if include_nhf:
        nhf = calculate_nhf(basic_annual)
        deductions["NHF (2.5%, capped)"] = nhf
        total_deductions += nhf
    
    if include_nhis:
        nhis = calculate_nhis(basic_annual)
        deductions["NHIS (5%)"] = nhis
        total_deductions += nhis
    
    rent_relief = calculate_rent_relief(gross_annual)
    deductions["Rent Relief (20%, max ₦500k)"] = rent_relief
    total_deductions += rent_relief
    
    life_assurance_relief = min(life_assurance, LIFE_ASSURANCE_CAP)
    if life_assurance_relief > 0:
        deductions["Life Assurance"] = life_assurance_relief
        total_deductions += life_assurance_relief
    
    if mortgage_interest > 0:
        deductions["Mortgage Interest"] = mortgage_interest
        total_deductions += mortgage_interest
    
    taxable_income = max(gross_annual - total_deductions, 0)
    tax_result = calculate_tax_on_income(taxable_income)
    annual_tax = tax_result["total_tax"]
    monthly_tax = annual_tax / 12
    effective_rate = (annual_tax / gross_annual * 100) if gross_annual > 0 else 0
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


# ============================================
# CONTRACTOR CALCULATOR (from calculators/contractor.py)
# ============================================

def calculate_contractor_tax(
    gross_revenue: float,
    business_expenses: dict = None,
    voluntary_pension: float = 0,
    life_assurance: float = 0,
    wht_credits: float = 0
) -> dict:
    if business_expenses is None:
        business_expenses = {}
    
    total_expenses = sum(business_expenses.values())
    gross_profit = gross_revenue - total_expenses
    
    reliefs = {}
    total_reliefs = 0
    
    rent_relief = min(gross_revenue * RENT_RELIEF_RATE, RENT_RELIEF_CAP)
    reliefs["Rent Relief (20%, max ₦500k)"] = rent_relief
    total_reliefs += rent_relief
    
    max_pension = gross_revenue * PENSION_RATE
    pension_relief = min(voluntary_pension, max_pension)
    if pension_relief > 0:
        reliefs["Voluntary Pension"] = pension_relief
        total_reliefs += pension_relief
    
    life_relief = min(life_assurance, LIFE_ASSURANCE_CAP)
    if life_relief > 0:
        reliefs["Life Assurance"] = life_relief
        total_reliefs += life_relief
    
    taxable_income = max(gross_profit - total_reliefs, 0)
    tax_result = calculate_tax_on_income(taxable_income)
    tax_before_credits = tax_result["total_tax"]
    
    net_tax_payable = max(tax_before_credits - wht_credits, 0)
    wht_refund = max(wht_credits - tax_before_credits, 0)
    
    effective_rate_revenue = (net_tax_payable / gross_revenue * 100) if gross_revenue > 0 else 0
    effective_rate_profit = (net_tax_payable / gross_profit * 100) if gross_profit > 0 else 0
    
    vat_registration_required = gross_revenue > VAT_REGISTRATION_THRESHOLD
    qualifies_small_company = gross_revenue <= SMALL_COMPANY_TURNOVER_LIMIT
    
    return {
        "revenue": {"gross_revenue": gross_revenue},
        "expenses": {"breakdown": business_expenses, "total": total_expenses},
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

def compare_salary_vs_contractor(gross_amount: float, expense_ratio: float = 0.3) -> dict:
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
    
    expenses = {"Estimated Business Expenses": gross_amount * expense_ratio}
    contractor_result = calculate_contractor_tax(
        gross_revenue=gross_amount,
        business_expenses=expenses,
        voluntary_pension=gross_amount * PENSION_RATE,
        wht_credits=gross_amount * 0.05
    )
    
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


# ============================================
# STREAMLIT APP
# ============================================

st.set_page_config(
    page_title="TaxReady Nigeria",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1B4D3E; margin-bottom: 0; }
    .sub-header { font-size: 1.1rem; color: #666; margin-top: 0; }
    .info-box { background-color: #D1ECF1; border-left: 4px solid #17A2B8; padding: 1rem; margin: 1rem 0; border-radius: 0 8px 8px 0; }
    .warning-box { background-color: #FFF3CD; border-left: 4px solid #FFC107; padding: 1rem; margin: 1rem 0; border-radius: 0 8px 8px 0; }
    .success-box { background-color: #D4EDDA; border-left: 4px solid #28A745; padding: 1rem; margin: 1rem 0; border-radius: 0 8px 8px 0; }
</style>
""", unsafe_allow_html=True)

def format_currency(amount: float) -> str:
    return f"₦{amount:,.2f}"

# Initialize session state
if 'records' not in st.session_state:
    st.session_state.records = {"income": [], "expenses": []}

# Sidebar
st.sidebar.markdown("## 🇳🇬 TaxReady Nigeria")
st.sidebar.markdown("*Tax Compliance Made Simple*")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "💼 Employee Calculator", "🧑‍💻 Contractor Calculator", 
     "⚖️ Compare Options", "📊 Record Keeper", "✅ Compliance Checklist", 
     "📚 Learn"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Key Dates")
st.sidebar.info("**PAYE:** 10th monthly\n\n**VAT:** 21st monthly\n\n**Annual:** Within 6 months")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ New Law Alert")
st.sidebar.warning("**Nigeria Tax Act 2025** takes effect **January 1, 2026**.\n\n• First ₦800K tax-free\n• CRA abolished → Rent Relief\n• ₦5M penalty for unregistered contractors")


# ============================================
# HOME PAGE
# ============================================
if page == "🏠 Home":
    st.markdown('<p class="main-header">🇳🇬 TaxReady Nigeria</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Navigate Nigeria\'s 2026 Tax Laws with Confidence</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    days_until = (date(2026, 1, 1) - date.today()).days
    if days_until > 0:
        st.warning(f"⏰ **{days_until} days** until the Nigeria Tax Act 2025 takes effect. Are you ready?")
    else:
        st.success("✅ The Nigeria Tax Act 2025 is now in effect!")
    
    st.markdown("### What's New in 2026?")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="info-box"><h4>💰 ₦800K Tax-Free</h4><p>First ₦800,000 of annual income is completely exempt from tax.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="info-box"><h4>🏠 New Rent Relief</h4><p>20% of gross income (max ₦500K) replaces the old CRA system.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="info-box"><h4>⚠️ Stricter Penalties</h4><p>₦5M fine for engaging unregistered contractors. TIN now mandatory.</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 2026 Tax Bands at a Glance")
    
    bands_df = pd.DataFrame([
        {"Income Band": "First ₦800,000", "Rate": "0%", "Cumulative Tax": "₦0"},
        {"Income Band": "₦800,001 - ₦3,000,000", "Rate": "15%", "Cumulative Tax": "₦330,000"},
        {"Income Band": "₦3,000,001 - ₦12,000,000", "Rate": "18%", "Cumulative Tax": "₦1,950,000"},
        {"Income Band": "₦12,000,001 - ₦25,000,000", "Rate": "21%", "Cumulative Tax": "₦4,680,000"},
        {"Income Band": "₦25,000,001 - ₦50,000,000", "Rate": "23%", "Cumulative Tax": "₦10,430,000"},
        {"Income Band": "Above ₦50,000,000", "Rate": "25%", "Cumulative Tax": "Continues..."},
    ])
    st.dataframe(bands_df, hide_index=True, use_container_width=True)


# ============================================
# EMPLOYEE CALCULATOR
# ============================================
elif page == "💼 Employee Calculator":
    st.markdown("## 💼 PAYE Calculator (Salary Earners)")
    st.markdown("Calculate your Pay-As-You-Earn tax under the **2026 tax bands**.")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 💵 Monthly Income")
        basic = st.number_input("Basic Salary (₦/month)", min_value=0, value=150000, step=10000)
        housing = st.number_input("Housing Allowance (₦/month)", min_value=0, value=75000, step=5000)
        transport = st.number_input("Transport Allowance (₦/month)", min_value=0, value=45000, step=5000)
        other = st.number_input("Other Allowances (₦/month)", min_value=0, value=30000, step=5000)
        bonus = st.number_input("Annual Bonus (₦/year)", min_value=0, value=0, step=50000)
        
        st.markdown("### 🛡️ Additional Reliefs")
        life_assurance = st.number_input("Life Assurance Premium (₦/year)", min_value=0, max_value=100000, value=0, step=10000)
        mortgage = st.number_input("Mortgage Interest (₦/year)", min_value=0, value=0, step=50000)
        
        st.markdown("### ⚙️ Deduction Options")
        include_pension = st.checkbox("Pension Contribution (8%)", value=True)
        include_nhf = st.checkbox("National Housing Fund (2.5%)", value=True)
        include_nhis = st.checkbox("NHIS (5%)", value=True)
    
    with col2:
        result = calculate_paye(
            basic_monthly=basic, housing_monthly=housing, transport_monthly=transport,
            other_allowances_monthly=other, bonus_annual=bonus, life_assurance=life_assurance,
            mortgage_interest=mortgage, include_pension=include_pension,
            include_nhf=include_nhf, include_nhis=include_nhis
        )
        
        st.markdown("### 📊 Tax Summary")
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Monthly PAYE", format_currency(result["monthly_tax"]))
            st.metric("Annual Tax", format_currency(result["annual_tax"]))
        with m2:
            st.metric("Effective Rate", f"{result['effective_rate']:.2f}%")
            st.metric("Monthly Take-Home", format_currency(result["net_monthly"]))
        
        st.markdown("---")
        st.markdown("#### 💰 Income Breakdown")
        income_df = pd.DataFrame([
            {"Component": "Basic Salary", "Annual": format_currency(result["income"]["basic_annual"])},
            {"Component": "Housing", "Annual": format_currency(result["income"]["housing_annual"])},
            {"Component": "Transport", "Annual": format_currency(result["income"]["transport_annual"])},
            {"Component": "Other Allowances", "Annual": format_currency(result["income"]["other_annual"])},
            {"Component": "Bonus", "Annual": format_currency(result["income"]["bonus_annual"])},
            {"Component": "**GROSS TOTAL**", "Annual": f"**{format_currency(result['income']['gross_annual'])}**"},
        ])
        st.dataframe(income_df, hide_index=True, use_container_width=True)
        
        st.markdown("#### ➖ Deductions")
        deductions_data = [{"Deduction": k, "Amount": format_currency(v)} for k, v in result["deductions"].items()]
        deductions_data.append({"Deduction": "**TOTAL**", "Amount": f"**{format_currency(result['total_deductions'])}**"})
        st.dataframe(pd.DataFrame(deductions_data), hide_index=True, use_container_width=True)
        
        st.info(f"**Taxable Income:** {format_currency(result['taxable_income'])}")
        
        st.markdown("#### 🧮 Tax by Band")
        tax_df = pd.DataFrame(result["tax_breakdown"])
        tax_df["taxable_amount"] = tax_df["taxable_amount"].apply(format_currency)
        tax_df["tax"] = tax_df["tax"].apply(format_currency)
        tax_df.columns = ["Tax Band", "Rate", "Taxable Amount", "Tax Due"]
        st.dataframe(tax_df, hide_index=True, use_container_width=True)


# ============================================
# CONTRACTOR CALCULATOR
# ============================================
elif page == "🧑‍💻 Contractor Calculator":
    st.markdown("## 🧑‍💻 Contractor Tax Calculator")
    st.markdown("Calculate your tax as an independent contractor or self-employed professional.")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 💵 Annual Revenue")
        gross_revenue = st.number_input("Total Annual Revenue (₦)", min_value=0, value=6000000, step=500000)
        
        st.markdown("### 📝 Business Expenses")
        expenses = {}
        with st.expander("Click to enter expenses", expanded=True):
            for i, cat in enumerate(EXPENSE_CATEGORIES[:8]):
                exp = st.number_input(f"{cat}", min_value=0, value=0, step=10000, key=f"exp_{i}")
                if exp > 0:
                    expenses[cat] = exp
        
        st.markdown("### 🛡️ Personal Reliefs")
        vol_pension = st.number_input("Voluntary Pension (₦/year)", min_value=0, max_value=int(gross_revenue * 0.08) if gross_revenue > 0 else 1000000, value=0, step=50000)
        life_assurance = st.number_input("Life Assurance (₦/year)", min_value=0, max_value=100000, value=0, step=10000, key="contractor_life")
        
        st.markdown("### 💳 WHT Credits")
        wht_credits = st.number_input("WHT Already Deducted (₦)", min_value=0, value=0, step=10000)
    
    with col2:
        result = calculate_contractor_tax(
            gross_revenue=gross_revenue, business_expenses=expenses,
            voluntary_pension=vol_pension, life_assurance=life_assurance, wht_credits=wht_credits
        )
        
        st.markdown("### 📊 Tax Summary")
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Net Tax Payable", format_currency(result["net_tax_payable"]))
            st.metric("Effective Rate", f"{result['effective_rate_revenue']:.2f}%")
        with m2:
            st.metric("Gross Profit", format_currency(result["gross_profit"]))
            st.metric("Profit Margin", f"{result['profit_margin']:.1f}%")
        
        if result["wht_refund"] > 0:
            st.success(f"💰 **WHT Refund Available:** {format_currency(result['wht_refund'])}")
        if result["vat_registration_required"]:
            st.warning("⚠️ **VAT Registration Required** - Turnover exceeds ₦25M")
        if result["qualifies_small_company"]:
            st.info("✅ Qualifies as **Small Company** (0% CIT if incorporated)")
        
        st.markdown("---")
        st.markdown("#### 📋 Calculation Breakdown")
        summary = [
            {"Item": "Gross Revenue", "Amount": format_currency(gross_revenue)},
            {"Item": "(-) Business Expenses", "Amount": format_currency(result["expenses"]["total"])},
            {"Item": "= Gross Profit", "Amount": format_currency(result["gross_profit"])},
            {"Item": "(-) Personal Reliefs", "Amount": format_currency(result["total_reliefs"])},
            {"Item": "= Taxable Income", "Amount": format_currency(result["taxable_income"])},
            {"Item": "Tax Before Credits", "Amount": format_currency(result["tax_before_credits"])},
            {"Item": "(-) WHT Credits", "Amount": format_currency(wht_credits)},
            {"Item": "**= Net Tax Payable**", "Amount": f"**{format_currency(result['net_tax_payable'])}**"},
        ]
        st.dataframe(pd.DataFrame(summary), hide_index=True, use_container_width=True)


# ============================================
# COMPARE OPTIONS
# ============================================
elif page == "⚖️ Compare Options":
    st.markdown("## ⚖️ Employee vs Contractor Comparison")
    st.markdown("See how your tax differs when receiving income as salary vs. contractor fees.")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        gross_amount = st.number_input("Total Annual Amount (₦)", min_value=1000000, value=6000000, step=500000)
        expense_ratio = st.slider("Business Expenses (%)", min_value=10, max_value=60, value=30)
        st.info("**Assumptions:**\n- Employee: 50/25/15/10 structure\n- Contractor: 5% WHT, 8% pension")
    
    with col2:
        result = compare_salary_vs_contractor(gross_amount, expense_ratio / 100)
        
        st.markdown("### 📊 Results")
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### 💼 As Employee")
            st.metric("Annual Tax", format_currency(result["employee"]["annual_tax"]))
            st.metric("Effective Rate", f"{result['employee']['effective_rate']:.2f}%")
            st.metric("Net Income", format_currency(result["employee"]["net_income"]))
        
        with c2:
            st.markdown("#### 🧑‍💻 As Contractor")
            st.metric("Annual Tax", format_currency(result["contractor"]["annual_tax"]))
            st.metric("Effective Rate", f"{result['contractor']['effective_rate']:.2f}%")
            st.metric("Net Income", format_currency(result["contractor"]["net_income"]))
        
        st.markdown("---")
        savings = result["tax_savings_as_contractor"]
        if savings > 0:
            st.success(f"### 💡 Recommendation: **Contractor**\n\nSave **{format_currency(savings)}** annually ({format_currency(savings/12)}/month)")
        else:
            st.info(f"### 💡 Recommendation: **Employee**\n\nPay **{format_currency(abs(savings))}** less in taxes")


# ============================================
# RECORD KEEPER
# ============================================
elif page == "📊 Record Keeper":
    st.markdown("## 📊 Record Keeper")
    st.markdown("Track income and expenses. Keep records for **6 years**.")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["💵 Add Income", "💸 Add Expense", "📋 View Records"])
    
    with tab1:
        st.markdown("### Add Income")
        ic1, ic2 = st.columns(2)
        with ic1:
            income_date = st.date_input("Date", value=date.today(), key="inc_date")
            income_category = st.selectbox("Category", INCOME_CATEGORIES)
            income_amount = st.number_input("Amount (₦)", min_value=0, value=0, step=1000, key="inc_amt")
        with ic2:
            income_client = st.text_input("Client/Source")
            income_wht = st.number_input("WHT Deducted (₦)", min_value=0, value=0, step=100)
        
        if st.button("➕ Add Income", type="primary"):
            if income_amount > 0:
                st.session_state.records["income"].append({
                    "date": str(income_date), "category": income_category,
                    "amount": income_amount, "client": income_client, "wht": income_wht
                })
                st.success("✅ Added!")
    
    with tab2:
        st.markdown("### Add Expense")
        ec1, ec2 = st.columns(2)
        with ec1:
            expense_date = st.date_input("Date", value=date.today(), key="exp_date")
            expense_category = st.selectbox("Category", EXPENSE_CATEGORIES)
            expense_amount = st.number_input("Amount (₦)", min_value=0, value=0, step=100, key="exp_amt")
        with ec2:
            expense_vendor = st.text_input("Vendor/Payee")
        
        if st.button("➕ Add Expense", type="primary"):
            if expense_amount > 0:
                st.session_state.records["expenses"].append({
                    "date": str(expense_date), "category": expense_category,
                    "amount": expense_amount, "vendor": expense_vendor
                })
                st.success("✅ Added!")
    
    with tab3:
        total_income = sum(r["amount"] for r in st.session_state.records["income"])
        total_expenses = sum(r["amount"] for r in st.session_state.records["expenses"])
        total_wht = sum(r.get("wht", 0) for r in st.session_state.records["income"])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Income", format_currency(total_income))
        m2.metric("Expenses", format_currency(total_expenses))
        m3.metric("Net Profit", format_currency(total_income - total_expenses))
        m4.metric("WHT Credits", format_currency(total_wht))
        
        if st.session_state.records["income"]:
            st.markdown("#### 💵 Income")
            st.dataframe(pd.DataFrame(st.session_state.records["income"]), hide_index=True, use_container_width=True)
        
        if st.session_state.records["expenses"]:
            st.markdown("#### 💸 Expenses")
            st.dataframe(pd.DataFrame(st.session_state.records["expenses"]), hide_index=True, use_container_width=True)


# ============================================
# COMPLIANCE CHECKLIST
# ============================================
elif page == "✅ Compliance Checklist":
    st.markdown("## ✅ Tax Compliance Checklist")
    st.markdown("---")
    
    st.markdown("### 📋 Registration")
    st.checkbox("TIN registered and verified")
    st.checkbox("Business registered with CAC (if applicable)")
    st.checkbox("VAT registered (if turnover > ₦25M)")
    st.checkbox("Pension RSA set up")
    
    st.markdown("### 📅 Monthly")
    current_month = MONTHS[datetime.now().month - 1]
    st.checkbox(f"PAYE remitted for {current_month}")
    st.checkbox(f"VAT filed for {current_month}")
    st.checkbox(f"WHT remitted for {current_month}")
    
    st.markdown("### 📆 Annual")
    st.checkbox("Annual tax return filed")
    st.checkbox("All WHT certificates collected")
    st.checkbox("Tax clearance certificate obtained")
    
    st.markdown("---")
    st.markdown("### ⚠️ Penalties")
    penalties_df = pd.DataFrame([
        {"Violation": "Late filing (first)", "Penalty": "₦50,000"},
        {"Violation": "Late filing (subsequent)", "Penalty": "₦25,000/month"},
        {"Violation": "Engaging unregistered contractor", "Penalty": "₦5,000,000"},
        {"Violation": "Failure to deduct WHT", "Penalty": "200% of amount"},
    ])
    st.dataframe(penalties_df, hide_index=True, use_container_width=True)


# ============================================
# LEARN
# ============================================
elif page == "📚 Learn":
    st.markdown("## 📚 Tax Knowledge Hub")
    st.markdown("---")
    
    topic = st.selectbox("Choose a topic:", [
        "What Changed in 2026?",
        "Understanding PAYE",
        "Contractor Tax Optimization",
        "Allowable Deductions",
        "WHT Explained",
        "Penalties to Avoid"
    ])
    
    if topic == "What Changed in 2026?":
        st.markdown("""
        ### Key Changes in Nigeria Tax Act 2025
        
        | Before (2025) | After (2026) |
        |---------------|--------------|
        | Tax-free: ~₦300K | Tax-free: **₦800K** |
        | CRA (complex) | Rent Relief (simple) |
        | Top rate at ₦3.2M | Top rate at ₦50M |
        | Max rate: 24% | Max rate: 25% |
        
        **For Businesses:**
        - Small companies (≤₦100M turnover): **0% CIT**
        - Medium companies (₦100M-₦500M): 20%
        - Large companies (>₦500M): 30%
        - **₦5M penalty** for engaging unregistered contractors
        """)
    
    elif topic == "Understanding PAYE":
        st.markdown("""
        ### PAYE Calculation Formula
        
        ```
        Gross Income
        - Pension (8%)
        - NHF (2.5% of basic, max ₦2,400/yr)
        - NHIS (5% of basic)
        - Rent Relief (20%, max ₦500K)
        = Taxable Income
        × Tax Rates (0% to 25%)
        = Annual Tax ÷ 12 = Monthly PAYE
        ```
        
        **Tips to reduce tax:**
        1. Ensure Rent Relief is applied
        2. Take life assurance (up to ₦100K deductible)
        3. Maximize pension contributions
        4. Claim mortgage interest if applicable
        """)
    
    elif topic == "Contractor Tax Optimization":
        st.markdown("""
        ### Contractor Advantages
        
        Unlike employees, contractors deduct ALL business expenses:
        - Office rent, utilities, internet
        - Equipment, software, subscriptions
        - Professional fees, training
        - Business travel
        
        **Optimization Formula:**
        ```
        Revenue - Expenses = Profit
        Profit - Reliefs = Taxable Income
        Tax - WHT Credits = Net Tax Payable
        ```
        
        **Key strategies:**
        1. Document EVERYTHING
        2. Collect ALL WHT certificates (valid 24 months)
        3. Contribute to voluntary pension (tax-deductible)
        """)
    
    elif topic == "Allowable Deductions":
        st.markdown("""
        ### Employee Deductions
        | Deduction | Rate/Cap |
        |-----------|----------|
        | Pension | 8% |
        | NHF | 2.5% (max ₦2,400/yr) |
        | NHIS | 5% |
        | Rent Relief | 20% (max ₦500K) |
        | Life Assurance | Max ₦100K |
        
        ### Contractor Deductions
        - All business expenses with receipts
        - Capital allowances (25%/yr for equipment)
        - Professional fees and subscriptions
        - Business travel and transport
        """)
    
    elif topic == "WHT Explained":
        st.markdown("""
        ### Withholding Tax Rates
        | Payment Type | Rate |
        |--------------|------|
        | Professional services | 10% |
        | Consultancy | 10% |
        | Contracts | 5% |
        | Supplies | 5% |
        | Rent | 10% |
        
        **Important:** WHT is a CREDIT, not final tax!
        
        If your actual tax < WHT deducted → You get a **refund**
        
        WHT certificates valid for **24 months**
        """)
    
    elif topic == "Penalties to Avoid":
        st.markdown("""
        ### Penalty Schedule
        | Violation | Penalty |
        |-----------|---------|
        | Late filing (first) | ₦50,000 |
        | Late filing (subsequent) | ₦25,000/month |
        | Unregistered contractor | **₦5,000,000** |
        | No TIN | Up to ₦50,000 |
        | Failure to deduct WHT | 200% of amount |
        | False returns | ₦500K + 5 years |
        """)


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.85rem;'>
TaxReady Nigeria | Built for Nigeria Tax Act 2025<br>
⚠️ Estimates only. Consult a tax professional for advice.<br>
© 2025 | Made with ❤️ for Nigerian businesses
</div>
""", unsafe_allow_html=True)
