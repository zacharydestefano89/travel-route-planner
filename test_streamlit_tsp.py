#!/usr/bin/env python3
"""
Test script for Streamlit TSP integration
"""

from mapbox_matrix import solve_origin_destination_with_optional_stops_streamlit

def test_tsp_integration():
    """Test the TSP integration function."""
    
    print("🧪 Testing TSP Integration for Streamlit")
    print("="*50)
    
    # Test parameters
    origin = "Boston, MA"
    destination = "Washington, DC"
    optional_stops = ["New York, NY", "Philadelphia, PA"]
    
    print(f"🚀 Origin: {origin}")
    print(f"🎯 Destination: {destination}")
    print(f"📍 Optional Stops: {optional_stops}")
    print()
    
    # Run the function
    result = solve_origin_destination_with_optional_stops_streamlit(
        origin=origin,
        destination=destination,
        optional_stops=optional_stops
    )
    
    if result["success"]:
        print("✅ TSP calculation successful!")
        print(f"📊 Found {len(result['route_rankings'])} route combinations")
        print(f"⏱️  Fastest route: {result['summary_stats']['fastest_route']['duration_minutes']} minutes")
        print(f"📏 Shortest route: {result['summary_stats']['shortest_route_km']} km")
        
        print("\n📋 Route Rankings Preview:")
        for i, route in enumerate(result['route_rankings'][:3], 1):
            print(f"  {i}. {route['name']}")
            print(f"     Duration: {route['total_duration_minutes']} min")
            print(f"     Distance: {route['total_distance_km']} km")
            print(f"     Extra time: +{route['extra_duration_minutes']} min")
            print()
        
        return True
    else:
        print(f"❌ TSP calculation failed: {result['error']}")
        print(f"💡 Suggestion: {result['suggestion']}")
        return False

if __name__ == "__main__":
    test_tsp_integration() 