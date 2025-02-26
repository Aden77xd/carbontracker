import streamlit as st

# Updated emission factors and average data
EMISSION_FACTORS = {
    "Malaysia": {
        "Transportation": 0.14,  # kgCO2/km
        "Electricity": 0.82,     # kgCO2/kWh
        "Diet": 1.25,            # kgCO2/meal
        "Waste": 0.1             # kgCO2/kg
    }
}

# Add national average emissions (tonnes CO2/year per capita)
NATIONAL_AVERAGES = {
    "Malaysia": 7.7,  # Source: World Bank 2021 data
    # Add more countries as needed
}

st.set_page_config(layout="wide", page_title="Personal Carbon Calculator")
st.title("Personal Carbon Calculator App ⚠️")

# User inputs
st.subheader("🌍 Your Country")
country = st.selectbox("Select", ["Malaysia"])

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚗 Daily commute distance (in km)")
    distance = st.slider("Distance", 0.0, 100.0, 10.0)

    st.subheader("💡 Monthly electricity consumption (in kWh)")
    electricity = st.slider("Electricity", 0.0, 1000.0, 200.0)

with col2:
    st.subheader("🍽️ Waste generated per week (in kg)")
    waste = st.slider("Waste", 0.0, 100.0, 5.0)

    st.subheader("🍽️ Number of meals per day")
    meals = st.number_input("Meals", 1, 10, 3)

# Convert inputs to yearly
distance *= 365
electricity *= 12
meals *= 365
waste *= 52

# Calculate emissions
transportation_emissions = EMISSION_FACTORS[country]["Transportation"] * distance
electricity_emissions = EMISSION_FACTORS[country]["Electricity"] * electricity
diet_emissions = EMISSION_FACTORS[country]["Diet"] * meals
waste_emissions = EMISSION_FACTORS[country]["Waste"] * waste

# Convert to tonnes and round
transportation_emissions = round(transportation_emissions / 1000, 2)
electricity_emissions = round(electricity_emissions / 1000, 2)
diet_emissions = round(diet_emissions / 1000, 2)
waste_emissions = round(waste_emissions / 1000, 2)

total_emissions = round(
    transportation_emissions + electricity_emissions + diet_emissions + waste_emissions, 2
)

if st.button("Calculate CO2 Emissions"):
    st.header("Results")
    
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Carbon Emissions by Category")
        st.info(f"🚗 Transportation: {transportation_emissions} tonnes CO2/year")
        st.info(f"💡 Electricity: {electricity_emissions} tonnes CO2/year")
        st.info(f"🍽️ Diet: {diet_emissions} tonnes CO2/year")
        st.info(f"🗑️ Waste: {waste_emissions} tonnes CO2/year")
    
    with col4:
        st.subheader("Total Carbon Footprint")
        st.success(f"🌍 Your total footprint: {total_emissions} tonnes CO2/year")
        
        # Get national average from database
        national_average = NATIONAL_AVERAGES.get(country, 7.7)  # Default to Malaysia if not found
        
        # Calculate comparison metrics
        difference = total_emissions - national_average
        percentage_diff = (difference / national_average) * 100
        
        # Display comparison
        st.subheader("🇲🇾 National Comparison")
        
        if difference > 0:
            st.error(f"🚨 Your emissions are {abs(percentage_diff):.1f}% HIGHER than the Malaysian average ({national_average} tonnes)")
        else:
            st.success(f"🎉 Your emissions are {abs(percentage_diff):.1f}% LOWER than the Malaysian average ({national_average} tonnes)")
        
        # Add visual progress bar
        st.markdown(f"""
        <div style="margin-top: 20px">
            <div style="display: flex; justify-content: space-between">
                <span>Your Footprint</span>
                <span>{total_emissions} tonnes</span>
            </div>
            <div style="background: #eee; height: 20px; border-radius: 10px">
                <div style="background: {'#ff4b4b' if difference > 0 else '#2ecc71'}; 
                            width: {min(abs(percentage_diff), 100)}%; 
                            height: 100%; 
                            border-radius: 10px">
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 5px">
                <span>National Average</span>
                <span>{national_average} tonnes</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
