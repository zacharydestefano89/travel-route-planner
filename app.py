import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Travel Route Planner",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .stop-card {
        background-color: #6c757d;
        color: white;
        padding: 1.2rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .mandatory {
        border-left-color: #e74c3c !important;
        background-color: #495057 !important;
    }
    .optional {
        border-left-color: #f39c12 !important;
        background-color: #6c757d !important;
    }
    .stop-info {
        color: white !important;
        font-weight: 500;
    }
    .stop-badge {
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stop-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }
    .route-summary {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'stops' not in st.session_state:
    st.session_state.stops = []
if 'origin' not in st.session_state:
    st.session_state.origin = ""
if 'destination' not in st.session_state:
    st.session_state.destination = ""

def main():
    # Header
    st.markdown('<h1 class="main-header">🗺️ Travel Route Planner</h1>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Choose a page:",
            ["Route Planning", "Route Summary", "Map View"]
        )
    
    if page == "Route Planning":
        show_route_planning()
    elif page == "Route Summary":
        show_route_summary()
    elif page == "Map View":
        show_map_view()

def show_route_planning():
    st.markdown('<h2 class="section-header">Plan Your Journey</h2>', unsafe_allow_html=True)
    
    # Origin and Destination
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Origin")
        origin = st.text_input(
            "Enter your starting point:",
            value=st.session_state.origin,
            placeholder="e.g., New York, NY",
            key="origin_input"
        )
        st.session_state.origin = origin
    
    with col2:
        st.subheader("🎯 Destination")
        destination = st.text_input(
            "Enter your final destination:",
            value=st.session_state.destination,
            placeholder="e.g., Los Angeles, CA",
            key="destination_input"
        )
        st.session_state.destination = destination
    
    st.markdown("---")
    
    # Stops Management
    st.markdown('<h2 class="section-header">🚏 Stops Along the Way</h2>', unsafe_allow_html=True)
    
    # Add new stop
    with st.expander("➕ Add New Stop", expanded=False):
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            new_stop = st.text_input(
                "Stop location:",
                placeholder="e.g., Chicago, IL",
                key="new_stop_input"
            )
        
        with col2:
            stop_type = st.selectbox(
                "Stop type:",
                ["Optional", "Mandatory"],
                key="stop_type_input"
            )
        
        with col3:
            if st.button("Add Stop", key="add_stop_btn"):
                if new_stop and len(st.session_state.stops) < 10:
                    stop_data = {
                        "location": new_stop,
                        "type": stop_type,
                        "id": len(st.session_state.stops)
                    }
                    st.session_state.stops.append(stop_data)
                    st.success(f"Added {new_stop} as {stop_type.lower()} stop!")
                    st.rerun()
                elif len(st.session_state.stops) >= 10:
                    st.error("Maximum 10 stops allowed!")
                else:
                    st.error("Please enter a stop location!")
    
    # Display current stops
    if st.session_state.stops:
        st.subheader(f"Current Stops ({len(st.session_state.stops)}/10)")
        
        for i, stop in enumerate(st.session_state.stops):
            stop_class = "mandatory" if stop["type"] == "Mandatory" else "optional"
            badge_color = "#e74c3c" if stop["type"] == "Mandatory" else "#f39c12"
            
            with st.container():
                st.markdown(f"""
                <div class="stop-card {stop_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="stop-info">
                            <strong style="font-size: 1.1rem;">Stop {i+1}:</strong> 
                            <span style="font-size: 1.1rem; margin-left: 0.5rem;">{stop['location']}</span>
                            <span class="stop-badge" style="background-color: {badge_color}; color: white; padding: 0.3rem 0.6rem; border-radius: 0.4rem; font-size: 0.75rem; margin-left: 0.8rem; display: inline-block;">
                                {stop['type']}
                            </span>
                        </div>
                        <div style="margin-left: 1rem;">
                            <button onclick="removeStop({i})" style="background-color: #dc3545; color: white; border: none; border-radius: 0.4rem; padding: 0.4rem 0.8rem; cursor: pointer; font-weight: bold; transition: background-color 0.2s;">
                                🗑️ Remove
                            </button>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Remove button functionality
                if st.button(f"Remove Stop {i+1}", key=f"remove_{i}"):
                    st.session_state.stops.pop(i)
                    st.rerun()
    else:
        st.markdown("""
        <div style="background-color: #e9ecef; border: 2px dashed #6c757d; border-radius: 0.5rem; padding: 2rem; text-align: center; color: #495057;">
            <h4 style="margin-bottom: 1rem; color: #495057;">📍 No Stops Added Yet</h4>
            <p style="margin: 0; font-size: 1rem;">Use the <strong>'Add New Stop'</strong> section above to add stops to your route.</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #6c757d;">You can add up to 10 stops and label them as mandatory or optional.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Route actions
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear All Stops", type="secondary"):
            st.session_state.stops = []
            st.rerun()
    
    with col2:
        if st.button("💾 Save Route", type="primary"):
            save_route()
    
    with col3:
        if st.button("📋 Load Route", type="secondary"):
            load_route()

def show_route_summary():
    st.markdown('<h2 class="section-header">📋 Route Summary</h2>', unsafe_allow_html=True)
    
    if not st.session_state.origin and not st.session_state.destination and not st.session_state.stops:
        st.warning("No route planned yet. Go to 'Route Planning' to create your journey!")
        return
    
    # Route overview
    st.markdown('<div class="route-summary">', unsafe_allow_html=True)
    st.subheader("Route Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Origin", st.session_state.origin or "Not set")
    
    with col2:
        st.metric("Destination", st.session_state.destination or "Not set")
    
    with col3:
        mandatory_count = sum(1 for stop in st.session_state.stops if stop["type"] == "Mandatory")
        optional_count = len(st.session_state.stops) - mandatory_count
        st.metric("Total Stops", f"{len(st.session_state.stops)} ({mandatory_count} mandatory, {optional_count} optional)")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed route
    if st.session_state.stops:
        st.subheader("Detailed Route")
        
        route_data = []
        route_data.append({
            "Order": 1,
            "Location": st.session_state.origin,
            "Type": "Origin",
            "Notes": "Starting point"
        })
        
        for i, stop in enumerate(st.session_state.stops):
            route_data.append({
                "Order": i + 2,
                "Location": stop["location"],
                "Type": stop["type"],
                "Notes": f"Stop {i + 1}"
            })
        
        route_data.append({
            "Order": len(st.session_state.stops) + 2,
            "Location": st.session_state.destination,
            "Type": "Destination",
            "Notes": "Final destination"
        })
        
        df = pd.DataFrame(route_data)
        st.dataframe(df, use_container_width=True)
        
        # Export options
        st.subheader("Export Route")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Export as JSON"):
                export_route_json()
        
        with col2:
            if st.button("📊 Export as CSV"):
                export_route_csv(df)

def show_map_view():
    st.markdown('<h2 class="section-header">🗺️ Route Map</h2>', unsafe_allow_html=True)
    
    if not st.session_state.origin and not st.session_state.destination:
        st.warning("Please set origin and destination in the Route Planning section to view the map.")
        return
    
    try:
        # Create map
        geolocator = Nominatim(user_agent="travel_route_planner")
        
        # Get coordinates for origin
        if st.session_state.origin:
            origin_location = geolocator.geocode(st.session_state.origin)
            if origin_location:
                center_lat, center_lon = origin_location.latitude, origin_location.longitude
            else:
                center_lat, center_lon = 40.7128, -74.0060  # Default to NYC
        else:
            center_lat, center_lon = 40.7128, -74.0060  # Default to NYC
        
        # Create map
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        
        # Add origin marker
        if st.session_state.origin and origin_location:
            folium.Marker(
                [origin_location.latitude, origin_location.longitude],
                popup=f"<b>Origin:</b> {st.session_state.origin}",
                icon=folium.Icon(color='green', icon='play')
            ).add_to(m)
        
        # Add destination marker
        if st.session_state.destination:
            dest_location = geolocator.geocode(st.session_state.destination)
            if dest_location:
                folium.Marker(
                    [dest_location.latitude, dest_location.longitude],
                    popup=f"<b>Destination:</b> {st.session_state.destination}",
                    icon=folium.Icon(color='red', icon='flag')
                ).add_to(m)
        
        # Add stop markers
        for i, stop in enumerate(st.session_state.stops):
            stop_location = geolocator.geocode(stop["location"])
            if stop_location:
                icon_color = 'orange' if stop["type"] == "Mandatory" else 'blue'
                folium.Marker(
                    [stop_location.latitude, stop_location.longitude],
                    popup=f"<b>Stop {i+1}:</b> {stop['location']}<br><b>Type:</b> {stop['type']}",
                    icon=folium.Icon(color=icon_color, icon='info-sign')
                ).add_to(m)
        
        # Display map
        folium_static(m, width=800, height=600)
        
    except Exception as e:
        st.error(f"Error loading map: {str(e)}")
        st.info("Please check your internet connection and try again.")

def save_route():
    route_data = {
        "origin": st.session_state.origin,
        "destination": st.session_state.destination,
        "stops": st.session_state.stops,
        "created_at": datetime.now().isoformat()
    }
    
    # Save to session state for now (in a real app, you'd save to a database or file)
    st.session_state.saved_route = route_data
    st.success("Route saved successfully!")

def load_route():
    if hasattr(st.session_state, 'saved_route'):
        route_data = st.session_state.saved_route
        st.session_state.origin = route_data.get("origin", "")
        st.session_state.destination = route_data.get("destination", "")
        st.session_state.stops = route_data.get("stops", [])
        st.success("Route loaded successfully!")
        st.rerun()
    else:
        st.warning("No saved route found!")

def export_route_json():
    route_data = {
        "origin": st.session_state.origin,
        "destination": st.session_state.destination,
        "stops": st.session_state.stops,
        "exported_at": datetime.now().isoformat()
    }
    
    st.download_button(
        label="Download JSON",
        data=json.dumps(route_data, indent=2),
        file_name=f"route_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def export_route_csv(df):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"route_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main() 