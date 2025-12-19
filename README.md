# 🇳🇬 TaxReady Nigeria

**Tax Compliance Made Simple** — Navigate Nigeria's 2026 Tax Laws with Confidence

A comprehensive tax management platform built for the Nigeria Tax Act 2025 (effective January 1, 2026).

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🎯 Features

### Calculators
- **PAYE Calculator** — Calculate employee tax with all 2026 deductions
- **Contractor Calculator** — Tax optimization for self-employed professionals  
- **Comparison Tool** — See tax implications of salary vs contractor income

### Record Keeping
- Track income and expenses
- Organize WHT certificates
- Export records for tax filing

### Compliance Tools
- Interactive compliance checklist
- Filing deadline reminders
- Penalty reference guide

### Learning Hub
- Complete guide to 2026 tax changes
- Topic-specific explainers
- FAQ and best practices

---

## 🚀 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/taxready-nigeria.git
cd taxready-nigeria

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repo and `app.py`
5. Click "Deploy"

Your app will be live at `https://your-app-name.streamlit.app`

---

## 📁 Project Structure

```
taxready/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── calculators/
│   ├── __init__.py
│   ├── paye.py              # Employee PAYE calculator
│   └── contractor.py        # Contractor tax calculator
├── utils/
│   ├── __init__.py
│   └── constants.py         # Tax rates, bands, penalties
└── README.md
```

---

## 📊 Tax Calculations

### 2026 Personal Income Tax Bands

| Income Band | Rate |
|-------------|------|
| First ₦800,000 | 0% |
| ₦800,001 - ₦3,000,000 | 15% |
| ₦3,000,001 - ₦12,000,000 | 18% |
| ₦12,000,001 - ₦25,000,000 | 21% |
| ₦25,000,001 - ₦50,000,000 | 23% |
| Above ₦50,000,000 | 25% |

### Key Deductions

| Deduction | Rate/Cap |
|-----------|----------|
| Pension | 8% of pensionable earnings |
| NHF | 2.5% of basic (max ₦2,400/year) |
| NHIS | 5% of basic |
| Rent Relief | 20% of gross (max ₦500,000) |
| Life Assurance | Actual (max ₦100,000) |

---

## 🛠️ Customization

### Adding New Tax Rules

Edit `utils/constants.py` to update:
- Tax bands and rates
- Deduction caps
- Penalty amounts
- Filing deadlines

### Styling

Edit `.streamlit/config.toml` to customize:
- Primary color
- Background colors
- Font settings

---

## 🔒 Data Privacy

- All calculations happen locally in your browser
- No data is sent to external servers
- Record keeper uses session state (cleared on refresh)
- For persistent storage, export your records to JSON

---

## 📝 Roadmap

### Phase 2 (Coming Soon)
- [ ] User authentication
- [ ] Persistent database storage
- [ ] Bank statement import
- [ ] Auto-categorization of expenses
- [ ] PDF report generation

### Phase 3 (Future)
- [ ] Mobile app (React Native)
- [ ] Direct NRS filing integration
- [ ] Accountant dashboard
- [ ] Multi-business support

---

## ⚖️ Legal Disclaimer

This tool provides **estimates only** based on publicly available tax regulations. 
It does not constitute tax advice. Always consult a qualified tax professional 
for advice specific to your situation.

TaxReady Nigeria is not affiliated with the Nigeria Revenue Service (NRS) or 
any government agency.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

Questions? Feedback? Reach out:

- Email: your.email@example.com
- Twitter: @yourhandle
- LinkedIn: /in/yourprofile

---

**Built with ❤️ for Nigerian businesses**
