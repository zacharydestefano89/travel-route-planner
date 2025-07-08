#!/usr/bin/env python3
"""
Mapbox Matrix API Query Script

This script queries the Mapbox Matrix API to get travel times and distances
between multiple locations. For the initial version, locations are hardcoded.

The Matrix API returns a matrix of travel times and distances between all
pairs of coordinates in your request.

Requirements:
- Mapbox API key (set as environment variable MAPBOX_ACCESS_TOKEN)
- requests library
"""

import os
import requests
import json
from typing import List, Dict, Tuple, Optional, NamedTuple
from datetime import datetime
import time
from dotenv import load_dotenv
import itertools

class MapboxMatrixAPI:
    """Class to handle Mapbox Matrix API queries."""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the Mapbox Matrix API client.
        
        Args:
            access_token: Mapbox access token. If None, will try to get from environment.
        """
        load_dotenv()
        self.access_token = access_token or os.getenv('MAPBOX_ACCESS_TOKEN')
        if not self.access_token:
            raise ValueError("Mapbox access token is required. Set MAPBOX_ACCESS_TOKEN environment variable or pass it to the constructor.")
        
        self.base_url = "https://api.mapbox.com/directions-matrix/v1/mapbox"
        self.session = requests.Session()
    
    def geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Geocode a location string to coordinates using Mapbox Geocoding API.
        
        Args:
            location: Location string (e.g., "New York, NY")
            
        Returns:
            Tuple of (longitude, latitude) or None if geocoding fails
        """
        geocoding_url = "https://api.mapbox.com/geocoding/v5/mapbox.places"
        params = {
            'access_token': self.access_token,
            'q': location,
            'limit': 1,
            'types': 'place,address'
        }
        
        try:
            response = self.session.get(f"{geocoding_url}/{location}.json", params=params)
            response.raise_for_status()
            
            data = response.json()
            if data['features']:
                coords = data['features'][0]['center']  # [longitude, latitude]
                return tuple(coords)
            else:
                print(f"⚠️  Could not geocode: {location}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error geocoding {location}: {e}")
            return None
    
    def get_matrix(self, 
                   coordinates: List[Tuple[float, float]], 
                   profile: str = "driving",
                   annotations: List[str] = None) -> Optional[Dict]:
        """
        Get travel time and distance matrix from Mapbox.
        
        Args:
            coordinates: List of (longitude, latitude) tuples
            profile: Travel profile ('driving', 'walking', 'cycling', 'driving-traffic')
            annotations: List of annotations to return ('duration', 'distance', 'speed')
            
        Returns:
            Dictionary containing matrix data or None if request fails
        """
        if not coordinates:
            raise ValueError("At least one coordinate pair is required")
        
        if len(coordinates) > 25:
            raise ValueError("Maximum 25 coordinates allowed per request")
        
        # Default annotations
        if annotations is None:
            annotations = ['duration', 'distance']
        
        # Format coordinates as "longitude,latitude;longitude,latitude;..."
        coords_str = ";".join([f"{lon},{lat}" for lon, lat in coordinates])
        
        params = {
            'access_token': self.access_token,
            'annotations': ','.join(annotations)
        }
        
        url = f"{self.base_url}/{profile}/{coords_str}"
        
        try:
            print(f"🔄 Requesting matrix for {len(coordinates)} locations...")
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error requesting matrix: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def format_matrix_results(self, matrix_data: Dict, locations: List[str]) -> Dict:
        """
        Format matrix results into a more readable structure.
        
        Args:
            matrix_data: Raw matrix data from Mapbox API
            locations: List of location names corresponding to coordinates
            
        Returns:
            Formatted results dictionary
        """
        if not matrix_data or 'durations' not in matrix_data:
            return {}
        
        results = {
            'metadata': {
                'locations': locations,
                'profile': matrix_data.get('code', 'unknown'),
                'timestamp': datetime.now().isoformat()
            },
            'durations': {},
            'distances': {},
            'summary': {}
        }
        
        durations = matrix_data.get('durations', [])
        distances = matrix_data.get('distances', [])
        
        # Create duration matrix
        for i, row in enumerate(durations):
            if i < len(locations):
                results['durations'][locations[i]] = {}
                for j, duration in enumerate(row):
                    if j < len(locations):
                        if duration is not None:
                            # Convert seconds to minutes
                            results['durations'][locations[i]][locations[j]] = round(duration / 60, 1)
                        else:
                            results['durations'][locations[i]][locations[j]] = None
        
        # Create distance matrix
        for i, row in enumerate(distances):
            if i < len(locations):
                results['distances'][locations[i]] = {}
                for j, distance in enumerate(row):
                    if j < len(locations):
                        if distance is not None:
                            # Convert meters to kilometers
                            results['distances'][locations[i]][locations[j]] = round(distance / 1000, 2)
                        else:
                            results['distances'][locations[i]][locations[j]] = None
        
        # Create summary statistics
        total_duration = 0
        total_distance = 0
        valid_pairs = 0
        
        for i in range(len(locations)):
            for j in range(len(locations)):
                if i != j:  # Skip same location pairs
                    duration = results['durations'][locations[i]][locations[j]]
                    distance = results['distances'][locations[i]][locations[j]]
                    
                    if duration is not None and distance is not None:
                        total_duration += duration
                        total_distance += distance
                        valid_pairs += 1
        
        if valid_pairs > 0:
            results['summary'] = {
                'average_duration_minutes': round(total_duration / valid_pairs, 1),
                'average_distance_km': round(total_distance / valid_pairs, 2),
                'total_pairs': valid_pairs
            }
        
        return results
    
    def print_matrix_results(self, results: Dict):
        """
        Print formatted matrix results in a readable format.
        
        Args:
            results: Formatted results from format_matrix_results
        """
        if not results:
            print("❌ No results to display")
            return
        
        print("\n" + "="*60)
        print("🗺️ MAPBOX MATRIX API RESULTS")
        print("="*60)
        
        # Print metadata
        metadata = results.get('metadata', {})
        print(f"📅 Timestamp: {metadata.get('timestamp', 'Unknown')}")
        print(f"🚗 Profile: {metadata.get('profile', 'Unknown')}")
        print(f"📍 Locations: {len(metadata.get('locations', []))}")
        
        locations = metadata.get('locations', [])
        if not locations:
            return
        
        # Print duration matrix
        print("\n⏱️  TRAVEL TIMES (minutes):")
        print("-" * 60)
        
        # Header row
        header = f"{'From/To':<20}"
        for loc in locations:
            header += f"{loc[:15]:<15}"
        print(header)
        print("-" * 60)
        
        # Data rows
        durations = results.get('durations', {})
        for from_loc in locations:
            row = f"{from_loc[:19]:<20}"
            for to_loc in locations:
                duration = durations.get(from_loc, {}).get(to_loc)
                if duration is not None:
                    row += f"{duration:<15.1f}"
                else:
                    row += f"{'N/A':<15}"
            print(row)
        
        # Print distance matrix
        print("\n📏 DISTANCES (kilometers):")
        print("-" * 60)
        
        # Header row
        header = f"{'From/To':<20}"
        for loc in locations:
            header += f"{loc[:15]:<15}"
        print(header)
        print("-" * 60)
        
        # Data rows
        distances = results.get('distances', {})
        for from_loc in locations:
            row = f"{from_loc[:19]:<20}"
            for to_loc in locations:
                distance = distances.get(from_loc, {}).get(to_loc)
                if distance is not None:
                    row += f"{distance:<15.2f}"
                else:
                    row += f"{'N/A':<15}"
            print(row)
        
        # Print summary
        summary = results.get('summary', {})
        if summary:
            print("\n📊 SUMMARY STATISTICS:")
            print("-" * 60)
            print(f"Average Duration: {summary.get('average_duration_minutes', 0):.1f} minutes")
            print(f"Average Distance: {summary.get('average_distance_km', 0):.2f} km")
            print(f"Total Location Pairs: {summary.get('total_pairs', 0)}")
        
        print("="*60)

class Route(NamedTuple):
    """Represents a route with its total distance and path."""
    path: List[str]
    total_distance: float
    total_duration: float

class TSPSolver:
    """Traveling Salesman Problem solver for finding shortest path through all cities."""
    
    def __init__(self, matrix_api: MapboxMatrixAPI):
        """
        Initialize the TSP solver.
        
        Args:
            matrix_api: Initialized MapboxMatrixAPI instance
        """
        self.api = matrix_api
    
    def solve_tsp(self, 
                  locations: List[str], 
                  start_location: Optional[str] = None,
                  end_location: Optional[str] = None,
                  return_to_start: bool = True) -> Optional[Route]:
        """
        Solve the Traveling Salesman Problem to find the shortest path.
        
        Args:
            locations: List of location names to visit
            start_location: Optional starting location (must be in locations)
            end_location: Optional ending location (must be in locations)
            return_to_start: Whether to return to the starting location
            
        Returns:
            Route object with optimal path and metrics, or None if no solution
        """
        if len(locations) < 2:
            print("❌ Need at least 2 locations for TSP")
            return None
        
        if len(locations) > 10:
            print("⚠️  Warning: TSP complexity grows exponentially. This may take a while...")
        
        # Validate start and end locations
        if start_location and start_location not in locations:
            print(f"❌ Start location '{start_location}' not in locations list")
            return None
        
        if end_location and end_location not in locations:
            print(f"❌ End location '{end_location}' not in locations list")
            return None
        
        # Geocode all locations
        print("🔄 Geocoding locations for TSP...")
        coordinates = []
        valid_locations = []
        
        for location in locations:
            coords = self.api.geocode_location(location)
            if coords:
                coordinates.append(coords)
                valid_locations.append(location)
                print(f"✅ {location} -> ({coords[1]:.4f}, {coords[0]:.4f})")
            else:
                print(f"❌ Failed to geocode: {location}")
        
        if len(valid_locations) < 2:
            print("❌ Need at least 2 valid locations")
            return None
        
        # Get distance matrix
        print("🔄 Getting distance matrix...")
        matrix_data = self.api.get_matrix(coordinates, profile="driving")
        
        if not matrix_data or 'distances' not in matrix_data:
            print("❌ Failed to get distance matrix")
            return None
        
        # Extract distance matrix
        distances = matrix_data['distances']
        durations = matrix_data.get('durations', {})
        
        # Create distance lookup dictionary (convert meters to kilometers)
        distance_lookup = {}
        duration_lookup = {}
        
        for i, from_loc in enumerate(valid_locations):
            distance_lookup[from_loc] = {}
            duration_lookup[from_loc] = {}
            for j, to_loc in enumerate(valid_locations):
                if i < len(distances) and j < len(distances[i]):
                    # Convert meters to kilometers
                    distance_km = distances[i][j] / 1000 if distances[i][j] is not None else None
                    distance_lookup[from_loc][to_loc] = distance_km
                    if durations and i < len(durations) and j < len(durations[i]):
                        # Convert seconds to minutes
                        duration_min = durations[i][j] / 60 if durations[i][j] is not None else None
                        duration_lookup[from_loc][to_loc] = duration_min
        
        # Solve TSP
        print("🧮 Solving TSP...")
        best_route = self._solve_tsp_brute_force(
            valid_locations, 
            distance_lookup, 
            duration_lookup,
            start_location,
            end_location,
            return_to_start
        )
        
        if best_route:
            self._print_route_details(best_route, valid_locations)
            return best_route
        else:
            print("❌ No valid route found")
            return None
    
    def _solve_tsp_brute_force(self, 
                               locations: List[str], 
                               distance_lookup: Dict,
                               duration_lookup: Dict,
                               start_location: Optional[str] = None,
                               end_location: Optional[str] = None,
                               return_to_start: bool = True) -> Optional[Route]:
        """
        Solve TSP using brute force (for small numbers of locations).
        
        Args:
            locations: List of location names
            distance_lookup: Dictionary of distances between locations
            duration_lookup: Dictionary of durations between locations
            start_location: Optional starting location
            end_location: Optional ending location
            return_to_start: Whether to return to start
            
        Returns:
            Best route found
        """
        if len(locations) > 12:
            print("⚠️  Too many locations for brute force. Using nearest neighbor heuristic...")
            return self._solve_tsp_nearest_neighbor(
                locations, distance_lookup, duration_lookup, 
                start_location, end_location, return_to_start
            )
        
        best_route = None
        best_distance = float('inf')
        
        # Generate all possible permutations
        if start_location:
            # Fix start location
            remaining = [loc for loc in locations if loc != start_location]
            if end_location and end_location != start_location:
                remaining = [loc for loc in remaining if loc != end_location]
            
            if return_to_start:
                # Generate permutations of remaining locations
                for perm in itertools.permutations(remaining):
                    path = [start_location] + list(perm)
                    if end_location and end_location != start_location:
                        path.append(end_location)
                    if return_to_start:
                        path.append(start_location)
                    
                    route = self._evaluate_route(path, distance_lookup, duration_lookup)
                    if route and route.total_distance < best_distance:
                        best_distance = route.total_distance
                        best_route = route
            else:
                # Don't return to start
                for perm in itertools.permutations(remaining):
                    path = [start_location] + list(perm)
                    if end_location and end_location != start_location:
                        path.append(end_location)
                    
                    route = self._evaluate_route(path, distance_lookup, duration_lookup)
                    if route and route.total_distance < best_distance:
                        best_distance = route.total_distance
                        best_route = route
        else:
            # No fixed start location, try all permutations
            for perm in itertools.permutations(locations):
                path = list(perm)
                if return_to_start:
                    path.append(path[0])
                
                route = self._evaluate_route(path, distance_lookup, duration_lookup)
                if route and route.total_distance < best_distance:
                    best_distance = route.total_distance
                    best_route = route
        
        return best_route
    
    def _solve_tsp_nearest_neighbor(self, 
                                   locations: List[str], 
                                   distance_lookup: Dict,
                                   duration_lookup: Dict,
                                   start_location: Optional[str] = None,
                                   end_location: Optional[str] = None,
                                   return_to_start: bool = True) -> Optional[Route]:
        """
        Solve TSP using nearest neighbor heuristic (for larger numbers of locations).
        
        Args:
            locations: List of location names
            distance_lookup: Dictionary of distances between locations
            duration_lookup: Dictionary of durations between locations
            start_location: Optional starting location
            end_location: Optional ending location
            return_to_start: Whether to return to start
            
        Returns:
            Best route found using nearest neighbor
        """
        if start_location:
            current = start_location
            unvisited = [loc for loc in locations if loc != start_location]
            if end_location and end_location != start_location:
                unvisited = [loc for loc in unvisited if loc != end_location]
        else:
            current = locations[0]
            unvisited = locations[1:]
        
        path = [current]
        
        # Build path using nearest neighbor
        while unvisited:
            nearest = None
            min_distance = float('inf')
            
            for location in unvisited:
                distance = distance_lookup.get(current, {}).get(location)
                if distance is not None and distance < min_distance:
                    min_distance = distance
                    nearest = location
            
            if nearest is None:
                print("❌ Cannot find valid path")
                return None
            
            path.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # Add end location if specified
        if end_location and end_location != current:
            path.append(end_location)
        
        # Return to start if requested
        if return_to_start and path[0] != path[-1]:
            path.append(path[0])
        
        return self._evaluate_route(path, distance_lookup, duration_lookup)
    
    def _evaluate_route(self, 
                       path: List[str], 
                       distance_lookup: Dict,
                       duration_lookup: Dict) -> Optional[Route]:
        """
        Evaluate a route and calculate total distance and duration.
        
        Args:
            path: List of locations in order
            distance_lookup: Dictionary of distances
            duration_lookup: Dictionary of durations
            
        Returns:
            Route object with total metrics
        """
        if len(path) < 2:
            return None
        
        total_distance = 0
        total_duration = 0
        
        for i in range(len(path) - 1):
            from_loc = path[i]
            to_loc = path[i + 1]
            
            distance = distance_lookup.get(from_loc, {}).get(to_loc)
            duration = duration_lookup.get(from_loc, {}).get(to_loc)
            
            if distance is None:
                print(f"❌ No distance data for {from_loc} -> {to_loc}")
                return None
            
            total_distance += distance
            if duration is not None:
                total_duration += duration
        
        return Route(path=path, total_distance=total_distance, total_duration=total_duration)
    
    def _print_route_details(self, route: Route, locations: List[str]):
        """
        Print detailed information about the optimal route.
        
        Args:
            route: Route object with path and metrics
            locations: List of all locations
        """
        print("\n" + "="*60)
        print("🎯 OPTIMAL ROUTE FOUND")
        print("="*60)
        
        print(f"📍 Total Distance: {route.total_distance:.2f} km")
        print(f"⏱️  Total Duration: {route.total_duration:.1f} minutes")
        print(f"🚗 Number of Stops: {len(route.path) - 1}")
        
        print("\n🗺️  ROUTE PATH:")
        print("-" * 60)
        
        for i, location in enumerate(route.path):
            if i == 0:
                print(f"🚀 Start: {location}")
            elif i == len(route.path) - 1 and route.path[0] == route.path[-1]:
                print(f"🏁 End: {location} (return to start)")
            else:
                print(f"   {i}. {location}")
        
        print("\n📊 ROUTE STATISTICS:")
        print("-" * 60)
        print(f"Average Distance per Leg: {route.total_distance / (len(route.path) - 1):.2f} km")
        print(f"Average Duration per Leg: {route.total_duration / (len(route.path) - 1):.1f} minutes")
        
        if len(locations) > 2:
            print(f"Route Efficiency: {self._calculate_efficiency(route, locations):.1f}%")
    
    def _calculate_efficiency(self, route: Route, locations: List[str]) -> float:
        """
        Calculate route efficiency compared to straight-line distances.
        
        Args:
            route: Route object
            locations: List of all locations
            
        Returns:
            Efficiency percentage
        """
        # This is a simplified efficiency calculation
        # In a real implementation, you might compare to other metrics
        return 100.0  # Placeholder

def solve_shortest_path():
    """Main function to solve the shortest path through all cities."""
    
    # Hardcoded locations (same as in main function)
    locations = [
        "Boston, MA",
        "New York, NY",
        "Philadelphia, PA",
        "Baltimore, MD",
        "Washington, DC"
    ]
    
    print("🗺️ Traveling Salesman Problem Solver")
    print("="*50)
    print(f"📍 Finding shortest path through {len(locations)} cities:")
    for i, loc in enumerate(locations, 1):
        print(f"   {i}. {loc}")
    print()
    
    try:
        # Initialize API and solver
        api = MapboxMatrixAPI()
        solver = TSPSolver(api)
        
        # Solve TSP with different options
        print("🔍 Solving TSP with different constraints...")
        
        # Option 1: Start and end at Boston
        print("\n1️⃣  Route starting and ending at Boston:")
        route1 = solver.solve_tsp(
            locations=locations,
            start_location="Boston, MA",
            return_to_start=True
        )
        
        # Option 2: Start at Boston, end at Washington DC
        print("\n2️⃣  Route from Boston to Washington DC:")
        route2 = solver.solve_tsp(
            locations=locations,
            start_location="Boston, MA",
            end_location="Washington, DC",
            return_to_start=False
        )
        
        # Option 3: No fixed start/end (find best overall route)
        print("\n3️⃣  Best overall route (no fixed start/end):")
        route3 = solver.solve_tsp(
            locations=locations,
            return_to_start=True
        )
        
        # Compare results
        print("\n" + "="*60)
        print("📊 ROUTE COMPARISON")
        print("="*60)
        
        routes = [
            ("Boston → All Cities → Boston", route1),
            ("Boston → All Cities → Washington DC", route2),
            ("Best Overall Route", route3)
        ]
        
        for name, route in routes:
            if route:
                print(f"\n{name}:")
                print(f"   Distance: {route.total_distance:.2f} km")
                print(f"   Duration: {route.total_duration:.1f} minutes")
                print(f"   Path: {' → '.join(route.path)}")
            else:
                print(f"\n{name}: No valid route found")
        
        # Save best route to file
        best_route = min([r for _, r in routes if r is not None], 
                        key=lambda x: x.total_distance, default=None)
        
        if best_route:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"optimal_route_{timestamp}.json"
            
            route_data = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "total_locations": len(locations),
                    "locations": locations
                },
                "optimal_route": {
                    "path": best_route.path,
                    "total_distance_km": round(best_route.total_distance, 2),
                    "total_duration_minutes": round(best_route.total_duration, 1),
                    "stops": len(best_route.path) - 1
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(route_data, f, indent=2)
            
            print(f"\n💾 Best route saved to: {filename}")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 To fix this:")
        print("   1. Get a Mapbox access token from https://account.mapbox.com/")
        print("   2. Set it as environment variable: export MAPBOX_ACCESS_TOKEN='your_token_here'")
        print("   3. Or create a .env file with MAPBOX_ACCESS_TOKEN=your_token_here")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def solve_origin_destination_with_optional_stops():
    """Solve for best path from origin to destination with all combinations of optional stops."""
    
    # Hardcoded locations: first is origin, last is destination, rest are optional stops
    locations = [
        "Boston, MA",      # Origin (fixed)
        "New York, NY",    # Optional stop
        "Philadelphia, PA", # Optional stop
        "Baltimore, MD",   # Optional stop
        "Washington, DC"   # Destination (fixed)
    ]
    
    origin = locations[0]
    destination = locations[-1]
    optional_stops = locations[1:-1]
    
    print("🗺️ Origin-Destination with Optional Stops Solver")
    print("="*60)
    print(f"🚀 Origin: {origin}")
    print(f"🎯 Destination: {destination}")
    print(f"📍 Optional Stops ({len(optional_stops)}):")
    for i, stop in enumerate(optional_stops, 1):
        print(f"   {i}. {stop}")
    print()
    
    try:
        # Initialize API and solver
        api = MapboxMatrixAPI()
        solver = TSPSolver(api)
        
        # Generate all possible combinations of optional stops
        all_combinations = []
        for r in range(len(optional_stops) + 1):
            combinations = list(itertools.combinations(optional_stops, r))
            all_combinations.extend(combinations)
        
        print(f"🔍 Analyzing {len(all_combinations)} possible route combinations...")
        print("   (including direct route with no stops)")
        print()
        
        all_routes = []
        
        # Solve for each combination
        for i, combination in enumerate(all_combinations, 1):
            if len(combination) == 0:
                # Direct route from origin to destination
                route_locations = [origin, destination]
                route_name = f"Direct Route ({origin} → {destination})"
            else:
                # Route with optional stops
                route_locations = [origin] + list(combination) + [destination]
                stops_str = " → ".join(combination)
                route_name = f"Route with {len(combination)} stop(s):  {stops_str} "
            
            print(f"{i:2d}. {route_name}")
            
            # Solve TSP for this combination
            route = solver.solve_tsp(
                locations=route_locations,
                start_location=origin,
                end_location=destination,
                return_to_start=False
            )
            
            if route:
                all_routes.append((route_name, route, len(combination)))
                print(f"     ✅ Distance: {route.total_distance:.2f} km, Duration: {route.total_duration:.1f} min")
            else:
                print(f"     ❌ No valid route found")
        
        # Sort routes by duration
        all_routes.sort(key=lambda x: x[1].total_duration)
        
        # Find direct route for comparison
        direct_route = None
        for name, route, num_stops in all_routes:
            if num_stops == 0:
                direct_route = route
                break
        
        # Display results
        print("\n" + "="*60)
        print("📊 ROUTE RANKINGS (by duration)")
        print("="*60)
        
        for i, (name, route, num_stops) in enumerate(all_routes, 1):
            print(f"\n{i:2d}. {name}")
            print(f"    📍 Distance: {route.total_distance:.2f} km")
            print(f"    ⏱️  Duration: {route.total_duration:.1f} minutes")
            print(f"    🚏 Stops: {num_stops}")
            
            # Calculate extra distance and duration over direct route
            if direct_route and num_stops > 0:
                extra_distance = route.total_distance - direct_route.total_distance
                extra_duration = route.total_duration - direct_route.total_duration
                print(f"    📈 Extra Distance: +{extra_distance:.2f} km")
                print(f"    ⏰ Extra Duration: +{extra_duration:.1f} minutes")
            
            print(f"    🗺️  Path: {' → '.join(route.path)}")
        
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 To fix this:")
        print("   1. Get a Mapbox access token from https://account.mapbox.com/")
        print("   2. Set it as environment variable: export MAPBOX_ACCESS_TOKEN='your_token_here'")
        print("   3. Or create a .env file with MAPBOX_ACCESS_TOKEN=your_token_here")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def solve_origin_destination_with_optional_stops_streamlit(origin: str, destination: str, optional_stops: List[str]):
    """
    Solve for best path from origin to destination with all combinations of optional stops.
    Returns data for Streamlit app instead of printing.
    
    Args:
        origin: Starting location
        destination: Final destination
        optional_stops: List of optional stops to consider
        
    Returns:
        Dictionary containing route rankings and metadata
    """
    
    try:
        # Initialize API and solver
        api = MapboxMatrixAPI()
        solver = TSPSolver(api)
        
        # Generate all possible combinations of optional stops
        all_combinations = []
        for r in range(len(optional_stops) + 1):
            combinations = list(itertools.combinations(optional_stops, r))
            all_combinations.extend(combinations)
        
        all_routes = []
        
        # Solve for each combination
        for i, combination in enumerate(all_combinations, 1):
            if len(combination) == 0:
                # Direct route from origin to destination
                route_locations = [origin, destination]
                route_name = f"Direct Route ({origin} → {destination})"
            else:
                # Route with optional stops
                route_locations = [origin] + list(combination) + [destination]
                stops_str = " → ".join(combination)
                route_name = f"Route with {len(combination)} stop(s): {stops_str}"
            
            # Solve TSP for this combination
            route = solver.solve_tsp(
                locations=route_locations,
                start_location=origin,
                end_location=destination,
                return_to_start=False
            )
            
            if route:
                all_routes.append((route_name, route, len(combination)))
        
        # Sort routes by duration
        all_routes.sort(key=lambda x: x[1].total_duration)
        
        # Find direct route for comparison
        direct_route = None
        for name, route, num_stops in all_routes:
            if num_stops == 0:
                direct_route = route
                break
        
        # Prepare route rankings data
        route_rankings = []
        for i, (name, route, num_stops) in enumerate(all_routes, 1):
            route_data = {
                "rank": i,
                "name": name,
                "path": route.path,
                "total_distance_km": round(route.total_distance, 2),
                "total_duration_minutes": round(route.total_duration, 1),
                "num_stops": num_stops,
                "stops_included": route.path[1:-1] if len(route.path) > 2 else []
            }
            
            # Calculate extra distance and duration over direct route
            if direct_route and num_stops > 0:
                extra_distance = route.total_distance - direct_route.total_distance
                extra_duration = route.total_duration - direct_route.total_duration
                route_data["extra_distance_km"] = round(extra_distance, 2)
                route_data["extra_duration_minutes"] = round(extra_duration, 1)
            else:
                route_data["extra_distance_km"] = 0
                route_data["extra_duration_minutes"] = 0
            
            route_rankings.append(route_data)
        
        # Prepare summary statistics
        distances = [route.total_distance for _, route, _ in all_routes]
        durations = [route.total_duration for _, route, _ in all_routes]
        
        summary_stats = {
            "fastest_route": {
                "duration_minutes": round(all_routes[0][1].total_duration, 1),
                "distance_km": round(all_routes[0][1].total_distance, 2)
            },
            "slowest_route": {
                "duration_minutes": round(all_routes[-1][1].total_duration, 1),
                "distance_km": round(all_routes[-1][1].total_distance, 2)
            },
            "average_duration_minutes": round(sum(durations) / len(durations), 1),
            "average_distance_km": round(sum(distances) / len(distances), 2),
            "shortest_route_km": round(min(distances), 2),
            "longest_route_km": round(max(distances), 2)
        }
        
        if direct_route:
            summary_stats["direct_route"] = {
                "duration_minutes": round(direct_route.total_duration, 1),
                "distance_km": round(direct_route.total_distance, 2)
            }
            summary_stats["max_extra_time_minutes"] = round(max(durations) - direct_route.total_duration, 1)
            summary_stats["max_extra_distance_km"] = round(max(distances) - direct_route.total_distance, 2)
        
        return {
            "success": True,
            "route_rankings": route_rankings,
            "summary_stats": summary_stats,
            "total_combinations": len(all_combinations),
            "origin": origin,
            "destination": destination,
            "optional_stops": optional_stops
        }
        
    except ValueError as e:
        return {
            "success": False,
            "error": f"Configuration error: {e}",
            "suggestion": "Please check your Mapbox API key configuration."
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}",
            "suggestion": "Please try again or check your input data."
        }

def main():
    """Main function with hardcoded example locations."""
    
    # Hardcoded locations for demonstration
    locations = [
        "Boston, MA",
        "New York, NY",
        "Philadelphia, PA",
        "Baltimore, MD",
        "Washington, DC"
    ]
    
    print("🗺️ Mapbox Matrix API Query Script")
    print("="*50)
    print(f"📍 Querying {len(locations)} locations:")
    for i, loc in enumerate(locations, 1):
        print(f"   {i}. {loc}")
    print()
    
    try:
        # Initialize API client
        api = MapboxMatrixAPI()
        
        # Geocode all locations
        print("🔄 Geocoding locations...")
        coordinates = []
        valid_locations = []
        
        for location in locations:
            coords = api.geocode_location(location)
            if coords:
                coordinates.append(coords)
                valid_locations.append(location)
                print(f"✅ {location} -> ({coords[1]:.4f}, {coords[0]:.4f})")
            else:
                print(f"❌ Failed to geocode: {location}")
        
        if not coordinates:
            print("❌ No valid coordinates found. Exiting.")
            return
        
        print(f"\n✅ Successfully geocoded {len(coordinates)} locations")
        
        # Get matrix for driving profile
        print("\n🚗 Getting driving matrix...")
        matrix_data = api.get_matrix(
            coordinates=coordinates,
            profile="driving",
            annotations=['duration', 'distance']
        )
        
        if matrix_data:
            # Format and display results
            results = api.format_matrix_results(matrix_data, valid_locations)
            api.print_matrix_results(results)
            
            # Save results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"matrix_results_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n💾 Results saved to: {filename}")
            
        else:
            print("❌ Failed to get matrix data")
        
        # Add TSP solver results
        if matrix_data:
            print("\n" + "="*60)
            print("🎯 TRAVELING SALESMAN PROBLEM SOLVER")
            print("="*60)
            
            try:
                # Initialize TSP solver
                solver = TSPSolver(api)
                
                # Solve TSP with different options
                print("🔍 Finding optimal routes...")
                
                # Option 1: Start and end at first location
                print("\n1️⃣  Route starting and ending at first location:")
                route1 = solver.solve_tsp(
                    locations=valid_locations,
                    start_location=valid_locations[0],
                    return_to_start=True
                )
                
                # Option 2: Start at first location, end at last location
                if len(valid_locations) > 1:
                    print("\n2️⃣  Route from first to last location:")
                    route2 = solver.solve_tsp(
                        locations=valid_locations,
                        start_location=valid_locations[0],
                        end_location=valid_locations[-1],
                        return_to_start=False
                    )
                else:
                    route2 = None
                
                # Option 3: No fixed start/end (find best overall route)
                print("\n3️⃣  Best overall route (no fixed start/end):")
                route3 = solver.solve_tsp(
                    locations=valid_locations,
                    return_to_start=True
                )
                
                # Compare results
                print("\n" + "="*60)
                print("📊 OPTIMAL ROUTE COMPARISON")
                print("="*60)
                
                routes = []
                if route1:
                    routes.append(("Round Trip (Start → All → Start)", route1))
                if route2:
                    routes.append(("Point-to-Point (Start → All → End)", route2))
                if route3:
                    routes.append(("Best Overall Route", route3))
                
                if routes:
                    for name, route in routes:
                        print(f"\n{name}:")
                        print(f"   Distance: {route.total_distance:.2f} km")
                        print(f"   Duration: {route.total_duration:.1f} minutes")
                        print(f"   Path: {' → '.join(route.path)}")
                    
                    # Save best route to file
                    best_route = min(routes, key=lambda x: x[1].total_distance)[1]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"optimal_route_{timestamp}.json"
                    
                    route_data = {
                        "metadata": {
                            "timestamp": datetime.now().isoformat(),
                            "total_locations": len(valid_locations),
                            "locations": valid_locations
                        },
                        "optimal_route": {
                            "path": best_route.path,
                            "total_distance_km": round(best_route.total_distance, 2),
                            "total_duration_minutes": round(best_route.total_duration, 1),
                            "stops": len(best_route.path) - 1
                        },
                        "all_routes": {
                            name: {
                                "path": route.path,
                                "total_distance_km": round(route.total_distance, 2),
                                "total_duration_minutes": round(route.total_duration, 1),
                                "stops": len(route.path) - 1
                            } for name, route in routes
                        }
                    }
                    
                    with open(filename, 'w') as f:
                        json.dump(route_data, f, indent=2)
                    
                    print(f"\n💾 Best route saved to: {filename}")
                else:
                    print("❌ No valid routes found")
                    
            except Exception as e:
                print(f"❌ Error in TSP solver: {e}")
            
            # Add Origin-Destination with Optional Stops analysis
            if len(valid_locations) >= 3:
                print("\n" + "="*60)
                print("🎯 ORIGIN-DESTINATION WITH OPTIONAL STOPS")
                print("="*60)
                
                origin = valid_locations[0]
                destination = valid_locations[-1]
                optional_stops = valid_locations[1:-1]
                
                print(f"🚀 Origin: {origin}")
                print(f"🎯 Destination: {destination}")
                print(f"📍 Optional Stops: {', '.join(optional_stops)}")
                
                # Generate all possible combinations of optional stops
                all_combinations = []
                for r in range(len(optional_stops) + 1):
                    combinations = list(itertools.combinations(optional_stops, r))
                    all_combinations.extend(combinations)
                
                print(f"\n🔍 Quick analysis of {len(all_combinations)} route combinations...")
                
                # Quick analysis of best routes by number of stops
                best_by_stops = {}
                
                for combination in all_combinations:
                    if len(combination) == 0:
                        route_locations = [origin, destination]
                        num_stops = 0
                    else:
                        route_locations = [origin] + list(combination) + [destination]
                        num_stops = len(combination)
                    
                    route = solver.solve_tsp(
                        locations=route_locations,
                        start_location=origin,
                        end_location=destination,
                        return_to_start=False
                    )
                    
                    if route:
                        if num_stops not in best_by_stops or route.total_distance < best_by_stops[num_stops][1].total_distance:
                            best_by_stops[num_stops] = (f"{num_stops} stop(s)", route)
                
                print("\n🏆 BEST ROUTES BY NUMBER OF STOPS:")
                for num_stops in sorted(best_by_stops.keys()):
                    name, route = best_by_stops[num_stops]
                    print(f"   {num_stops} stop(s): {route.total_distance:.2f} km, {route.total_duration:.1f} min")
                
                print(f"\n💡 Run 'python run_origin_destination.py' for detailed analysis of all {len(all_combinations)} routes")
    
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 To fix this:")
        print("   1. Get a Mapbox access token from https://account.mapbox.com/")
        print("   2. Set it as environment variable: export MAPBOX_ACCESS_TOKEN='your_token_here'")
        print("   3. Or pass it directly to MapboxMatrixAPI(access_token='your_token_here')")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 