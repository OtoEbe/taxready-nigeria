"""
TaxReady Nigeria - Tax Compliance Made Simple
MVP for Nigeria Tax Act 2025 (Effective January 1, 2026)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import sys
from pathlib import Path

# Fix import path for Streamlit Cloud
app_dir = Path(__file__).parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from calculators.paye import calculate_paye
from calculators.contractor import calculate_contractor_tax, compare_salary_vs_contractor
from utils.constants import (
    TAX_BANDS_2026, EXPENSE_CATEGORIES, INCOME_CATEGORIES,
    FILING_DEADLINES, PENALTIES, VAT_REGISTRATION_THRESHOLD,
    SMALL_COMPANY_TURNOVER_LIMIT, MONTHS
)

# Page config
st.set_page_config(
    page_title="TaxReady Nigeria",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1B4D3E;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-top: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #1B4D3E 0%, #2E7D5B 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
    }
    .warning-box {
        background-color: #FFF3CD;
        border-left: 4px solid #FFC107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    .success-box {
        background-color: #D4EDDA;
        border-left: 4px solid #28A745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    .info-box {
        background-color: #D1ECF1;
        border-left: 4px solid #17A2B8;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1B4D3E;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def format_currency(amount: float) -> str:
    """Format number as Nigerian Naira"""
    return f"₦{amount:,.2f}"


def format_currency_short(amount: float) -> str:
    """Format large numbers in millions/thousands"""
    if amount >= 1_000_000:
        return f"₦{amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"₦{amount/1_000:.1f}K"
    return f"₦{amount:,.0f}"


# Initialize session state
if 'records' not in st.session_state:
    st.session_state.records = {"income": [], "expenses": []}
if 'user_type' not in st.session_state:
    st.session_state.user_type = None


# Sidebar Navigation
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
st.sidebar.info("""
**PAYE Remittance:** 10th monthly  
**VAT Filing:** 21st monthly  
**Annual Return:** Within 6 months of year end
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ New Law Alert")
st.sidebar.warning("""
**Nigeria Tax Act 2025** takes effect **January 1, 2026**.

Key changes:
- First ₦800K tax-free
- CRA abolished → Rent Relief
- ₦5M penalty for unregistered contractors
""")


# ============================================
# HOME PAGE
# ============================================
if page == "🏠 Home":
    st.markdown('<p class="main-header">🇳🇬 TaxReady Nigeria</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Navigate Nigeria\'s 2026 Tax Laws with Confidence</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Alert banner
    days_until = (date(2026, 1, 1) - date.today()).days
    if days_until > 0:
        st.warning(f"⏰ **{days_until} days** until the Nigeria Tax Act 2025 takes effect. Are you ready?")
    else:
        st.success("✅ The Nigeria Tax Act 2025 is now in effect!")
    
    st.markdown("### What's New in 2026?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <h4>💰 ₦800K Tax-Free</h4>
        <p>First ₦800,000 of annual income is completely exempt from tax.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
        <h4>🏠 New Rent Relief</h4>
        <p>20% of gross income (max ₦500K) replaces the old CRA system.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-box">
        <h4>⚠️ Stricter Penalties</h4>
        <p>₦5M fine for engaging unregistered contractors. TIN now mandatory.</p>
        </div>
        """, unsafe_allow_html=True)
    
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
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("💼 Calculate PAYE", use_container_width=True):
            st.session_state.page = "💼 Employee Calculator"
            st.rerun()
    with col2:
        if st.button("🧑‍💻 Contractor Tax", use_container_width=True):
            st.session_state.page = "🧑‍💻 Contractor Calculator"
            st.rerun()
    with col3:
        if st.button("⚖️ Compare Options", use_container_width=True):
            st.session_state.page = "⚖️ Compare Options"
            st.rerun()
    with col4:
        if st.button("✅ Check Compliance", use_container_width=True):
            st.session_state.page = "✅ Compliance Checklist"
            st.rerun()


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
        
        basic = st.number_input("Basic Salary (₦/month)", min_value=0, value=150000, step=10000,
                               help="Your monthly basic salary")
        housing = st.number_input("Housing Allowance (₦/month)", min_value=0, value=75000, step=5000)
        transport = st.number_input("Transport Allowance (₦/month)", min_value=0, value=45000, step=5000)
        other = st.number_input("Other Allowances (₦/month)", min_value=0, value=30000, step=5000)
        bonus = st.number_input("Annual Bonus (₦/year)", min_value=0, value=0, step=50000)
        
        st.markdown("### 🛡️ Additional Reliefs")
        life_assurance = st.number_input("Life Assurance Premium (₦/year)", min_value=0, max_value=100000, 
                                         value=0, step=10000, help="Maximum ₦100,000")
        mortgage = st.number_input("Mortgage Interest (₦/year)", min_value=0, value=0, step=50000,
                                   help="Interest on primary residence mortgage")
        
        st.markdown("### ⚙️ Deduction Options")
        include_pension = st.checkbox("Pension Contribution (8%)", value=True)
        include_nhf = st.checkbox("National Housing Fund (2.5%)", value=True)
        include_nhis = st.checkbox("NHIS (5%)", value=True)
    
    with col2:
        # Calculate
        result = calculate_paye(
            basic_monthly=basic,
            housing_monthly=housing,
            transport_monthly=transport,
            other_allowances_monthly=other,
            bonus_annual=bonus,
            life_assurance=life_assurance,
            mortgage_interest=mortgage,
            include_pension=include_pension,
            include_nhf=include_nhf,
            include_nhis=include_nhis
        )
        
        st.markdown("### 📊 Tax Summary")
        
        # Key metrics
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("Monthly PAYE", format_currency(result["monthly_tax"]))
            st.metric("Annual Tax", format_currency(result["annual_tax"]))
        with metric_col2:
            st.metric("Effective Rate", f"{result['effective_rate']:.2f}%")
            st.metric("Monthly Take-Home", format_currency(result["net_monthly"]))
        
        st.markdown("---")
        
        # Income breakdown
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
        
        # Deductions
        st.markdown("#### ➖ Deductions")
        deductions_data = [{"Deduction": k, "Amount": format_currency(v)} for k, v in result["deductions"].items()]
        deductions_data.append({"Deduction": "**TOTAL DEDUCTIONS**", "Amount": f"**{format_currency(result['total_deductions'])}**"})
        st.dataframe(pd.DataFrame(deductions_data), hide_index=True, use_container_width=True)
        
        st.info(f"**Taxable Income:** {format_currency(result['taxable_income'])}")
        
        # Tax calculation
        st.markdown("#### 🧮 Tax Calculation by Band")
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
        st.caption("Enter your annual business expenses by category")
        
        expenses = {}
        with st.expander("Click to enter expenses", expanded=True):
            for i, category in enumerate(EXPENSE_CATEGORIES[:8]):  # Show first 8 categories
                exp = st.number_input(f"{category}", min_value=0, value=0, step=10000, key=f"exp_{i}")
                if exp > 0:
                    expenses[category] = exp
            
            other_exp = st.number_input("Other Business Expenses", min_value=0, value=0, step=10000)
            if other_exp > 0:
                expenses["Other Business Expenses"] = other_exp
        
        st.markdown("### 🛡️ Personal Reliefs")
        vol_pension = st.number_input("Voluntary Pension (₦/year)", min_value=0, 
                                       max_value=int(gross_revenue * 0.08), value=0, step=50000,
                                       help=f"Maximum: {format_currency(gross_revenue * 0.08)} (8% of revenue)")
        life_assurance = st.number_input("Life Assurance (₦/year)", min_value=0, max_value=100000, 
                                          value=0, step=10000)
        
        st.markdown("### 💳 WHT Credits")
        wht_credits = st.number_input("WHT Already Deducted (₦)", min_value=0, value=0, step=10000,
                                       help="Total WHT deducted by clients (from your WHT certificates)")
    
    with col2:
        # Calculate
        result = calculate_contractor_tax(
            gross_revenue=gross_revenue,
            business_expenses=expenses,
            voluntary_pension=vol_pension,
            life_assurance=life_assurance,
            wht_credits=wht_credits
        )
        
        st.markdown("### 📊 Tax Summary")
        
        # Key metrics
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("Net Tax Payable", format_currency(result["net_tax_payable"]))
            st.metric("Effective Rate (Revenue)", f"{result['effective_rate_revenue']:.2f}%")
        with metric_col2:
            st.metric("Gross Profit", format_currency(result["gross_profit"]))
            st.metric("Profit Margin", f"{result['profit_margin']:.1f}%")
        
        # Alerts
        if result["wht_refund"] > 0:
            st.success(f"💰 **WHT Refund Available:** {format_currency(result['wht_refund'])}")
        
        if result["vat_registration_required"]:
            st.warning("⚠️ **VAT Registration Required** - Your turnover exceeds ₦25M")
        
        if result["qualifies_small_company"]:
            st.info("✅ You qualify as a **Small Company** (0% CIT if incorporated)")
        
        st.markdown("---")
        
        # Calculation breakdown
        st.markdown("#### 📋 Calculation Breakdown")
        
        summary_data = [
            {"Item": "Gross Revenue", "Amount": format_currency(gross_revenue)},
            {"Item": "(-) Business Expenses", "Amount": format_currency(result["expenses"]["total"])},
            {"Item": "= Gross Profit", "Amount": format_currency(result["gross_profit"])},
            {"Item": "(-) Personal Reliefs", "Amount": format_currency(result["total_reliefs"])},
            {"Item": "= Taxable Income", "Amount": format_currency(result["taxable_income"])},
            {"Item": "Tax Before Credits", "Amount": format_currency(result["tax_before_credits"])},
            {"Item": "(-) WHT Credits", "Amount": format_currency(wht_credits)},
            {"Item": "**= Net Tax Payable**", "Amount": f"**{format_currency(result['net_tax_payable'])}**"},
        ]
        st.dataframe(pd.DataFrame(summary_data), hide_index=True, use_container_width=True)
        
        # Tax by band
        st.markdown("#### 🧮 Tax Calculation by Band")
        tax_df = pd.DataFrame(result["tax_breakdown"])
        tax_df["taxable_amount"] = tax_df["taxable_amount"].apply(format_currency)
        tax_df["tax"] = tax_df["tax"].apply(format_currency)
        tax_df.columns = ["Tax Band", "Rate", "Taxable Amount", "Tax Due"]
        st.dataframe(tax_df, hide_index=True, use_container_width=True)


# ============================================
# COMPARE OPTIONS
# ============================================
elif page == "⚖️ Compare Options":
    st.markdown("## ⚖️ Employee vs Contractor Comparison")
    st.markdown("See how your tax differs when receiving income as salary vs. contractor fees.")
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 💵 Enter Annual Amount")
        gross_amount = st.number_input("Total Annual Amount (₦)", min_value=1000000, 
                                        value=6000000, step=500000)
        
        expense_ratio = st.slider("Estimated Business Expenses (%)", min_value=10, max_value=60, 
                                   value=30, help="As a contractor, what % of revenue goes to expenses?")
        
        st.info("""
        **Assumptions:**
        - Employee: Standard 50/25/15/10 salary structure
        - Contractor: 5% WHT deducted, 8% voluntary pension
        """)
    
    with col2:
        result = compare_salary_vs_contractor(gross_amount, expense_ratio / 100)
        
        st.markdown("### 📊 Comparison Results")
        
        comp_col1, comp_col2 = st.columns(2)
        
        with comp_col1:
            st.markdown("#### 💼 As Employee")
            st.metric("Annual Tax", format_currency(result["employee"]["annual_tax"]))
            st.metric("Effective Rate", f"{result['employee']['effective_rate']:.2f}%")
            st.metric("Net Income", format_currency(result["employee"]["net_income"]))
        
        with comp_col2:
            st.markdown("#### 🧑‍💻 As Contractor")
            st.metric("Annual Tax", format_currency(result["contractor"]["annual_tax"]))
            st.metric("Effective Rate", f"{result['contractor']['effective_rate']:.2f}%")
            st.metric("Net Income", format_currency(result["contractor"]["net_income"]))
        
        st.markdown("---")
        
        # Recommendation
        savings = result["tax_savings_as_contractor"]
        if savings > 0:
            st.success(f"""
            ### 💡 Recommendation: **{result['recommendation']}**
            
            As a contractor, you could save **{format_currency(savings)}** annually in taxes 
            ({format_currency(savings/12)}/month).
            
            This assumes you can legitimately claim {expense_ratio}% in business expenses.
            """)
        else:
            st.info(f"""
            ### 💡 Recommendation: **{result['recommendation']}**
            
            As an employee, you would pay **{format_currency(abs(savings))}** less in taxes annually.
            
            This is because your expense ratio ({expense_ratio}%) may not offset the deductions available to employees.
            """)
        
        st.markdown("---")
        st.markdown("#### ⚠️ Important Considerations")
        st.markdown("""
        **Beyond tax, consider:**
        - **Job security:** Employees have more protections
        - **Benefits:** Pension, health insurance, leave
        - **Compliance burden:** Contractors must file their own returns
        - **Multiple income streams:** Contractors can work for multiple clients
        - **Business expenses:** Must be legitimate and documented
        """)


# ============================================
# RECORD KEEPER
# ============================================
elif page == "📊 Record Keeper":
    st.markdown("## 📊 Record Keeper")
    st.markdown("Track your income and expenses for tax purposes. Keep records for **6 years**.")
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["💵 Add Income", "💸 Add Expense", "📋 View Records"])
    
    with tab1:
        st.markdown("### Add Income Record")
        
        col1, col2 = st.columns(2)
        with col1:
            income_date = st.date_input("Date", value=date.today(), key="income_date")
            income_category = st.selectbox("Category", INCOME_CATEGORIES)
            income_amount = st.number_input("Amount (₦)", min_value=0, value=0, step=1000, key="income_amt")
        
        with col2:
            income_client = st.text_input("Client/Source", placeholder="e.g., ABC Company Ltd")
            income_invoice = st.text_input("Invoice/Reference No.", placeholder="e.g., INV-2026-001")
            income_wht = st.number_input("WHT Deducted (₦)", min_value=0, value=0, step=100)
        
        income_notes = st.text_area("Notes", placeholder="Description of work performed...", key="income_notes")
        
        if st.button("➕ Add Income Record", type="primary"):
            if income_amount > 0:
                record = {
                    "date": str(income_date),
                    "category": income_category,
                    "amount": income_amount,
                    "client": income_client,
                    "invoice": income_invoice,
                    "wht": income_wht,
                    "notes": income_notes,
                    "timestamp": datetime.now().isoformat()
                }
                st.session_state.records["income"].append(record)
                st.success("✅ Income record added!")
            else:
                st.error("Please enter an amount greater than 0")
    
    with tab2:
        st.markdown("### Add Expense Record")
        
        col1, col2 = st.columns(2)
        with col1:
            expense_date = st.date_input("Date", value=date.today(), key="expense_date")
            expense_category = st.selectbox("Category", EXPENSE_CATEGORIES)
            expense_amount = st.number_input("Amount (₦)", min_value=0, value=0, step=100, key="expense_amt")
        
        with col2:
            expense_vendor = st.text_input("Vendor/Payee", placeholder="e.g., MTN Nigeria")
            expense_receipt = st.text_input("Receipt No.", placeholder="e.g., RCP-12345")
        
        expense_notes = st.text_area("Notes", placeholder="Purpose of expense...", key="expense_notes")
        
        if st.button("➕ Add Expense Record", type="primary"):
            if expense_amount > 0:
                record = {
                    "date": str(expense_date),
                    "category": expense_category,
                    "amount": expense_amount,
                    "vendor": expense_vendor,
                    "receipt": expense_receipt,
                    "notes": expense_notes,
                    "timestamp": datetime.now().isoformat()
                }
                st.session_state.records["expenses"].append(record)
                st.success("✅ Expense record added!")
            else:
                st.error("Please enter an amount greater than 0")
    
    with tab3:
        st.markdown("### Your Records")
        
        # Summary metrics
        total_income = sum(r["amount"] for r in st.session_state.records["income"])
        total_expenses = sum(r["amount"] for r in st.session_state.records["expenses"])
        total_wht = sum(r.get("wht", 0) for r in st.session_state.records["income"])
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            st.metric("Total Income", format_currency(total_income))
        with metric_col2:
            st.metric("Total Expenses", format_currency(total_expenses))
        with metric_col3:
            st.metric("Net Profit", format_currency(total_income - total_expenses))
        with metric_col4:
            st.metric("WHT Credits", format_currency(total_wht))
        
        st.markdown("---")
        
        # Income records
        st.markdown("#### 💵 Income Records")
        if st.session_state.records["income"]:
            income_df = pd.DataFrame(st.session_state.records["income"])
            income_df["amount"] = income_df["amount"].apply(format_currency)
            income_df["wht"] = income_df["wht"].apply(format_currency)
            st.dataframe(income_df[["date", "category", "client", "amount", "wht", "invoice"]], 
                        hide_index=True, use_container_width=True)
        else:
            st.info("No income records yet. Add your first record above!")
        
        # Expense records
        st.markdown("#### 💸 Expense Records")
        if st.session_state.records["expenses"]:
            expense_df = pd.DataFrame(st.session_state.records["expenses"])
            expense_df["amount"] = expense_df["amount"].apply(format_currency)
            st.dataframe(expense_df[["date", "category", "vendor", "amount", "receipt"]], 
                        hide_index=True, use_container_width=True)
        else:
            st.info("No expense records yet. Add your first record above!")
        
        # Export
        st.markdown("---")
        if st.button("📥 Export Records (JSON)"):
            export_data = json.dumps(st.session_state.records, indent=2)
            st.download_button(
                label="Download JSON",
                data=export_data,
                file_name=f"taxready_records_{date.today()}.json",
                mime="application/json"
            )


# ============================================
# COMPLIANCE CHECKLIST
# ============================================
elif page == "✅ Compliance Checklist":
    st.markdown("## ✅ Tax Compliance Checklist")
    st.markdown("Stay on top of your tax obligations with this interactive checklist.")
    
    st.markdown("---")
    
    # Registration
    st.markdown("### 📋 Registration & Documentation")
    
    reg_items = [
        ("TIN registered and verified", "Verify at tinverification.jtb.gov.ng"),
        ("Business registered with CAC (if applicable)", "Required for companies"),
        ("VAT registered (if turnover > ₦25M)", "Mandatory for eligible businesses"),
        ("Separate business bank account", "Recommended for clean records"),
        ("Pension RSA set up", "Required for employees, optional for contractors"),
    ]
    
    for item, help_text in reg_items:
        st.checkbox(item, help=help_text, key=f"reg_{item}")
    
    st.markdown("---")
    
    # Monthly obligations
    st.markdown("### 📅 Monthly Obligations")
    
    current_month = MONTHS[datetime.now().month - 1]
    st.info(f"**Current Month:** {current_month} {datetime.now().year}")
    
    monthly_items = [
        (f"PAYE remitted for {current_month}", "Due: 10th of following month"),
        (f"VAT filed for {current_month}", "Due: 21st of following month"),
        (f"WHT remitted for {current_month}", "Due: 21st of following month"),
        (f"Income recorded for {current_month}", "Keep records updated"),
        (f"Expenses documented for {current_month}", "Keep receipts for 6 years"),
    ]
    
    for item, help_text in monthly_items:
        st.checkbox(item, help=help_text, key=f"monthly_{item}")
    
    st.markdown("---")
    
    # Annual obligations
    st.markdown("### 📆 Annual Obligations (2026)")
    
    annual_items = [
        ("Annual tax return filed", "Due within 6 months of year end"),
        ("Form H1 submitted (employers)", "Due: January 31"),
        ("All WHT certificates collected", "Valid for 24 months"),
        ("Financial statements prepared", "Required for companies"),
        ("Tax clearance certificate obtained", "For contracts and banking"),
    ]
    
    for item, help_text in annual_items:
        st.checkbox(item, help=help_text, key=f"annual_{item}")
    
    st.markdown("---")
    
    # Penalties reminder
    st.markdown("### ⚠️ Penalty Reminder")
    
    penalty_df = pd.DataFrame([
        {"Violation": "Late filing (first offense)", "Penalty": "₦50,000"},
        {"Violation": "Late filing (subsequent)", "Penalty": "₦25,000/month"},
        {"Violation": "Engaging unregistered contractor", "Penalty": "₦5,000,000"},
        {"Violation": "Failure to register TIN", "Penalty": "Up to ₦50,000"},
        {"Violation": "Failure to deduct WHT", "Penalty": "200% of amount"},
    ])
    st.dataframe(penalty_df, hide_index=True, use_container_width=True)


# ============================================
# LEARN
# ============================================
elif page == "📚 Learn":
    st.markdown("## 📚 Tax Knowledge Hub")
    st.markdown("Everything you need to know about Nigeria's 2026 tax laws.")
    
    st.markdown("---")
    
    topic = st.selectbox("Choose a topic:", [
        "Overview: What Changed in 2026?",
        "For Employees: Understanding PAYE",
        "For Contractors: Tax Optimization",
        "Allowable Deductions Explained",
        "WHT: What You Need to Know",
        "VAT Basics",
        "Penalties to Avoid",
        "Frequently Asked Questions"
    ])
    
    if topic == "Overview: What Changed in 2026?":
        st.markdown("""
        ### The Nigeria Tax Act 2025: Key Changes
        
        The Nigeria Tax Act 2025, signed on June 26, 2025, is the most comprehensive tax reform in decades.
        It takes effect **January 1, 2026**.
        
        #### What Was Consolidated
        The new Act replaces 12+ separate laws:
        - Personal Income Tax Act (PITA)
        - Companies Income Tax Act (CITA)
        - Value Added Tax Act
        - Capital Gains Tax Act
        - Petroleum Profits Tax Act
        - Stamp Duties Act
        
        #### Key Changes for Individuals
        
        | Before (2025) | After (2026) |
        |---------------|--------------|
        | Tax-free threshold: ~₦300K | Tax-free threshold: **₦800K** |
        | Consolidated Relief Allowance (complex) | Rent Relief (simple: 20%, max ₦500K) |
        | Top rate at ₦3.2M threshold | Top rate at ₦50M threshold |
        | Maximum rate: 24% | Maximum rate: 25% |
        
        #### Key Changes for Businesses
        
        - **Small companies** (turnover ≤₦100M, assets ≤₦250M): **0% CIT**
        - **Medium companies** (₦100M-₦500M): 20% CIT
        - **Large companies** (>₦500M): 30% CIT
        - **E-invoicing** mandatory for VAT-registered businesses
        - **WHT credits** valid for 24 months (can offset tax)
        
        #### Stricter Enforcement
        
        - **₦5M penalty** for engaging unregistered contractors
        - TIN now **mandatory** for bank accounts
        - NRS has AI tools to cross-reference bank data with tax filings
        """)
    
    elif topic == "For Employees: Understanding PAYE":
        st.markdown("""
        ### PAYE (Pay As You Earn) Explained
        
        PAYE is how income tax is collected from employees. Your employer deducts it from your salary
        and remits it to the tax authority.
        
        #### How It's Calculated
        
        ```
        Gross Income
        - Pension (8%)
        - NHF (2.5% of basic)
        - NHIS (5% of basic)
        - Rent Relief (20% of gross, max ₦500K)
        - Life Assurance (max ₦100K)
        = Taxable Income
        × Tax Rates (0% to 25%)
        = Annual Tax
        ÷ 12
        = Monthly PAYE
        ```
        
        #### What's Taxable
        - Basic salary
        - Housing allowance
        - Transport allowance
        - Bonuses
        - Benefits-in-kind (company car, housing)
        
        #### What's NOT Taxable
        - Reimbursement of actual expenses
        - Meal subsidies/vouchers
        - Uniforms and work tools
        - Medical expenses paid by employer
        - Retirement benefits under PRA
        
        #### Tips to Reduce Your Tax
        1. Ensure your employer applies Rent Relief
        2. Take out a life assurance policy (up to ₦100K deductible)
        3. Maximize pension contributions
        4. If you have a mortgage, claim interest deduction
        """)
    
    elif topic == "For Contractors: Tax Optimization":
        st.markdown("""
        ### Tax Strategies for Independent Contractors
        
        As a contractor, you have more control over your tax liability than employees.
        
        #### The Big Advantage: Business Expenses
        
        Unlike employees, you can deduct ALL legitimate business expenses:
        
        | Category | Examples |
        |----------|----------|
        | Premises | Office rent, utilities, maintenance |
        | Equipment | Computers, furniture, software |
        | Communications | Internet, phone, data |
        | Professional | Accounting, legal, subscriptions |
        | Marketing | Ads, website, business cards |
        | Travel | Fuel, flights, hotels (business only) |
        | Personnel | Subcontractors, assistants |
        
        #### The Formula for Lower Taxes
        
        ```
        Revenue
        - Business Expenses (document everything!)
        = Gross Profit
        - Rent Relief (20%, max ₦500K)
        - Voluntary Pension (up to 8%)
        - Life Assurance (max ₦100K)
        = Taxable Income
        - WHT Credits (from clients)
        = Net Tax Payable
        ```
        
        #### Top Optimization Strategies
        
        1. **Document EVERYTHING** — No receipt = no deduction
        2. **Maximize legitimate expenses** — Home office, vehicle, training
        3. **Contribute to pension** — Tax-deductible AND builds retirement
        4. **Collect ALL WHT certificates** — They offset your tax for 24 months
        5. **Time your income** — If near threshold, consider timing of invoices
        
        #### Warning Signs for Audits
        - Expense ratio much higher than industry average
        - Large cash transactions
        - Mismatch between bank deposits and declared income
        """)
    
    elif topic == "Allowable Deductions Explained":
        st.markdown("""
        ### Complete Guide to Allowable Deductions
        
        #### For Employees (Automatic)
        
        | Deduction | Rate | Cap |
        |-----------|------|-----|
        | Pension | 8% of (Basic + Housing + Transport) | None |
        | NHF | 2.5% of Basic | ₦2,400/year |
        | NHIS | 5% of Basic | None |
        | Rent Relief | 20% of Gross | ₦500,000 |
        | Life Assurance | Actual | ₦100,000 |
        | Mortgage Interest | Actual | None |
        
        #### For Contractors (Must Document)
        
        **Office & Premises**
        - Rent (proportional if home office)
        - Utilities (proportional)
        - Internet
        - Maintenance
        
        **Equipment & Tools**
        - Computers, phones
        - Software subscriptions
        - Furniture
        - Capital allowances (25%/year for equipment)
        
        **Professional Services**
        - Accounting fees
        - Legal fees
        - Professional subscriptions
        - Training and development
        
        **Travel & Transport**
        - Business travel (with log book)
        - Fuel (business portion)
        - Vehicle maintenance (business portion)
        - Flights and accommodation
        
        #### What's NOT Deductible
        - Personal expenses
        - Entertainment (except direct client meetings)
        - Fines and penalties
        - Political contributions
        - Expenses without documentation
        """)
    
    elif topic == "WHT: What You Need to Know":
        st.markdown("""
        ### Withholding Tax (WHT) Explained
        
        WHT is tax deducted at source when payments are made.
        
        #### Who Deducts WHT?
        Companies paying for services must deduct WHT and remit to NRS.
        
        #### WHT Rates
        
        | Payment Type | Rate |
        |--------------|------|
        | Professional services | 10% |
        | Consultancy | 10% |
        | Technical services | 10% |
        | Contracts | 5% |
        | Supplies | 5% |
        | Rent | 10% |
        | Dividends | 10% |
        | Interest | 10% |
        
        #### For Contractors: WHT is a CREDIT, Not Final Tax
        
        This is crucial: WHT is NOT your final tax liability. It's an advance payment.
        
        **Example:**
        - You earn ₦1,000,000 from a client
        - Client deducts 10% WHT = ₦100,000
        - You receive ₦900,000
        - At year end, your actual tax is ₦80,000
        - You get ₦20,000 REFUND (or credit against next year)
        
        #### Important Rules
        - WHT certificates are valid for **24 months**
        - Always collect certificates from clients
        - Keep organized records by date and client
        - Report all WHT credits on your annual return
        """)
    
    elif topic == "VAT Basics":
        st.markdown("""
        ### VAT: What You Need to Know
        
        #### The Basics
        - Rate: **7.5%**
        - Registration threshold: **₦25M annual turnover**
        - Filing: Monthly, by 21st of following month
        
        #### Do You Need to Register?
        
        **Yes, if:**
        - Annual turnover exceeds ₦25 million
        - You supply taxable goods or services
        
        **No, if:**
        - Turnover below ₦25 million
        - You only supply exempt items
        
        #### VAT-Exempt Items
        - Basic food items
        - Medical supplies
        - Educational materials
        - Books and newspapers
        - Baby products
        - Fertilizers
        
        #### Input VAT Recovery (New in 2026)
        
        You can now recover VAT paid on:
        - Goods purchased for business
        - Services used in business
        - **Fixed assets** (NEW — previously not allowed)
        
        #### E-Invoicing Requirement
        
        From 2026, VAT-registered businesses must use NRS-approved
        e-invoicing systems. Start preparing now!
        """)
    
    elif topic == "Penalties to Avoid":
        st.markdown("""
        ### Tax Penalties: What to Avoid
        
        #### Registration Penalties
        
        | Violation | Penalty |
        |-----------|---------|
        | Failure to register TIN | Up to ₦50,000 |
        | Failure to notify address change | ₦25,000 |
        | Operating without TIN | Restrictions on banking |
        
        #### Filing Penalties
        
        | Violation | Penalty |
        |-----------|---------|
        | Late filing (first month) | ₦50,000 |
        | Late filing (subsequent) | ₦25,000/month |
        | False returns | ₦500,000 + up to 5 years imprisonment |
        
        #### Payment Penalties
        
        | Violation | Penalty |
        |-----------|---------|
        | Late payment | 10% p.a. + interest at CBN MPR |
        | Under-remittance of PAYE | 10% of amount + interest |
        | Failure to deduct WHT | **200% of amount** |
        
        #### Contractor-Related Penalties
        
        | Violation | Penalty |
        |-----------|---------|
        | **Engaging unregistered contractor** | **₦5,000,000** |
        | Not obtaining TIN before payment | ₦5,000,000 |
        
        #### How to Stay Safe
        
        1. Register and verify TIN immediately
        2. File on time (even if you can't pay full amount)
        3. Always verify contractor TINs before payment
        4. Keep records for 6 years
        5. When in doubt, consult a tax professional
        """)
    
    elif topic == "Frequently Asked Questions":
        st.markdown("""
        ### Frequently Asked Questions
        
        **Q: Has the VAT rate changed?**
        A: No, VAT remains at 7.5%.
        
        **Q: Do I need to re-register my business?**
        A: No. Keep your existing CAC registration and TIN.
        
        **Q: When do the new rules start?**
        A: January 1, 2026.
        
        **Q: What happened to Consolidated Relief Allowance?**
        A: CRA is abolished. It's replaced by Rent Relief (20% of gross, max ₦500K).
        
        **Q: I earn below ₦800K/year. Do I pay tax?**
        A: No. The first ₦800,000 is completely tax-free.
        
        **Q: I'm a contractor. Can I still deduct expenses?**
        A: Yes! All legitimate business expenses remain deductible.
        
        **Q: What if I haven't been paying tax?**
        A: Register immediately. Consider voluntary disclosure
        to reduce penalties. Consult a tax professional.
        
        **Q: How long must I keep records?**
        A: 6 years minimum.
        
        **Q: Can I offset WHT against my tax?**
        A: Yes! WHT credits are valid for 24 months.
        
        **Q: Do I need an accountant?**
        A: Recommended if turnover exceeds ₦30M or you have
        complex affairs. Otherwise, tools like TaxReady can help.
        """)


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8rem;'>
    <p>TaxReady Nigeria | Built for the Nigeria Tax Act 2025</p>
    <p>⚠️ This tool provides estimates only. Consult a qualified tax professional for advice.</p>
    <p>© 2025 | Made with ❤️ for Nigerian businesses</p>
</div>
""", unsafe_allow_html=True)
