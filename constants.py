"""
Nigeria Tax Act 2025 - Constants and Tax Rates
Effective: January 1, 2026
"""

# 2026 Personal Income Tax Bands
TAX_BANDS_2026 = [
    {"min": 0, "max": 800_000, "rate": 0.00, "label": "First ₦800,000"},
    {"min": 800_000, "max": 3_000_000, "rate": 0.15, "label": "₦800,001 - ₦3,000,000"},
    {"min": 3_000_000, "max": 12_000_000, "rate": 0.18, "label": "₦3,000,001 - ₦12,000,000"},
    {"min": 12_000_000, "max": 25_000_000, "rate": 0.21, "label": "₦12,000,001 - ₦25,000,000"},
    {"min": 25_000_000, "max": 50_000_000, "rate": 0.23, "label": "₦25,000,001 - ₦50,000,000"},
    {"min": 50_000_000, "max": float('inf'), "rate": 0.25, "label": "Above ₦50,000,000"},
]

# Corporate Income Tax Rates
CIT_RATES = {
    "small": {"threshold": 25_000_000, "rate": 0.00, "label": "Small Company (0%)"},
    "medium": {"threshold": 100_000_000, "rate": 0.20, "label": "Medium Company (20%)"},
    "large": {"threshold": float('inf'), "rate": 0.30, "label": "Large Company (30%)"},
}

# Small Company Definition (CIT Exempt)
SMALL_COMPANY_TURNOVER_LIMIT = 100_000_000  # ₦100M
SMALL_COMPANY_ASSETS_LIMIT = 250_000_000    # ₦250M

# Statutory Deduction Rates
PENSION_RATE = 0.08          # 8% of pensionable earnings
NHF_RATE = 0.025             # 2.5% of basic salary
NHF_ANNUAL_CAP = 2_400       # ₦2,400/year (₦200/month)
NHIS_RATE = 0.05             # 5% of basic salary

# Relief Caps
RENT_RELIEF_RATE = 0.20      # 20% of gross income
RENT_RELIEF_CAP = 500_000    # Maximum ₦500,000
LIFE_ASSURANCE_CAP = 100_000 # Maximum ₦100,000

# WHT Rates
WHT_RATES = {
    "professional_services": 0.10,
    "consultancy": 0.10,
    "technical_services": 0.10,
    "contracts": 0.05,
    "supplies": 0.05,
    "rent": 0.10,
    "dividends": 0.10,
    "interest": 0.10,
    "royalties": 0.10,
}

# VAT
VAT_RATE = 0.075  # 7.5%
VAT_REGISTRATION_THRESHOLD = 25_000_000  # ₦25M annual turnover

# Penalties
PENALTIES = {
    "late_filing_first": 50_000,
    "late_filing_subsequent": 25_000,  # Per month
    "unregistered_contractor": 5_000_000,
    "failure_to_register_tin": 50_000,
    "failure_to_deduct_wht": 2.0,  # 200% of amount
}

# Filing Deadlines
FILING_DEADLINES = {
    "paye_monthly": "10th of following month",
    "vat_monthly": "21st of following month",
    "annual_return": "Within 6 months of year end",
    "wht_remittance": "21st of following month",
}

# Expense Categories for Contractors
EXPENSE_CATEGORIES = [
    "Office Rent/Workspace",
    "Utilities (Power, Water)",
    "Internet & Communications",
    "Equipment & Software",
    "Professional Subscriptions",
    "Accounting/Legal Fees",
    "Marketing & Advertising",
    "Travel & Transportation",
    "Subcontractor Payments",
    "Insurance",
    "Bank Charges",
    "Office Supplies",
    "Training & Development",
    "Other Business Expenses",
]

# Income Categories
INCOME_CATEGORIES = [
    "Consulting/Professional Fees",
    "Contract Payments",
    "Retainer Income",
    "Project-Based Income",
    "Royalties/Licensing",
    "Training/Speaking Fees",
    "Other Business Income",
]

# Months
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
