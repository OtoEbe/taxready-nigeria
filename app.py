"""
TaxReady Nigeria - Tax Compliance Made Simple
MVP for Nigeria Tax Act 2025 (Effective January 1, 2026)

Enhanced UI Version with Professional Homepage
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import json

# ============================================
# CONSTANTS
# ============================================

TAX_BANDS_2026 = [
    {"min": 0, "max": 800_000, "rate": 0.00, "label": "First ₦800,000"},
    {"min": 800_000, "max": 3_000_000, "rate": 0.15, "label": "₦800,001 - ₦3,000,000"},
    {"min": 3_000_000, "max": 12_000_000, "rate": 0.18, "label": "₦3,000,001 - ₦12,000,000"},
    {"min": 12_000_000, "max": 25_000_000, "rate": 0.21, "label": "₦12,000,001 - ₦25,000,000"},
    {"min": 25_000_000, "max": 50_000_000, "rate": 0.23, "label": "₦25,000,001 - ₦50,000,000"},
    {"min": 50_000_000, "max": float('inf'), "rate": 0.25, "label": "Above ₦50,000,000"},
]

PENSION_RATE = 0.08
NHF_RATE = 0.025
NHF_ANNUAL_CAP = 2_400
NHIS_RATE = 0.05
RENT_RELIEF_RATE = 0.20
RENT_RELIEF_CAP = 500_000
LIFE_ASSURANCE_CAP = 100_000
SMALL_COMPANY_TURNOVER_LIMIT = 100_000_000
VAT_REGISTRATION_THRESHOLD = 25_000_000

WHT_RATES = {
    "professional_services": 0.10, "consultancy": 0.10, "technical_services": 0.10,
    "contracts": 0.05, "supplies": 0.05, "rent": 0.10,
}

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
# CALCULATOR FUNCTIONS
# ============================================

def calculate_pension(basic, housing, transport):
    return (basic + housing + transport) * PENSION_RATE

def calculate_nhf(basic):
    return min(basic * NHF_RATE, NHF_ANNUAL_CAP)

def calculate_nhis(basic):
    return basic * NHIS_RATE

def calculate_rent_relief(gross_income):
    return min(gross_income * RENT_RELIEF_RATE, RENT_RELIEF_CAP)

def calculate_tax_on_income(taxable_income):
    remaining = taxable_income
    total_tax = 0
    breakdown = []
    
    for band in TAX_BANDS_2026:
        if remaining <= 0:
            breakdown.append({"band": band["label"], "rate": f"{band['rate']*100:.0f}%", "taxable_amount": 0, "tax": 0})
            continue
        band_size = band["max"] - band["min"]
        amount_in_band = min(remaining, band_size)
        tax_in_band = amount_in_band * band["rate"]
        breakdown.append({"band": band["label"], "rate": f"{band['rate']*100:.0f}%", "taxable_amount": amount_in_band, "tax": tax_in_band})
        total_tax += tax_in_band
        remaining -= amount_in_band
    
    return {"breakdown": breakdown, "total_tax": total_tax}

def calculate_paye(basic_monthly, housing_monthly=0, transport_monthly=0, other_allowances_monthly=0,
                   bonus_annual=0, life_assurance=0, mortgage_interest=0,
                   include_pension=True, include_nhf=True, include_nhis=True):
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
    
    if life_assurance > 0:
        life_relief = min(life_assurance, LIFE_ASSURANCE_CAP)
        deductions["Life Assurance"] = life_relief
        total_deductions += life_relief
    if mortgage_interest > 0:
        deductions["Mortgage Interest"] = mortgage_interest
        total_deductions += mortgage_interest
    
    taxable_income = max(gross_annual - total_deductions, 0)
    tax_result = calculate_tax_on_income(taxable_income)
    annual_tax = tax_result["total_tax"]
    monthly_tax = annual_tax / 12
    effective_rate = (annual_tax / gross_annual * 100) if gross_annual > 0 else 0
    
    return {
        "income": {"basic_annual": basic_annual, "housing_annual": housing_annual, "transport_annual": transport_annual,
                   "other_annual": other_annual, "bonus_annual": bonus_annual, "gross_annual": gross_annual, "gross_monthly": gross_monthly},
        "deductions": deductions, "total_deductions": total_deductions, "taxable_income": taxable_income,
        "tax_breakdown": tax_result["breakdown"], "annual_tax": annual_tax, "monthly_tax": monthly_tax,
        "effective_rate": effective_rate, "net_annual": gross_annual - annual_tax, "net_monthly": (gross_annual - annual_tax) / 12,
    }

def calculate_contractor_tax(gross_revenue, business_expenses=None, voluntary_pension=0, life_assurance=0, wht_credits=0):
    if business_expenses is None:
        business_expenses = {}
    total_expenses = sum(business_expenses.values())
    gross_profit = gross_revenue - total_expenses
    
    reliefs = {}
    total_reliefs = 0
    rent_relief = min(gross_revenue * RENT_RELIEF_RATE, RENT_RELIEF_CAP)
    reliefs["Rent Relief"] = rent_relief
    total_reliefs += rent_relief
    
    if voluntary_pension > 0:
        pension_relief = min(voluntary_pension, gross_revenue * PENSION_RATE)
        reliefs["Voluntary Pension"] = pension_relief
        total_reliefs += pension_relief
    if life_assurance > 0:
        life_relief = min(life_assurance, LIFE_ASSURANCE_CAP)
        reliefs["Life Assurance"] = life_relief
        total_reliefs += life_relief
    
    taxable_income = max(gross_profit - total_reliefs, 0)
    tax_result = calculate_tax_on_income(taxable_income)
    tax_before_credits = tax_result["total_tax"]
    net_tax_payable = max(tax_before_credits - wht_credits, 0)
    wht_refund = max(wht_credits - tax_before_credits, 0)
    
    return {
        "revenue": {"gross_revenue": gross_revenue}, "expenses": {"breakdown": business_expenses, "total": total_expenses},
        "gross_profit": gross_profit, "reliefs": reliefs, "total_reliefs": total_reliefs, "taxable_income": taxable_income,
        "tax_breakdown": tax_result["breakdown"], "tax_before_credits": tax_before_credits, "wht_credits": wht_credits,
        "net_tax_payable": net_tax_payable, "wht_refund": wht_refund,
        "effective_rate_revenue": (net_tax_payable / gross_revenue * 100) if gross_revenue > 0 else 0,
        "effective_rate_profit": (net_tax_payable / gross_profit * 100) if gross_profit > 0 else 0,
        "vat_registration_required": gross_revenue > VAT_REGISTRATION_THRESHOLD,
        "qualifies_small_company": gross_revenue <= SMALL_COMPANY_TURNOVER_LIMIT,
        "profit_margin": (gross_profit / gross_revenue * 100) if gross_revenue > 0 else 0,
    }

def compare_salary_vs_contractor(gross_amount, expense_ratio=0.3):
    monthly = gross_amount / 12
    employee_result = calculate_paye(monthly * 0.5, monthly * 0.25, monthly * 0.15, monthly * 0.10)
    expenses = {"Business Expenses": gross_amount * expense_ratio}
    contractor_result = calculate_contractor_tax(gross_amount, expenses, gross_amount * PENSION_RATE, 0, gross_amount * 0.05)
    
    employee_tax = employee_result["annual_tax"]
    contractor_tax = contractor_result["net_tax_payable"]
    
    return {
        "gross_amount": gross_amount,
        "employee": {"annual_tax": employee_tax, "effective_rate": employee_result["effective_rate"], "net_income": employee_result["net_annual"]},
        "contractor": {"annual_tax": contractor_tax, "effective_rate": contractor_result["effective_rate_revenue"], "net_income": gross_amount - contractor_tax},
        "tax_savings_as_contractor": employee_tax - contractor_tax,
        "recommendation": "Contractor" if employee_tax > contractor_tax else "Employee",
    }

def format_currency(amount):
    return f"₦{amount:,.0f}"


# ============================================
# PAGE CONFIG & STYLES
# ============================================

st.set_page_config(page_title="TaxReady Nigeria", page_icon="🇳🇬", layout="wide", initial_sidebar_state="expanded")

# Calculate days until deadline
days_until = (date(2026, 1, 1) - date.today()).days
deadline_passed = days_until <= 0

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

.block-container { padding-top: 1rem; padding-bottom: 1rem; }

/* Hero Section */
.hero-container {
    background: linear-gradient(135deg, #0A2F1F 0%, #1B4D3E 50%, #2E7D5B 100%);
    border-radius: 20px;
    padding: 3rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 60%;
    height: 200%;
    background: radial-gradient(ellipse, rgba(255,255,255,0.1) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    color: #7FFFD4;
    padding: 0.4rem 1rem;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    color: white;
    line-height: 1.1;
    margin-bottom: 1rem;
}
.hero-subtitle {
    font-size: 1.25rem;
    color: rgba(255,255,255,0.85);
    margin-bottom: 2rem;
    line-height: 1.6;
    max-width: 600px;
}
.hero-cta {
    display: inline-block;
    background: #FFD700;
    color: #0A2F1F;
    padding: 1rem 2rem;
    border-radius: 10px;
    font-weight: 700;
    font-size: 1.1rem;
    text-decoration: none;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(255,215,0,0.3);
}
.hero-cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255,215,0,0.4);
}
.hero-stats {
    display: flex;
    gap: 2rem;
    margin-top: 2rem;
}
.hero-stat {
    text-align: left;
}
.hero-stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #7FFFD4;
}
.hero-stat-label {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.7);
}

/* Countdown */
.countdown-container {
    background: linear-gradient(90deg, #FF6B35 0%, #F7931E 100%);
    border-radius: 12px;
    padding: 1.25rem 2rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.countdown-text {
    color: white;
    font-weight: 600;
    font-size: 1.1rem;
}
.countdown-timer {
    display: flex;
    gap: 0.75rem;
}
.countdown-box {
    background: rgba(255,255,255,0.2);
    border-radius: 8px;
    padding: 0.5rem 1rem;
    text-align: center;
    min-width: 70px;
}
.countdown-number {
    font-size: 1.75rem;
    font-weight: 800;
    color: white;
}
.countdown-label {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.9);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Feature Cards */
.features-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin: 2rem 0;
}
.feature-card {
    background: white;
    border-radius: 16px;
    padding: 1.75rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border: 1px solid #f0f0f0;
    transition: all 0.3s;
}
.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.1);
}
.feature-icon {
    width: 56px;
    height: 56px;
    background: linear-gradient(135deg, #1B4D3E 0%, #2E7D5B 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-bottom: 1rem;
}
.feature-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.5rem;
}
.feature-desc {
    color: #666;
    font-size: 0.95rem;
    line-height: 1.5;
}

/* Quick Calculator */
.quick-calc-container {
    background: #f8fafc;
    border-radius: 20px;
    padding: 2rem;
    margin: 2rem 0;
    border: 2px solid #e2e8f0;
}
.quick-calc-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1B4D3E;
    margin-bottom: 0.5rem;
}
.quick-calc-subtitle {
    color: #64748b;
    margin-bottom: 1.5rem;
}
.result-card {
    background: linear-gradient(135deg, #1B4D3E 0%, #2E7D5B 100%);
    border-radius: 16px;
    padding: 1.5rem;
    color: white;
    text-align: center;
}
.result-label {
    font-size: 0.9rem;
    opacity: 0.85;
    margin-bottom: 0.25rem;
}
.result-value {
    font-size: 2rem;
    font-weight: 800;
}
.result-sub {
    font-size: 0.85rem;
    opacity: 0.75;
    margin-top: 0.5rem;
}

/* Tax Bands Table */
.bands-container {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    margin: 2rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}
.bands-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1B4D3E;
    margin-bottom: 1.5rem;
}

/* Trust Section */
.trust-container {
    background: #f8fafc;
    border-radius: 16px;
    padding: 2rem;
    margin: 2rem 0;
    text-align: center;
}
.trust-badges {
    display: flex;
    justify-content: center;
    gap: 3rem;
    flex-wrap: wrap;
}
.trust-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #475569;
    font-size: 0.95rem;
}
.trust-badge-icon {
    color: #1B4D3E;
    font-size: 1.25rem;
}

/* CTA Section */
.cta-container {
    background: linear-gradient(135deg, #0A2F1F 0%, #1B4D3E 100%);
    border-radius: 20px;
    padding: 3rem;
    text-align: center;
    margin: 2rem 0;
}
.cta-title {
    font-size: 2rem;
    font-weight: 700;
    color: white;
    margin-bottom: 0.75rem;
}
.cta-subtitle {
    color: rgba(255,255,255,0.8);
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
}

/* Section Headers */
.section-header {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1B4D3E;
    margin: 2.5rem 0 1.5rem;
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem 0;
    color: #64748b;
    font-size: 0.9rem;
    border-top: 1px solid #e2e8f0;
    margin-top: 3rem;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A2F1F 0%, #1B4D3E 100%);
}
section[data-testid="stSidebar"] .stMarkdown { color: white; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2); }

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)


# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown("## 🇳🇬 TaxReady")
    st.markdown("*Nigeria Tax Compliance*")
    st.markdown("---")
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "💼 Employee Calculator", "🧑‍💻 Contractor Calculator", 
         "⚖️ Compare Options", "📊 Record Keeper", "✅ Compliance Checklist", "📚 Learn"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("#### 📅 Key Deadlines")
    st.markdown("""
    <small>
    • PAYE: 10th monthly<br>
    • VAT: 21st monthly<br>
    • Annual: 6 months after year-end
    </small>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### 💬 Feedback")
    st.markdown("<small>Help us improve!</small>", unsafe_allow_html=True)
    st.markdown("[Share Feedback →](https://forms.gle)")


# ============================================
# HOME PAGE
# ============================================

if page == "🏠 Home":
    
    # Hero Section
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-badge">🚀 Nigeria Tax Act 2025 Ready</div>
        <h1 class="hero-title">Know Exactly What<br>You'll Pay in 2026</h1>
        <p class="hero-subtitle">
            Nigeria's biggest tax reform in decades takes effect January 1st. 
            Calculate your taxes, optimize your structure, and stay compliant — all in one place.
        </p>
        <div class="hero-stats">
            <div class="hero-stat">
                <div class="hero-stat-value">₦800K</div>
                <div class="hero-stat-label">New Tax-Free Threshold</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-value">6 Bands</div>
                <div class="hero-stat-label">Progressive Tax System</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-value">₦5M</div>
                <div class="hero-stat-label">Penalty for Non-Compliance</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Countdown Timer
    if not deadline_passed:
        hours = 0
        minutes = 0
        st.markdown(f"""
        <div class="countdown-container">
            <div class="countdown-text">⏰ New tax law takes effect in:</div>
            <div class="countdown-timer">
                <div class="countdown-box">
                    <div class="countdown-number">{days_until}</div>
                    <div class="countdown-label">Days</div>
                </div>
                <div class="countdown-box">
                    <div class="countdown-number">{hours}</div>
                    <div class="countdown-label">Hours</div>
                </div>
                <div class="countdown-box">
                    <div class="countdown-number">{minutes}</div>
                    <div class="countdown-label">Minutes</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="countdown-container" style="background: linear-gradient(90deg, #1B4D3E 0%, #2E7D5B 100%);">
            <div class="countdown-text">✅ Nigeria Tax Act 2025 is now in effect!</div>
            <div style="color: white; font-weight: 600;">Calculate your taxes below</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature Cards
    st.markdown("""
    <div class="features-grid">
        <div class="feature-card">
            <div class="feature-icon">🧮</div>
            <div class="feature-title">Instant Tax Calculator</div>
            <div class="feature-desc">Calculate your PAYE or contractor tax in seconds with the 2026 bands already built in.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⚖️</div>
            <div class="feature-title">Salary vs Contractor</div>
            <div class="feature-desc">See exactly how much you'd save as an employee versus an independent contractor.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <div class="feature-title">Compliance Checklist</div>
            <div class="feature-desc">Never miss a deadline. Track your TIN, filings, and avoid costly penalties.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Calculator Section
    st.markdown("""
    <div class="quick-calc-container">
        <div class="quick-calc-title">⚡ Quick Tax Estimate</div>
        <div class="quick-calc-subtitle">Enter your monthly salary to see your 2026 tax instantly</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        quick_salary = st.slider("Monthly Gross Salary (₦)", min_value=50000, max_value=2000000, value=400000, step=25000, format="₦%d")
    
    # Quick calculation
    quick_result = calculate_paye(quick_salary * 0.5, quick_salary * 0.25, quick_salary * 0.15, quick_salary * 0.10)
    
    with col2:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Your Monthly PAYE</div>
            <div class="result-value">{format_currency(quick_result['monthly_tax'])}</div>
            <div class="result-sub">Effective rate: {quick_result['effective_rate']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    qc1, qc2, qc3 = st.columns(3)
    with qc1:
        st.metric("Annual Gross", format_currency(quick_result['income']['gross_annual']))
    with qc2:
        st.metric("Annual Tax", format_currency(quick_result['annual_tax']))
    with qc3:
        st.metric("Annual Take-Home", format_currency(quick_result['net_annual']))
    
    # Tax Bands
    st.markdown('<h2 class="section-header">📊 2026 Tax Bands</h2>', unsafe_allow_html=True)
    
    bands_df = pd.DataFrame([
        {"Income Band": "First ₦800,000", "Rate": "0%", "Tax on Band": "₦0", "Cumulative": "₦0"},
        {"Income Band": "₦800,001 - ₦3,000,000", "Rate": "15%", "Tax on Band": "₦330,000", "Cumulative": "₦330,000"},
        {"Income Band": "₦3,000,001 - ₦12,000,000", "Rate": "18%", "Tax on Band": "₦1,620,000", "Cumulative": "₦1,950,000"},
        {"Income Band": "₦12,000,001 - ₦25,000,000", "Rate": "21%", "Tax on Band": "₦2,730,000", "Cumulative": "₦4,680,000"},
        {"Income Band": "₦25,000,001 - ₦50,000,000", "Rate": "23%", "Tax on Band": "₦5,750,000", "Cumulative": "₦10,430,000"},
        {"Income Band": "Above ₦50,000,000", "Rate": "25%", "Tax on Band": "Continues", "Cumulative": "—"},
    ])
    st.dataframe(bands_df, hide_index=True, use_container_width=True)
    
    # Trust Section
    st.markdown("""
    <div class="trust-container">
        <div class="trust-badges">
            <div class="trust-badge">
                <span class="trust-badge-icon">✓</span>
                <span>Based on Nigeria Tax Act 2025</span>
            </div>
            <div class="trust-badge">
                <span class="trust-badge-icon">✓</span>
                <span>Updated for January 2026</span>
            </div>
            <div class="trust-badge">
                <span class="trust-badge-icon">✓</span>
                <span>Built by Tax Professionals</span>
            </div>
            <div class="trust-badge">
                <span class="trust-badge-icon">✓</span>
                <span>100% Free to Use</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Section
    st.markdown("""
    <div class="cta-container">
        <div class="cta-title">Ready to Calculate Your 2026 Taxes?</div>
        <div class="cta-subtitle">Get your personalized tax breakdown in under 60 seconds</div>
    </div>
    """, unsafe_allow_html=True)
    
    cta_col1, cta_col2, cta_col3 = st.columns([1, 1, 1])
    with cta_col1:
        if st.button("💼 I'm an Employee", use_container_width=True, type="primary"):
            st.session_state.nav = "employee"
            st.rerun()
    with cta_col2:
        if st.button("🧑‍💻 I'm a Contractor", use_container_width=True, type="primary"):
            st.session_state.nav = "contractor"
            st.rerun()
    with cta_col3:
        if st.button("⚖️ Help Me Decide", use_container_width=True, type="secondary"):
            st.session_state.nav = "compare"
            st.rerun()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p><strong>TaxReady Nigeria</strong> — Navigate the 2026 tax laws with confidence</p>
        <p>⚠️ This tool provides estimates only. Consult a qualified tax professional for advice.</p>
        <p>© 2025 TaxReady Nigeria. Made with ❤️ for Nigerian businesses.</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# EMPLOYEE CALCULATOR
# ============================================

elif page == "💼 Employee Calculator":
    st.markdown("## 💼 PAYE Calculator")
    st.markdown("Calculate your 2026 Pay-As-You-Earn tax with all deductions applied.")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 💵 Monthly Income")
        basic = st.number_input("Basic Salary", min_value=0, value=150000, step=10000, format="%d")
        housing = st.number_input("Housing Allowance", min_value=0, value=75000, step=5000, format="%d")
        transport = st.number_input("Transport Allowance", min_value=0, value=45000, step=5000, format="%d")
        other = st.number_input("Other Allowances", min_value=0, value=30000, step=5000, format="%d")
        bonus = st.number_input("Annual Bonus", min_value=0, value=0, step=50000, format="%d")
        
        st.markdown("#### 🛡️ Additional Reliefs")
        life_assurance = st.number_input("Life Assurance (max ₦100K)", min_value=0, max_value=100000, value=0, step=10000, format="%d")
        mortgage = st.number_input("Mortgage Interest", min_value=0, value=0, step=50000, format="%d")
        
        st.markdown("#### ⚙️ Options")
        include_pension = st.checkbox("Include Pension (8%)", value=True)
        include_nhf = st.checkbox("Include NHF (2.5%)", value=True)
        include_nhis = st.checkbox("Include NHIS (5%)", value=True)
    
    with col2:
        result = calculate_paye(basic, housing, transport, other, bonus, life_assurance, mortgage, include_pension, include_nhf, include_nhis)
        
        st.markdown(f"""
        <div class="result-card" style="margin-bottom: 1.5rem;">
            <div class="result-label">Monthly PAYE</div>
            <div class="result-value">{format_currency(result['monthly_tax'])}</div>
            <div class="result-sub">Effective rate: {result['effective_rate']:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        m1, m2 = st.columns(2)
        m1.metric("Annual Tax", format_currency(result['annual_tax']))
        m2.metric("Monthly Take-Home", format_currency(result['net_monthly']))
        
        st.markdown("---")
        st.markdown("#### 📋 Breakdown")
        
        st.markdown("**Income**")
        inc_df = pd.DataFrame([
            {"Item": "Basic", "Amount": format_currency(result['income']['basic_annual'])},
            {"Item": "Housing", "Amount": format_currency(result['income']['housing_annual'])},
            {"Item": "Transport", "Amount": format_currency(result['income']['transport_annual'])},
            {"Item": "Other", "Amount": format_currency(result['income']['other_annual'])},
            {"Item": "**Gross Total**", "Amount": f"**{format_currency(result['income']['gross_annual'])}**"},
        ])
        st.dataframe(inc_df, hide_index=True, use_container_width=True)
        
        st.markdown("**Deductions**")
        ded_df = pd.DataFrame([{"Item": k, "Amount": format_currency(v)} for k, v in result['deductions'].items()])
        st.dataframe(ded_df, hide_index=True, use_container_width=True)
        
        st.info(f"**Taxable Income:** {format_currency(result['taxable_income'])}")


# ============================================
# CONTRACTOR CALCULATOR
# ============================================

elif page == "🧑‍💻 Contractor Calculator":
    st.markdown("## 🧑‍💻 Contractor Tax Calculator")
    st.markdown("Calculate your tax as an independent contractor with expense deductions.")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 💵 Annual Revenue")
        gross_revenue = st.number_input("Total Revenue", min_value=0, value=6000000, step=500000, format="%d")
        
        st.markdown("#### 📝 Business Expenses")
        expenses = {}
        with st.expander("Add Expenses", expanded=True):
            for i, cat in enumerate(EXPENSE_CATEGORIES[:6]):
                exp = st.number_input(cat, min_value=0, value=0, step=10000, key=f"e_{i}", format="%d")
                if exp > 0: expenses[cat] = exp
        
        st.markdown("#### 🛡️ Reliefs")
        vol_pension = st.number_input("Voluntary Pension", min_value=0, value=0, step=50000, format="%d")
        life_ins = st.number_input("Life Assurance", min_value=0, max_value=100000, value=0, step=10000, key="c_life", format="%d")
        wht = st.number_input("WHT Credits", min_value=0, value=0, step=10000, format="%d")
    
    with col2:
        result = calculate_contractor_tax(gross_revenue, expenses, vol_pension, life_ins, wht)
        
        st.markdown(f"""
        <div class="result-card" style="margin-bottom: 1.5rem;">
            <div class="result-label">Net Tax Payable</div>
            <div class="result-value">{format_currency(result['net_tax_payable'])}</div>
            <div class="result-sub">Effective rate: {result['effective_rate_revenue']:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        m1, m2 = st.columns(2)
        m1.metric("Gross Profit", format_currency(result['gross_profit']))
        m2.metric("Profit Margin", f"{result['profit_margin']:.1f}%")
        
        if result['wht_refund'] > 0:
            st.success(f"💰 WHT Refund Available: {format_currency(result['wht_refund'])}")
        if result['vat_registration_required']:
            st.warning("⚠️ VAT Registration Required (turnover > ₦25M)")
        if result['qualifies_small_company']:
            st.info("✅ Qualifies as Small Company (0% CIT if incorporated)")
        
        st.markdown("---")
        st.markdown("#### 📋 Calculation")
        calc_df = pd.DataFrame([
            {"Step": "Gross Revenue", "Amount": format_currency(gross_revenue)},
            {"Step": "(-) Expenses", "Amount": format_currency(result['expenses']['total'])},
            {"Step": "= Gross Profit", "Amount": format_currency(result['gross_profit'])},
            {"Step": "(-) Reliefs", "Amount": format_currency(result['total_reliefs'])},
            {"Step": "= Taxable Income", "Amount": format_currency(result['taxable_income'])},
            {"Step": "Tax Before WHT", "Amount": format_currency(result['tax_before_credits'])},
            {"Step": "(-) WHT Credits", "Amount": format_currency(wht)},
            {"Step": "**Net Tax**", "Amount": f"**{format_currency(result['net_tax_payable'])}**"},
        ])
        st.dataframe(calc_df, hide_index=True, use_container_width=True)


# ============================================
# COMPARE OPTIONS
# ============================================

elif page == "⚖️ Compare Options":
    st.markdown("## ⚖️ Employee vs Contractor")
    st.markdown("See how your taxes differ between employment structures.")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        amount = st.number_input("Annual Amount (₦)", min_value=1000000, value=6000000, step=500000, format="%d")
        exp_ratio = st.slider("Business Expenses %", 10, 60, 30)
        st.caption("Assumption: 5% WHT, 8% pension as contractor")
    
    with col2:
        result = compare_salary_vs_contractor(amount, exp_ratio / 100)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 💼 Employee")
            st.metric("Annual Tax", format_currency(result['employee']['annual_tax']))
            st.metric("Effective Rate", f"{result['employee']['effective_rate']:.2f}%")
            st.metric("Net Income", format_currency(result['employee']['net_income']))
        
        with c2:
            st.markdown("#### 🧑‍💻 Contractor")
            st.metric("Annual Tax", format_currency(result['contractor']['annual_tax']))
            st.metric("Effective Rate", f"{result['contractor']['effective_rate']:.2f}%")
            st.metric("Net Income", format_currency(result['contractor']['net_income']))
        
        st.markdown("---")
        savings = result['tax_savings_as_contractor']
        if savings > 0:
            st.success(f"### 💡 Contractor saves {format_currency(savings)}/year")
        else:
            st.info(f"### 💡 Employee saves {format_currency(abs(savings))}/year")


# ============================================
# RECORD KEEPER
# ============================================

elif page == "📊 Record Keeper":
    st.markdown("## 📊 Record Keeper")
    st.markdown("Track income and expenses for tax purposes.")
    st.markdown("---")
    
    if 'records' not in st.session_state:
        st.session_state.records = {"income": [], "expenses": []}
    
    tab1, tab2, tab3 = st.tabs(["Add Income", "Add Expense", "View All"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            inc_date = st.date_input("Date", key="id")
            inc_cat = st.selectbox("Category", INCOME_CATEGORIES)
            inc_amt = st.number_input("Amount", min_value=0, value=0, step=1000, key="ia", format="%d")
        with c2:
            inc_client = st.text_input("Client")
            inc_wht = st.number_input("WHT Deducted", min_value=0, value=0, key="iw", format="%d")
        
        if st.button("➕ Add Income", type="primary"):
            if inc_amt > 0:
                st.session_state.records["income"].append({"date": str(inc_date), "category": inc_cat, "amount": inc_amt, "client": inc_client, "wht": inc_wht})
                st.success("Added!")
    
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            exp_date = st.date_input("Date", key="ed")
            exp_cat = st.selectbox("Category", EXPENSE_CATEGORIES)
            exp_amt = st.number_input("Amount", min_value=0, value=0, step=100, key="ea", format="%d")
        with c2:
            exp_vendor = st.text_input("Vendor")
        
        if st.button("➕ Add Expense", type="primary"):
            if exp_amt > 0:
                st.session_state.records["expenses"].append({"date": str(exp_date), "category": exp_cat, "amount": exp_amt, "vendor": exp_vendor})
                st.success("Added!")
    
    with tab3:
        total_inc = sum(r["amount"] for r in st.session_state.records["income"])
        total_exp = sum(r["amount"] for r in st.session_state.records["expenses"])
        total_wht = sum(r.get("wht", 0) for r in st.session_state.records["income"])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Income", format_currency(total_inc))
        m2.metric("Expenses", format_currency(total_exp))
        m3.metric("Net", format_currency(total_inc - total_exp))
        m4.metric("WHT", format_currency(total_wht))
        
        if st.session_state.records["income"]:
            st.markdown("#### Income")
            st.dataframe(pd.DataFrame(st.session_state.records["income"]), hide_index=True, use_container_width=True)
        
        if st.session_state.records["expenses"]:
            st.markdown("#### Expenses")
            st.dataframe(pd.DataFrame(st.session_state.records["expenses"]), hide_index=True, use_container_width=True)


# ============================================
# COMPLIANCE CHECKLIST
# ============================================

elif page == "✅ Compliance Checklist":
    st.markdown("## ✅ Compliance Checklist")
    st.markdown("---")
    
    st.markdown("#### 📋 Registration")
    st.checkbox("TIN registered and verified")
    st.checkbox("Business registered with CAC")
    st.checkbox("VAT registered (if turnover > ₦25M)")
    
    st.markdown("#### 📅 Monthly")
    month = MONTHS[datetime.now().month - 1]
    st.checkbox(f"PAYE remitted for {month}")
    st.checkbox(f"VAT filed for {month}")
    st.checkbox(f"WHT remitted for {month}")
    
    st.markdown("#### 📆 Annual")
    st.checkbox("Annual return filed")
    st.checkbox("WHT certificates collected")
    st.checkbox("Tax clearance obtained")
    
    st.markdown("---")
    st.markdown("#### ⚠️ Penalties")
    st.dataframe(pd.DataFrame([
        {"Violation": "Late filing", "Penalty": "₦50,000 first, ₦25,000/month after"},
        {"Violation": "Unregistered contractor", "Penalty": "₦5,000,000"},
        {"Violation": "No WHT deduction", "Penalty": "200% of amount"},
    ]), hide_index=True, use_container_width=True)


# ============================================
# LEARN
# ============================================

elif page == "📚 Learn":
    st.markdown("## 📚 Learn")
    st.markdown("---")
    
    topic = st.selectbox("Topic:", ["What Changed in 2026?", "PAYE Explained", "Contractor Tips", "Deductions", "WHT Guide", "Penalties"])
    
    if topic == "What Changed in 2026?":
        st.markdown("""
        ### Key Changes
        
        | Before | After |
        |--------|-------|
        | Tax-free: ~₦300K | Tax-free: **₦800K** |
        | CRA (complex) | Rent Relief (simple) |
        | Max rate: 24% | Max rate: 25% |
        
        **For Businesses:**
        - Small (≤₦100M): **0% CIT**
        - Medium (₦100-500M): 20%
        - Large (>₦500M): 30%
        """)
    
    elif topic == "PAYE Explained":
        st.markdown("""
        ### PAYE Formula
        ```
        Gross Income
        - Pension (8%)
        - NHF (2.5%, max ₦2,400/yr)
        - NHIS (5%)
        - Rent Relief (20%, max ₦500K)
        = Taxable Income × Tax Rates
        = Annual Tax ÷ 12 = Monthly PAYE
        ```
        """)
    
    elif topic == "Contractor Tips":
        st.markdown("""
        ### Contractor Advantages
        - Deduct ALL business expenses
        - WHT credits offset your tax
        - Voluntary pension is deductible
        - Lower effective rates possible
        
        **Key:** Document everything!
        """)
    
    elif topic == "Deductions":
        st.markdown("""
        ### Employee Deductions
        | Item | Rate |
        |------|------|
        | Pension | 8% |
        | NHF | 2.5% (max ₦2,400/yr) |
        | NHIS | 5% |
        | Rent Relief | 20% (max ₦500K) |
        | Life Assurance | max ₦100K |
        """)
    
    elif topic == "WHT Guide":
        st.markdown("""
        ### WHT Rates
        | Type | Rate |
        |------|------|
        | Professional services | 10% |
        | Contracts | 5% |
        | Rent | 10% |
        
        **Important:** WHT is a credit, not final tax!
        """)
    
    elif topic == "Penalties":
        st.markdown("""
        ### Penalty Schedule
        | Violation | Penalty |
        |-----------|---------|
        | Late filing | ₦50,000 + ₦25,000/month |
        | Unregistered contractor | **₦5,000,000** |
        | No WHT deduction | 200% of amount |
        """)
