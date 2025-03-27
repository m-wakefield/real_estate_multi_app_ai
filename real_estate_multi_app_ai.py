import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="PropWise - AI Powered Real Estate Analyzer", layout="wide")
st.title("🏠 PropWise - Multi-Property Investment Analyzer (AI Powered)")

st.info("📱 On mobile? Tap the top-left menu ☰ to enter property info.")

# Initialize session state for properties
if "properties" not in st.session_state:
    st.session_state.properties = []

st.sidebar.header("📋 Enter Property Info")
st.sidebar.markdown("👈 Fill in the fields below and click 'Add Property'.")

# Basic property info
name = st.sidebar.text_input("Property Name", value="Property A")
address = st.sidebar.text_input("Address", value="123 Main St")
zip_code = st.sidebar.text_input("ZIP Code", value="12345")
image_url = st.sidebar.text_input("Image URL (optional)", value="")

sqft = st.sidebar.number_input("Square Footage", value=1500)
price = st.sidebar.number_input("Purchase Price ($)", value=200000)
down = st.sidebar.number_input("Down Payment ($)", value=40000)
interest = st.sidebar.number_input("Interest Rate (%)", value=6.5)
loan_term = st.sidebar.number_input("Loan Term (years)", value=30)
tax = st.sidebar.number_input("Annual Property Tax ($)", value=3600)
insurance = st.sidebar.number_input("Annual Insurance ($)", value=1200)
maint = st.sidebar.number_input("Monthly Maintenance ($)", value=150)
vacancy = st.sidebar.slider("Vacancy Rate (%)", min_value=0, max_value=20, value=5)

rent_est = st.sidebar.number_input("Expected Monthly Rent ($)", value=1800)
appreciation = st.sidebar.number_input("Annual Appreciation (%)", value=3.0)
hold = st.sidebar.number_input("Hold Period (years)", value=5)

rehab = st.sidebar.number_input("Rehab Cost ($)", value=30000)
resale = st.sidebar.number_input("Target Resale Price ($)", value=275000)

if st.sidebar.button("Add Property"):
    st.session_state.properties.append({
        "Name": name,
        "Address": address,
        "ZIP": zip_code,
        "Image": image_url,
        "SqFt": sqft,
        "Price": price,
        "Down": down,
        "Interest": interest,
        "LoanTerm": loan_term,
        "Tax": tax,
        "Insurance": insurance,
        "Maint": maint,
        "Vacancy": vacancy / 100,
        "Rent": rent_est,
        "Appreciation": appreciation,
        "Hold": hold,
        "Rehab": rehab,
        "Resale": resale
    })

# -----------------------------
# AI-Powered Suggestions
# -----------------------------
def smart_rent_estimate(sqft, zip_code):
    # For demonstration, we use a simple model based on square footage.
    low_rate = 1.1  # $ per sqft
    high_rate = 1.3
    return sqft * low_rate, sqft * high_rate

def investment_type_recommendation(roi, cash_flow, flip_profit):
    if roi >= 10 and cash_flow > 0:
        return "Best as a Rental"
    elif flip_profit > 0 and roi < 10:
        return "Good for Flipping"
    elif roi < 5 and cash_flow < 0:
        return "Bad Buy"
    else:
        return "Depends — Evaluate Further"

def smart_summary(name, roi, annual_cf, net_rent):
    return (f"{name} is projected to generate an annual cash flow of ${annual_cf:.2f} "
            f"with an ROI of {roi:.2f}%. The net rent collected is ${net_rent:.2f} per month, "
            "making it a compelling investment.")

# -----------------------------
# Display and Comparison
# -----------------------------
if st.session_state.properties:
    st.subheader("📊 Property Comparison")
    comparison_data = []
    for prop in st.session_state.properties:
        loan_amt = prop["Price"] - prop["Down"]
        monthly_interest = prop["Interest"] / 12 / 100
        months = prop["LoanTerm"] * 12
        mortgage = loan_amt * (monthly_interest * (1 + monthly_interest)**months) / ((1 + monthly_interest)**months - 1)
        tax_m = prop["Tax"] / 12
        ins_m = prop["Insurance"] / 12
        total_monthly = mortgage + tax_m + ins_m + prop["Maint"]
        net_rent = prop["Rent"] * (1 - prop["Vacancy"])
        cash_flow = net_rent - total_monthly
        annual_cf = cash_flow * 12
        future_value = prop["Price"] * ((1 + prop["Appreciation"] / 100) ** prop["Hold"])
        appreciation_gain = future_value - prop["Price"]
        total_invested = prop["Down"] + (prop["Maint"] * 12 * prop["Hold"])
        roi = ((annual_cf * prop["Hold"]) + appreciation_gain) / total_invested * 100
        flip_profit = prop["Resale"] - prop["Price"] - prop["Rehab"]

        # AI suggestions
        rent_low, rent_high = smart_rent_estimate(prop["SqFt"], prop["ZIP"])
        invest_recommend = investment_type_recommendation(roi, cash_flow, flip_profit)
        summary = smart_summary(prop["Name"], roi, annual_cf, net_rent)

        comparison_data.append({
            "Name": prop["Name"],
            "Address": prop["Address"],
            "ZIP": prop["ZIP"],
            "Image": prop["Image"],
            "Monthly Cost": round(total_monthly, 2),
            "Net Rent": round(net_rent, 2),
            "Cash Flow": round(cash_flow, 2),
            "Annual Profit": round(annual_cf, 2),
            "ROI (%)": round(roi, 2),
            "Flip Profit": round(flip_profit, 2),
            "Rent Range": f"${rent_low:.2f} - ${rent_high:.2f}",
            "Investment Type": invest_recommend,
            "Summary": summary
        })

    df = pd.DataFrame(comparison_data)

    # Display each property with AI insights
    for i, row in df.iterrows():
        st.markdown(f"### {row['Name']} ({row['ZIP']})")
        st.write(f"**Address:** {row['Address']}")
        if row["Image"]:
            st.image(row["Image"], width=400)
        st.write(f"**Monthly Cost:** ${row['Monthly Cost']} | **Net Rent:** ${row['Net Rent']} | **Cash Flow:** ${row['Cash Flow']}")
        st.write(f"**Annual Profit:** ${row['Annual Profit']} | **ROI:** {row['ROI (%)']}% | **Flip Profit:** ${row['Flip Profit']}")
        st.write(f"**Smart Rent Estimate:** {row['Rent Range']}")
        st.write(f"**Investment Type:** {row['Investment Type']}")
        st.write(f"**Summary:** {row['Summary']}")
        st.markdown("---")

    # ROI Comparison Chart
    st.subheader("📈 ROI Comparison")
    fig, ax = plt.subplots()
    ax.bar(df["Name"], df["ROI (%)"], color="teal")
    ax.set_ylabel("ROI (%)")
    ax.set_title("Return on Investment by Property")
    st.pyplot(fig)

    # Export to Excel
    st.subheader("📤 Export to Excel")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Properties")
    st.download_button("Download Excel File", buffer.getvalue(), file_name="propwise_ai_analysis.xlsx")
else:
    st.warning("No properties added yet. Use the sidebar to input and add a property.")
