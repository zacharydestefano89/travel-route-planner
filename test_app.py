#!/usr/bin/env python3
"""
Test script to verify the Travel Route Planner app functionality.
This script tests the core functions without running the full Streamlit server.
"""

import sys
import os
import json
from datetime import datetime

# Add the current directory to the path so we can import app functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_geocoding():
    """Test geocoding functionality."""
    print("🧪 Testing geocoding...")
    
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="travel_route_planner_test")
        
        # Test a simple location
        location = geolocator.geocode("New York, NY")
        if location:
            print(f"✅ Geocoding works: New York, NY -> ({location.latitude}, {location.longitude})")
            return True
        else:
            print("❌ Geocoding failed for New York, NY")
            return False
    except Exception as e:
        print(f"❌ Geocoding error: {e}")
        return False

def test_data_structures():
    """Test data structure creation and manipulation."""
    print("\n🧪 Testing data structures...")
    
    # Test stop data structure
    test_stop = {
        "location": "Chicago, IL",
        "type": "Mandatory",
        "id": 0
    }
    
    # Test route data structure
    test_route = {
        "origin": "New York, NY",
        "destination": "Los Angeles, CA",
        "stops": [test_stop],
        "created_at": datetime.now().isoformat()
    }
    
    try:
        # Test JSON serialization
        json_str = json.dumps(test_route, indent=2)
        parsed_route = json.loads(json_str)
        
        assert parsed_route["origin"] == "New York, NY"
        assert parsed_route["destination"] == "Los Angeles, CA"
        assert len(parsed_route["stops"]) == 1
        assert parsed_route["stops"][0]["type"] == "Mandatory"
        
        print("✅ Data structures work correctly")
        return True
    except Exception as e:
        print(f"❌ Data structure error: {e}")
        return False

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    required_modules = [
        'streamlit',
        'pandas',
        'folium',
        'streamlit_folium',
        'geopy',
        'json',
        'datetime'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All imports successful")
        return True

def test_app_file():
    """Test that the app.py file exists and is valid Python."""
    print("\n🧪 Testing app.py file...")
    
    if not os.path.exists("app.py"):
        print("❌ app.py file not found")
        return False
    
    try:
        with open("app.py", "r") as f:
            content = f.read()
        
        # Basic syntax check
        compile(content, "app.py", "exec")
        print("✅ app.py is valid Python")
        
        # Check for required functions
        required_functions = [
            "main",
            "show_route_planning",
            "show_route_summary", 
            "show_map_view"
        ]
        
        missing_functions = []
        for func in required_functions:
            if f"def {func}(" not in content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"❌ Missing functions: {', '.join(missing_functions)}")
            return False
        else:
            print("✅ All required functions found")
            return True
            
    except SyntaxError as e:
        print(f"❌ Syntax error in app.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def test_requirements():
    """Test that requirements.txt exists and has required packages."""
    print("\n🧪 Testing requirements.txt...")
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    required_packages = [
        "streamlit",
        "pandas", 
        "folium",
        "streamlit-folium",
        "geopy"
    ]
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        missing_packages = []
        for package in required_packages:
            if package not in content:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            return False
        else:
            print("✅ All required packages listed")
            return True
            
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Travel Route Planner - Test Suite")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("App File", test_app_file),
        ("Requirements", test_requirements),
        ("Data Structures", test_data_structures),
        ("Geocoding", test_geocoding)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The app should work correctly.")
        print("\n🚀 To run the app:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 