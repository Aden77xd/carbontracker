import streamlit as st
import requests
from geopy.geocoders import Nominatim
import math
from streamlit_folium import folium_static
import folium
from folium.plugins import BeautifyIcon

# Constants
EMISSION_FACTORS = {
    "transportation": 0.14,  # kgCO2/km
    "electricity": 0.82,     # kgCO2/kWh
    "diet": 1.25,            # kgCO2/meal
    "waste": 0.1             # kgCO2/kg
}

COUNTRY_AVERAGES = {
    'MY': 7.7, 'US': 14.7, 'IN': 1.9, 'CN': 7.7, 'GLOBAL': 4.7
}

COUNTRY_POPULATIONS = {
    'MY': 33.57, 'US': 331.9, 'IN': 1408, 'CN': 1412
}

# Configure page
st.set_page_config(page_title="Carbon Calculator", layout="wide")
st.title("🌍 Complete Carbon Calculator")

# Initialize geocoder
geolocator = Nominatim(user_agent="carbon_calculator_app")

def get_coordinates(address):
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude), location.raw.get('display_name', '')
    return None, None

def get_route_distance(start, end):
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=false"
        response = requests.get(url)
        data = response.json()
        return data['routes'][0]['distance'] / 1000  # Convert to km
    except:
        # Fallback to straight-line distance
        return calculate_straight_distance(start, end)

def calculate_straight_distance(coord1, coord2):
    R = 6371  # Earth radius in km
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def calculate_emissions(inputs):
    emissions = {
        "transport": (inputs['distance'] * 2 * inputs['work_days'] * 
                     EMISSION_FACTORS['transportation']) / 1000,
        "electricity": (inputs['electricity'] * 12 * 
                       EMISSION_FACTORS['electricity']) / 1000,
        "diet": (inputs['meals'] * 365 * 
                EMISSION_FACTORS['diet']) / 1000,
        "waste": (inputs['waste'] * 52 * 
                 EMISSION_FACTORS['waste']) / 1000
    }
    emissions["total"] = sum(emissions.values())
    return emissions

# Input Section
with st.sidebar:
    st.header("Input Parameters")
    country = st.selectbox("Select Country", ["MY", "US", "IN", "CN"], index=0)
    home_address = st.text_input("Home Address", "Yayasan Selangor, Bukit Bintang, Kuala Lumpur")
    work_address = st.text_input("Work Address", "Menara Maybank, Kuala Lumpur")
    work_days = st.number_input("Work Days/Year", 230, 365, 230)
    electricity = st.number_input("Monthly Electricity (kWh)", 200, 2000, 200)
    waste = st.number_input("Weekly Waste (kg)", 1, 100, 5)
    meals = st.number_input("Daily Meals", 1, 10, 3)

# Geocode addresses
home_coords, home_full = get_coordinates(home_address)
work_coords, work_full = get_coordinates(work_address)

# Create map
if home_coords and work_coords:
    m = folium.Map(location=home_coords, zoom_start=12)
    folium.Marker(home_coords, popup="Home", icon=BeautifyIcon(icon="home")).add_to(m)
    folium.Marker(work_coords, popup="Work", icon=BeautifyIcon(icon="briefcase")).add_to(m)
    
    try:
        route = f"http://router.project-osrm.org/route/v1/driving/{home_coords[1]},{home_coords[0]};{work_coords[1]},{work_coords[0]}?overview=full&geometries=geojson"
        response = requests.get(route)
        data = response.json()
        route_geo = data['routes'][0]['geometry']
        folium.GeoJson(route_geo, name="Route").add_to(m)
    except:
        folium.PolyLine([home_coords, work_coords], color='red').add_to(m)
    
    with st.expander("View Map", expanded=True):
        folium_static(m, width=1200, height=400)

# Calculate emissions
if st.sidebar.button("Calculate Emissions"):
    if not home_coords or not work_coords:
        st.error("Please enter valid addresses")
    else:
        distance = get_route_distance(home_coords, work_coords)
        inputs = {
            "distance": distance,
            "work_days": work_days,
            "electricity": electricity,
            "waste": waste,
            "meals": meals
        }
        results = calculate_emissions(inputs)
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Emissions Breakdown")
            st.metric("🚗 Transportation", f"{results['transport']:.2f} tCO₂")
            st.metric("💡 Electricity", f"{results['electricity']:.2f} tCO₂")
            st.metric("🍽️ Diet", f"{results['diet']:.2f} tCO₂")
            st.metric("🗑️ Waste", f"{results['waste']:.2f} tCO₂")
            st.metric("🌍 Total Annual Emissions", f"{results['total']:.2f} tCO₂")
        
        with col2:
            st.subheader("🌱 Reduction Tips")
            max_category = max(results, key=lambda k: results[k] if k != "total" else 0)
            tips = {
                "transport": [
                    "🚗 Carpool twice weekly (20% reduction)",
                    "🚆 Try public transport (50% less CO₂)",
                    "🚴 Cycle for short trips (0 emissions)"
                ],
                "electricity": [
                    "💡 Switch to LED bulbs (75% savings)",
                    "☀️ Install solar panels (5-7 year ROI)",
                    "❄️ Set AC to 24°C (6% savings/degree)"
                ],
                "diet": [
                    "🥦 Meat-free days (beef = 60kg CO₂/kg)",
                    "🚚 Buy local produce (30% less transport)",
                    "🗑️ Reduce food waste (8% global emissions)"
                ],
                "waste": [
                    "♻️ Proper recycling (95% aluminum savings)",
                    "🍂 Start composting (50% less methane)",
                    "🛍️ Use reusable bags (1000yr decomposition)"
                ]
            }
            st.write(f"**Focus on {max_category.capitalize()}:**")
            for tip in tips.get(max_category, []):
                st.write(f"- {tip}")
