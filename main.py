import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date
import plotly.graph_objects as go
from streamlit_lottie import st_lottie

# -------------------------
# API Key
# -------------------------
import os

API_KEY = os.getenv("WEATHER_API_KEY")
if not API_KEY:
    st.error("API key not found! Please set WEATHER_API_KEY as an environment variable.")

# -------------------------
# Load Lottie animation
# -------------------------
def load_lottie(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

WEATHER_LOTTIE = {
    "Sunny": "https://assets3.lottiefiles.com/packages/lf20_sun.json",
    "Clear": "https://assets3.lottiefiles.com/packages/lf20_sun.json",
    "Partly cloudy": "https://assets5.lottiefiles.com/packages/lf20_cloudy.json",
    "Cloudy": "https://assets5.lottiefiles.com/packages/lf20_cloudy.json",
    "Rain": "https://assets3.lottiefiles.com/packages/lf20_rain.json",
    "Snow": "https://assets3.lottiefiles.com/packages/lf20_snow.json",
    "Thunderstorm": "https://assets3.lottiefiles.com/packages/lf20_thunder.json",
    "Mist": "https://assets3.lottiefiles.com/packages/lf20_fog.json",
}

def get_lottie_for_condition(condition):
    for key in WEATHER_LOTTIE.keys():
        if key.lower() in condition.lower():
            return load_lottie(WEATHER_LOTTIE[key])
    return None

# -------------------------
# Full-page animated background
# -------------------------
def set_full_bg_animation(condition, width, height):
    url = None
    if "sun" in condition.lower() or "clear" in condition.lower():
        url = "https://assets3.lottiefiles.com/packages/lf20_sun.json"
    elif "cloud" in condition.lower():
        url = "https://assets5.lottiefiles.com/packages/lf20_cloudy.json"
    elif "rain" in condition.lower() or "thunder" in condition.lower():
        url = "https://assets3.lottiefiles.com/packages/lf20_rain.json"
    elif "snow" in condition.lower():
        url = "https://assets3.lottiefiles.com/packages/lf20_snow.json"
    if url:
        lottie_bg = load_lottie(url)
        if lottie_bg:
            st_lottie(lottie_bg, height=height, width=width, key=f"bg_{condition}")

# -------------------------
# Overlay CSS
# -------------------------
def set_overlay_css():
    st.markdown("""
    <style>
    .overlay {
        background-color: rgba(255, 255, 255, 0.7);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
    }
    h1, h2, h3, h4, h5, h6, p, span {
        text-shadow: 1px 1px 3px black;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------
# Get weather data from WeatherAPI
# -------------------------
def get_weather(city):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=7&aqi=no&alerts=no"
    response = requests.get(url).json()
    if response.get("error"):
        return None
    current = response["current"]
    location = response["location"]
    forecast_days = response["forecast"]["forecastday"]
    forecast = []
    for day in forecast_days:
        forecast.append({
            "date": datetime.strptime(day["date"], "%Y-%m-%d"),
            "temp_day": day["day"]["maxtemp_c"],
            "temp_night": day["day"]["mintemp_c"],
            "weather": day["day"]["condition"]["text"],
            "wind_kph": day["day"]["maxwind_kph"],
            "humidity": day["day"]["avghumidity"],
            "chance_of_rain": day["day"]["daily_chance_of_rain"],
            "uv": day["day"]["uv"],
            "sunrise": day["astro"]["sunrise"],
            "sunset": day["astro"]["sunset"],
            "icon": "http:" + day["day"]["condition"]["icon"]
        })
    data = {
        "city": location["name"],
        "region": location["region"],
        "country": location["country"],
        "temp": current["temp_c"],
        "humidity": current["humidity"],
        "weather": current["condition"]["text"],
        "wind_kph": current["wind_kph"],
        "wind_dir": current["wind_dir"],
        "sunrise": forecast[0]["sunrise"],
        "sunset": forecast[0]["sunset"],
        "icon": "http:" + current["condition"]["icon"],
        "forecast": forecast
    }
    return data

# -------------------------
# Streamlit layout
# -------------------------
st.set_page_config(page_title="Weather Forecast", layout="wide")
st.title("🌤️  Weather Forecasting Information")
set_overlay_css()

cities_input = st.text_input("Enter cities separated by commas:", "Kathmandu,Lalitpur")
cities = [c.strip() for c in cities_input.split(",")]

# Responsive settings
screen_width = st.sidebar.slider("Screen width for preview (px)", 320, 1600, 800)
screen_height = st.sidebar.slider("Screen height for preview (px)", 400, 1600, 800)
is_mobile = screen_width < 700

comparison_df = pd.DataFrame()
download_df = pd.DataFrame()

# Layout for cities
if is_mobile:
    cols = [st.container() for _ in cities]  # vertical stacking
else:
    cols = st.columns(len(cities))  # multi-column

# -------------------------
# Loop through cities
# -------------------------
for i, city in enumerate(cities):
    weather = get_weather(city)
    with cols[i]:
        if weather:
            # Full-page background
            set_full_bg_animation(weather['weather'], screen_width, screen_height)
            st.markdown('<div class="overlay">', unsafe_allow_html=True)
            st.subheader(f"{weather['city']}, {weather['country']}")
            
            # Current weather Lottie/icon
            lottie_anim = get_lottie_for_condition(weather['weather'])
            width = min(screen_width//3, 300)
            if lottie_anim:
                st_lottie(lottie_anim, height=150, width=width)
            else:
                st.image(weather['icon'], width=60)
            
            st.write(f"**{weather['weather']}**")
            st.write(f"🌡 Temperature: {weather['temp']}°C")
            st.write(f"💧 Humidity: {weather['humidity']}%")
            st.write(f"🌬 Wind: {weather['wind_kph']} kph {weather['wind_dir']}")
            st.write(f"🌅 Sunrise: {weather['sunrise']} | 🌇 Sunset: {weather['sunset']}")
            
            # Forecast date selection
            selected_date = st.date_input(
                f"Select a date for {weather['city']}",
                value=date.today(),
                min_value=date.today(),
                max_value=date.today() + pd.Timedelta(days=6)
            )
            forecast_for_date = next((d for d in weather["forecast"] if d["date"].date() == selected_date), None)
            if forecast_for_date:
                st.markdown(f"**Forecast on {selected_date.strftime('%A, %d %B %Y')}:**")
                lottie_forecast = get_lottie_for_condition(forecast_for_date['weather'])
                if lottie_forecast:
                    st_lottie(lottie_forecast, height=120, width=width)
                else:
                    st.image(forecast_for_date['icon'], width=50)
                
                st.write(f"🌡 Day Temp: {forecast_for_date['temp_day']}°C")
                st.write(f"🌡 Night Temp: {forecast_for_date['temp_night']}°C")
                st.write(f"🌤 Condition: {forecast_for_date['weather']}")
                st.write(f"💧 Humidity: {forecast_for_date['humidity']}%")
                st.write(f"🌬 Wind: {forecast_for_date['wind_kph']} kph")
                st.write(f"🌧 Chance of Rain: {forecast_for_date['chance_of_rain']}%")
                st.write(f"🌞 UV Index: {forecast_for_date['uv']}")
                st.write(f"🌅 Sunrise: {forecast_for_date['sunrise']} | 🌇 Sunset: {forecast_for_date['sunset']}")
                
                # Extreme alerts
                if forecast_for_date["temp_day"] > 35:
                    st.markdown("⚠️ **Hot day alert!** 🔥")
                elif forecast_for_date["temp_day"] < 10:
                    st.markdown("❄️ **Cold day alert!** 🥶")
                if forecast_for_date["uv"] >= 7:
                    st.markdown("⚠️ **High UV Index!** 🌞")
                if forecast_for_date["chance_of_rain"] >= 50:
                    st.markdown("💧 **High chance of rain!** 🌧️")
            
            # Add to comparison dataframe
            temp_df = pd.DataFrame(weather["forecast"])[["date","temp_day","temp_night"]]
            temp_df = temp_df.set_index("date").rename(
                columns={"temp_day": f"{weather['city']}_day", "temp_night": f"{weather['city']}_night"})
            comparison_df = pd.concat([comparison_df, temp_df], axis=1)
            
            # Add to CSV download dataframe
            city_csv_df = pd.DataFrame(weather["forecast"])
            city_csv_df["city"] = weather["city"]
            download_df = pd.concat([download_df, city_csv_df], ignore_index=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error(f"City '{city}' not found!")

# -------------------------
# Plotly temperature comparison chart
# -------------------------
if not comparison_df.empty:
    st.markdown("## 🌡 Temperature Comparison Across Cities")
    fig = go.Figure()
    for col in comparison_df.columns:
        fig.add_trace(go.Scatter(
            x=comparison_df.index, y=comparison_df[col], mode='lines+markers', name=col
        ))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Temperature (°C)",
        legend_title="Cities",
        hovermode="x unified",
        width=min(screen_width, 1000)
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# CSV download
# -------------------------
if not download_df.empty:
    st.markdown("## 📥 Download Forecast Data")
    st.download_button("Download CSV", download_df.to_csv(index=False), "weather_forecast.csv", "text/csv")

st.markdown("---")
st.info("Data provided by [WeatherAPI](https://www.weatherapi.com/)")
