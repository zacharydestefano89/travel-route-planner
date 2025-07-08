#!/usr/bin/env python3
"""
Example usage of the Mapbox Matrix API script.

This script demonstrates different ways to use the MapboxMatrixAPI class
with various travel profiles and configurations.
"""

import os
from mapbox_matrix import MapboxMatrixAPI
from dotenv import load_dotenv

def example_basic_usage():
    """Basic usage example with hardcoded locations."""
    print("🚀 Example 1: Basic Usage")
    print("="*40)
    
    # Hardcoded locations
    locations = [
        "San Francisco, CA",
        "Los Angeles, CA",
        "San Diego, CA"
    ]
    
    try:
        api = MapboxMatrixAPI()
        
        # Geocode locations
        coordinates = []
        valid_locations = []
        
        for location in locations:
            coords = api.geocode_location(location)
            if coords:
                coordinates.append(coords)
                valid_locations.append(location)
        
        # Get matrix
        matrix_data = api.get_matrix(coordinates, profile="driving")
        
        if matrix_data:
            results = api.format_matrix_results(matrix_data, valid_locations)
            api.print_matrix_results(results)
        
    except Exception as e:
        print(f"Error: {e}")

def example_multiple_profiles():
    """Example with multiple travel profiles."""
    print("\n🚀 Example 2: Multiple Travel Profiles")
    print("="*40)
    
    locations = [
        "New York, NY",
        "Boston, MA"
    ]
    
    profiles = ["driving", "walking", "cycling"]
    
    try:
        api = MapboxMatrixAPI()
        
        # Geocode locations
        coordinates = []
        valid_locations = []
        
        for location in locations:
            coords = api.geocode_location(location)
            if coords:
                coordinates.append(coords)
                valid_locations.append(location)
        
        # Get matrix for each profile
        for profile in profiles:
            print(f"\n🚗 {profile.upper()} Profile:")
            print("-" * 20)
            
            matrix_data = api.get_matrix(coordinates, profile=profile)
            
            if matrix_data:
                results = api.format_matrix_results(matrix_data, valid_locations)
                api.print_matrix_results(results)
        
    except Exception as e:
        print(f"Error: {e}")

def example_custom_annotations():
    """Example with custom annotations."""
    print("\n🚀 Example 3: Custom Annotations")
    print("="*40)
    
    locations = [
        "Chicago, IL",
        "Detroit, MI",
        "Cleveland, OH"
    ]
    
    try:
        api = MapboxMatrixAPI()
        
        # Geocode locations
        coordinates = []
        valid_locations = []
        
        for location in locations:
            coords = api.geocode_location(location)
            if coords:
                coordinates.append(coords)
                valid_locations.append(location)
        
        # Get matrix with custom annotations
        matrix_data = api.get_matrix(
            coordinates=coordinates,
            profile="driving-traffic",  # Real-time traffic
            annotations=['duration', 'distance', 'speed']
        )
        
        if matrix_data:
            results = api.format_matrix_results(matrix_data, valid_locations)
            api.print_matrix_results(results)
        
    except Exception as e:
        print(f"Error: {e}")

def example_error_handling():
    """Example showing error handling."""
    print("\n🚀 Example 4: Error Handling")
    print("="*40)
    
    # Test with invalid API token
    try:
        # Temporarily set invalid token
        original_token = os.getenv('MAPBOX_ACCESS_TOKEN')
        os.environ['MAPBOX_ACCESS_TOKEN'] = 'invalid_token'
        
        api = MapboxMatrixAPI()
        coords = api.geocode_location("New York, NY")
        
        print("This should show an error...")
        
    except ValueError as e:
        print(f"✅ Caught expected error: {e}")
    
    finally:
        # Restore original token
        if original_token:
            os.environ['MAPBOX_ACCESS_TOKEN'] = original_token
        else:
            os.environ.pop('MAPBOX_ACCESS_TOKEN', None)

def example_coordinate_input():
    """Example using direct coordinates instead of geocoding."""
    print("\n🚀 Example 5: Direct Coordinates")
    print("="*40)
    
    # Direct coordinates (longitude, latitude)
    coordinates = [
        (-74.006, 40.7128),  # New York
        (-71.0589, 42.3601), # Boston
        (-75.1652, 39.9526)  # Philadelphia
    ]
    
    locations = ["New York, NY", "Boston, MA", "Philadelphia, PA"]
    
    try:
        api = MapboxMatrixAPI()
        
        # Get matrix directly with coordinates
        matrix_data = api.get_matrix(coordinates, profile="driving")
        
        if matrix_data:
            results = api.format_matrix_results(matrix_data, locations)
            api.print_matrix_results(results)
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all examples."""
    print("🗺️ Mapbox Matrix API Examples")
    print("="*50)

    load_dotenv()
    
    # Check if API token is available
    if not os.getenv('MAPBOX_ACCESS_TOKEN'):
        print("⚠️  MAPBOX_ACCESS_TOKEN not set!")
        print("💡 Set it with: export MAPBOX_ACCESS_TOKEN='your_token_here'")
        print("   Or get one from: https://account.mapbox.com/")
        print()
        print("Running examples that don't require API calls...")
        example_error_handling()
        return
    
    # Run examples
    example_basic_usage()
    example_multiple_profiles()
    example_custom_annotations()
    example_error_handling()
    example_coordinate_input()
    
    print("\n✅ All examples completed!")

if __name__ == "__main__":
    main() 