#!/usr/bin/env python3
"""
Example script to demonstrate the Travel Route Planner app.
This script shows how to run the app and provides sample usage.
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'streamlit',
        'pandas', 
        'folium',
        'streamlit_folium',
        'geopy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install them using:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed!")
    return True

def run_app():
    """Run the Streamlit app."""
    print("🚀 Starting Travel Route Planner...")
    print("📱 The app will open in your default browser at http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the app")
    print("-" * 50)
    
    try:
        # Run the Streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")

def show_sample_usage():
    """Show sample usage examples."""
    print("\n📖 Sample Usage Examples:")
    print("-" * 30)
    
    examples = [
        {
            "name": "Cross-Country Road Trip",
            "origin": "New York, NY",
            "destination": "Los Angeles, CA",
            "stops": [
                {"location": "Chicago, IL", "type": "Mandatory"},
                {"location": "Denver, CO", "type": "Optional"},
                {"location": "Las Vegas, NV", "type": "Mandatory"}
            ]
        },
        {
            "name": "European Tour",
            "origin": "London, UK",
            "destination": "Rome, Italy",
            "stops": [
                {"location": "Paris, France", "type": "Mandatory"},
                {"location": "Barcelona, Spain", "type": "Optional"},
                {"location": "Milan, Italy", "type": "Mandatory"}
            ]
        },
        {
            "name": "Weekend Getaway",
            "origin": "San Francisco, CA",
            "destination": "San Diego, CA",
            "stops": [
                {"location": "Monterey, CA", "type": "Optional"},
                {"location": "Santa Barbara, CA", "type": "Mandatory"}
            ]
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}")
        print(f"   Origin: {example['origin']}")
        print(f"   Destination: {example['destination']}")
        print("   Stops:")
        for stop in example['stops']:
            icon = "🔴" if stop['type'] == "Mandatory" else "🟡"
            print(f"     {icon} {stop['location']} ({stop['type']})")

def main():
    """Main function."""
    print("🗺️ Travel Route Planner - Example Runner")
    print("=" * 40)
    
    # Check if app.py exists
    if not os.path.exists("app.py"):
        print("❌ app.py not found! Make sure you're in the correct directory.")
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Show sample usage
    show_sample_usage()
    
    # Ask user if they want to run the app
    print("\n" + "=" * 40)
    response = input("🚀 Would you like to start the app now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        run_app()
    else:
        print("👋 To run the app later, use: streamlit run app.py")

if __name__ == "__main__":
    main() 