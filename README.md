# 🗺️ Travel Route Planner

A comprehensive Streamlit application for planning travel routes with multiple stops, featuring origin/destination input, up to 10 stops with mandatory/optional labeling, interactive maps, and export functionality.

## ✨ Features

- **Route Planning**: Set origin and destination points
- **Multiple Stops**: Add up to 10 stops along your route
- **Stop Classification**: Label stops as "Mandatory" or "Optional"
- **TSP Route Analysis**: Calculate optimal routes with optional stops using Traveling Salesman Problem solver
- **Route Rankings**: View routes ranked by duration with extra time/distance metrics
- **Interactive Map**: Visualize your route with markers for all points
- **Route Summary**: View detailed route information and statistics
- **Export Options**: Download routes as JSON or CSV files
- **Save/Load**: Save and load route configurations
- **Responsive Design**: Beautiful, modern UI with custom styling

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Mapbox API key (for TSP route analysis)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd travel-route-planner
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Mapbox API key** (for TSP analysis):
   ```bash
   # Option 1: Environment variable
   export MAPBOX_ACCESS_TOKEN='your_mapbox_token_here'
   
   # Option 2: Create .env file
   echo "MAPBOX_ACCESS_TOKEN=your_mapbox_token_here" > .env
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** and navigate to `http://localhost:8501`

## 📖 How to Use

### 1. Route Planning Page

- **Set Origin**: Enter your starting point (e.g., "New York, NY")
- **Set Destination**: Enter your final destination (e.g., "Los Angeles, CA")
- **Add Stops**: Use the "Add New Stop" expander to add up to 10 stops
- **Stop Types**: Choose between "Mandatory" (must-visit) or "Optional" (nice-to-have)
- **Manage Stops**: Remove individual stops or clear all stops
- **TSP Analysis**: Click "Calculate Times to Add Stops" to analyze optimal routes with optional stops

### 2. Route Summary Page

- **Overview**: See key metrics including origin, destination, and stop counts
- **Detailed Route**: View a table with all stops in order
- **Export**: Download your route as JSON or CSV files

### 3. Map View Page

- **Interactive Map**: Visualize your entire route on an interactive map
- **Markers**: 
  - 🟢 Green play icon: Origin
  - 🔴 Red flag icon: Destination
  - 🟠 Orange info icon: Mandatory stops
  - 🔵 Blue info icon: Optional stops
- **Popups**: Click markers to see location details

### 4. TSP Route Analysis

- **Calculate Optimal Routes**: Click "Calculate Times to Add Stops" button
- **Route Rankings**: View all possible route combinations ranked by duration
- **Extra Metrics**: See additional time and distance compared to direct route
- **Summary Statistics**: Get overview of fastest, slowest, and average routes
- **Export Results**: Download analysis as JSON or CSV files

## 🛠️ Technical Details

### Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **folium**: Interactive maps
- **streamlit-folium**: Streamlit integration for folium maps
- **geopy**: Geocoding and distance calculations
- **requests**: HTTP library for API calls
- **python-dotenv**: Environment variable management

### Architecture

- **Session State Management**: Persistent data across page navigation
- **Modular Design**: Separate functions for each page/feature
- **Error Handling**: Graceful handling of geocoding failures
- **Responsive Layout**: Column-based layout for better UX

### File Structure

```
travel-route-planner/
├── app.py                          # Main Streamlit application
├── mapbox_matrix.py                # TSP solver and Mapbox API integration
├── requirements.txt                # Python dependencies
├── test_streamlit_tsp.py          # Test script for TSP integration
├── README.md                      # Documentation
└── .gitignore                     # Git ignore file
```

## 🎨 Customization

### Styling

The app uses custom CSS for styling. You can modify the styles in the `st.markdown()` section at the top of `app.py`:

- **Color Scheme**: Change colors for headers, cards, and badges
- **Layout**: Adjust spacing, padding, and border styles
- **Typography**: Modify font sizes and weights

### Adding Features

The modular design makes it easy to add new features:

1. **New Pages**: Add new page options to the sidebar radio button
2. **Additional Stop Types**: Extend the stop type selection
3. **More Export Formats**: Add new export functions
4. **Route Optimization**: Integrate with routing APIs for optimal paths

## 🔧 Troubleshooting

### Common Issues

1. **Map not loading**: Check internet connection (required for geocoding)
2. **Geocoding errors**: Ensure location names are specific and valid
3. **Dependency issues**: Make sure all packages are installed correctly

### Performance Tips

- Use specific location names for better geocoding accuracy
- Limit stops to essential locations for faster processing
- Clear browser cache if experiencing display issues

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions, please open an issue on the repository.

---

**Happy Travel Planning!** 🗺️✈️