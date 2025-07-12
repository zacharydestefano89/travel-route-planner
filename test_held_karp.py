#!/usr/bin/env python3
"""
Test script for Held-Karp algorithm implementation
"""

from mapbox_matrix import MapboxMatrixAPI, TSPSolver

def test_held_karp_algorithm():
    """Test the Held-Karp algorithm with a simple example."""
    
    print("🧪 Testing Held-Karp Algorithm Implementation")
    print("="*50)
    
    # Test with a small set of locations
    test_locations = [
        "Boston, MA",
        "New York, NY", 
        "Philadelphia, PA",
        "Washington, DC"
    ]
    
    print(f"📍 Test locations: {test_locations}")
    print(f"🔢 Number of locations: {len(test_locations)}")
    print()
    
    try:
        # Initialize API and solver
        api = MapboxMatrixAPI()
        solver = TSPSolver(api)
        
        # Test Held-Karp algorithm
        print("🔍 Testing Held-Karp algorithm...")
        route = solver._solve_tsp_held_karp(
            locations=test_locations,
            distance_lookup={
                "Boston, MA": {"Boston, MA": 0, "New York, NY": 300, "Philadelphia, PA": 450, "Washington, DC": 650},
                "New York, NY": {"Boston, MA": 300, "New York, NY": 0, "Philadelphia, PA": 150, "Washington, DC": 350},
                "Philadelphia, PA": {"Boston, MA": 450, "New York, NY": 150, "Philadelphia, PA": 0, "Washington, DC": 200},
                "Washington, DC": {"Boston, MA": 650, "New York, NY": 350, "Philadelphia, PA": 200, "Washington, DC": 0}
            },
            duration_lookup={
                "Boston, MA": {"Boston, MA": 0, "New York, NY": 180, "Philadelphia, PA": 270, "Washington, DC": 390},
                "New York, NY": {"Boston, MA": 180, "New York, NY": 0, "Philadelphia, PA": 90, "Washington, DC": 210},
                "Philadelphia, PA": {"Boston, MA": 270, "New York, NY": 90, "Philadelphia, PA": 0, "Washington, DC": 120},
                "Washington, DC": {"Boston, MA": 390, "New York, NY": 210, "Philadelphia, PA": 120, "Washington, DC": 0}
            },
            start_location="Boston, MA",
            end_location="Washington, DC",
            return_to_start=False
        )
        
        if route:
            print("✅ Held-Karp algorithm successful!")
            print(f"🗺️  Optimal path: {' → '.join(route.path)}")
            print(f"📏 Total distance: {route.total_distance:.2f} km")
            print(f"⏱️  Total duration: {route.total_duration:.1f} minutes")
            print()
            
            # Test with start and end constraints
            print("🔍 Testing with start/end constraints...")
            route_constrained = solver._solve_tsp_held_karp(
                locations=test_locations,
                distance_lookup={
                    "Boston, MA": {"Boston, MA": 0, "New York, NY": 300, "Philadelphia, PA": 450, "Washington, DC": 650},
                    "New York, NY": {"Boston, MA": 300, "New York, NY": 0, "Philadelphia, PA": 150, "Washington, DC": 350},
                    "Philadelphia, PA": {"Boston, MA": 450, "New York, NY": 150, "Philadelphia, PA": 0, "Washington, DC": 200},
                    "Washington, DC": {"Boston, MA": 650, "New York, NY": 350, "Philadelphia, PA": 200, "Washington, DC": 0}
                },
                duration_lookup={
                    "Boston, MA": {"Boston, MA": 0, "New York, NY": 180, "Philadelphia, PA": 270, "Washington, DC": 390},
                    "New York, NY": {"Boston, MA": 180, "New York, NY": 0, "Philadelphia, PA": 90, "Washington, DC": 210},
                    "Philadelphia, PA": {"Boston, MA": 270, "New York, NY": 90, "Philadelphia, PA": 0, "Washington, DC": 120},
                    "Washington, DC": {"Boston, MA": 390, "New York, NY": 210, "Philadelphia, PA": 120, "Washington, DC": 0}
                },
                start_location="Boston, MA",
                end_location="Washington, DC",
                return_to_start=True
            )
            
            if route_constrained:
                print("✅ Constrained Held-Karp algorithm successful!")
                print(f"🗺️  Optimal path: {' → '.join(route_constrained.path)}")
                print(f"📏 Total distance: {route_constrained.total_distance:.2f} km")
                print(f"⏱️  Total duration: {route_constrained.total_duration:.1f} minutes")
            else:
                print("❌ Constrained Held-Karp algorithm failed")
                
        else:
            print("❌ Held-Karp algorithm failed")
            
    except Exception as e:
        print(f"❌ Error testing Held-Karp: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_held_karp_algorithm() 