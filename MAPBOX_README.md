# 🗺️ Mapbox Matrix API Script

A Python script to query the Mapbox Matrix API for travel times and distances between multiple locations. This script provides a comprehensive interface to get matrix data for route planning and optimization.

## ✨ Features

- **Matrix API Integration**: Get travel times and distances between all pairs of locations
- **Geocoding**: Convert location names to coordinates automatically
- **Multiple Travel Profiles**: Support for driving, walking, cycling, and driving-traffic
- **Custom Annotations**: Request duration, distance, and speed data
- **Formatted Output**: Human-readable matrix display with summary statistics
- **Error Handling**: Robust error handling and validation
- **JSON Export**: Save results to JSON files for further analysis

## 🚀 Quick Start

### Prerequisites

1. **Mapbox Account**: Sign up at [Mapbox](https://account.mapbox.com/)
2. **Access Token**: Get your access token from the Mapbox dashboard
3. **Python Dependencies**: Install required packages

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r mapbox_requirements.txt
   ```

2. **Set your Mapbox access token**:
   ```bash
   export MAPBOX_ACCESS_TOKEN='your_mapbox_token_here'
   ```

3. **Run the script**:
   ```bash
   python mapbox_matrix.py
   ```

## 📖 Usage

### Basic Usage

```python
from mapbox_matrix import MapboxMatrixAPI

# Initialize API client
api = MapboxMatrixAPI()

# Define locations
locations = ["New York, NY", "Boston, MA", "Philadelphia, PA"]

# Geocode locations
coordinates = []
for location in locations:
    coords = api.geocode_location(location)
    if coords:
        coordinates.append(coords)

# Get matrix data
matrix_data = api.get_matrix(coordinates, profile="driving")

# Format and display results
results = api.format_matrix_results(matrix_data, locations)
api.print_matrix_results(results)
```

### Travel Profiles

The script supports multiple travel profiles:

- **`driving`**: Car travel (default)
- **`walking`**: Pedestrian routes
- **`cycling`**: Bicycle routes
- **`driving-traffic`**: Car travel with real-time traffic

```python
# Get matrix for different profiles
profiles = ["driving", "walking", "cycling"]
for profile in profiles:
    matrix_data = api.get_matrix(coordinates, profile=profile)
    # Process results...
```

### Custom Annotations

Request specific data types:

```python
# Get duration and distance
matrix_data = api.get_matrix(
    coordinates=coordinates,
    annotations=['duration', 'distance']
)

# Get duration, distance, and speed
matrix_data = api.get_matrix(
    coordinates=coordinates,
    annotations=['duration', 'distance', 'speed']
)
```

### Direct Coordinates

Use coordinates directly instead of geocoding:

```python
# Coordinates as (longitude, latitude) tuples
coordinates = [
    (-74.006, 40.7128),  # New York
    (-71.0589, 42.3601), # Boston
    (-75.1652, 39.9526)  # Philadelphia
]

matrix_data = api.get_matrix(coordinates, profile="driving")
```

## 📊 Output Format

The script provides formatted output including:

### Matrix Display
- **Travel Times Matrix**: Duration between all location pairs (in minutes)
- **Distance Matrix**: Distance between all location pairs (in kilometers)
- **Summary Statistics**: Average duration, average distance, total pairs

### JSON Export
Results are automatically saved to timestamped JSON files:

```json
{
  "metadata": {
    "locations": ["New York, NY", "Boston, MA"],
    "profile": "driving",
    "timestamp": "2024-01-15T10:30:00"
  },
  "durations": {
    "New York, NY": {
      "New York, NY": null,
      "Boston, MA": 240.5
    },
    "Boston, MA": {
      "New York, NY": 245.2,
      "Boston, MA": null
    }
  },
  "distances": {
    "New York, NY": {
      "New York, NY": null,
      "Boston, MA": 308.5
    },
    "Boston, MA": {
      "New York, NY": 308.5,
      "Boston, MA": null
    }
  },
  "summary": {
    "average_duration_minutes": 242.9,
    "average_distance_km": 308.5,
    "total_pairs": 2
  }
}
```

## 🔧 Configuration

### Environment Variables

- **`MAPBOX_ACCESS_TOKEN`**: Your Mapbox access token (required)

### API Limits

- **Maximum coordinates**: 25 per request
- **Rate limits**: Vary by account type (check Mapbox documentation)
- **Geocoding limits**: 100 requests per minute (free tier)

## 📁 Files

- **`mapbox_matrix.py`**: Main script with MapboxMatrixAPI class
- **`mapbox_example.py`**: Example usage and demonstrations
- **`mapbox_requirements.txt`**: Python dependencies
- **`MAPBOX_README.md`**: This documentation

## 🛠️ Examples

### Example 1: Basic Matrix Query
```bash
python mapbox_matrix.py
```

### Example 2: Run Examples
```bash
python mapbox_example.py
```

### Example 3: Custom Locations
Edit the `locations` list in `mapbox_matrix.py` to use your own locations.

## 🔍 Troubleshooting

### Common Issues

1. **"Mapbox access token is required"**
   - Set the `MAPBOX_ACCESS_TOKEN` environment variable
   - Or pass the token directly to the constructor

2. **"Could not geocode: [location]"**
   - Check the location name spelling
   - Try more specific location names
   - Verify the location exists

3. **"Maximum 25 coordinates allowed"**
   - Reduce the number of locations
   - Split into multiple requests

4. **API rate limiting**
   - Wait between requests
   - Upgrade your Mapbox account

### Error Handling

The script includes comprehensive error handling:

- **Configuration errors**: Clear messages about missing tokens
- **Geocoding errors**: Graceful handling of failed geocoding
- **API errors**: Detailed error messages with response content
- **Validation**: Input validation for coordinates and parameters

## 🔗 Integration with Travel Route Planner

This script can be integrated with the Streamlit Travel Route Planner:

1. **Add Matrix Data**: Use matrix results to show travel times between stops
2. **Route Optimization**: Use matrix data for optimal route calculation
3. **Real-time Updates**: Get current traffic conditions
4. **Export Integration**: Include matrix data in route exports

## 📝 License

This script is part of the Travel Route Planner project and follows the same license terms.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit improvements, bug fixes, or new features.

---

**Happy Routing!** 🗺️🚗 