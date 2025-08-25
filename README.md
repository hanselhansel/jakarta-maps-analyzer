# Jakarta Maps Analyzer

## 🎯 Overview

AI-powered pet market analysis for Jakarta using Google Maps Platform. This tool performs comprehensive location intelligence analysis to identify pet-related businesses, community infrastructure, and market opportunities across Jakarta.

**Part of the Mapping AI Organization** - Professional location intelligence tools for Southeast Asia.

## 🌟 Features

- **Comprehensive Market Analysis**: Identifies pet stores, veterinary clinics, grooming services
- **Community Infrastructure Mapping**: Schools, hospitals, community centers, religious facilities
- **Grid-Based Search Strategy**: Complete coverage with optimized API usage
- **Smart Data Processing**: Deduplication, validation, and enrichment
- **Multiple Analysis Modes**: Simple, comprehensive, and community-focused
- **Export Capabilities**: CSV, JSON, and QGIS-compatible formats

## 📁 Project Structure

```
jakarta-maps-analyzer/
├── src/                      # Source code
│   ├── analyzers/           # Core analysis modules
│   │   ├── analyze_existing_data.py
│   │   ├── community_extractor.py
│   │   ├── coverage_analysis.py
│   │   └── merge_datasets.py
│   ├── runners/             # Execution scripts
│   │   ├── main.py
│   │   ├── main_comprehensive.py
│   │   ├── main_simple.py
│   │   └── run_*.py
│   └── utils/               # Utility functions
│       ├── test_api_key.py
│       ├── debug_api.py
│       └── verify_*.py
├── data/                    # Data directory
│   ├── raw/                # Input data files
│   ├── processed/          # Processed datasets
│   ├── analysis/           # Analysis results
│   └── exports/            # Final outputs
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test data
├── scripts/                 # Standalone scripts
│   ├── run_analysis.py     # Main entry point
│   ├── quick_analysis.py
│   └── demo_analysis.py
├── docs/                    # Documentation
├── logs/                    # Application logs
└── reports/                 # Generated reports
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Maps API key with the following APIs enabled:
  - Places API
  - Geocoding API
  - Maps JavaScript API (optional, for visualization)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/hanselhansel/jakarta-maps-analyzer.git
cd jakarta-maps-analyzer
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your Google Maps API key
```

### Running the Analysis

**Basic analysis:**
```bash
python scripts/run_analysis.py
```

**Comprehensive grid search:**
```bash
python src/runners/main_comprehensive.py
```

**Community infrastructure analysis:**
```bash
python src/analyzers/community_extractor.py
```

**Quick test with sample data:**
```bash
python scripts/quick_analysis.py
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Required
GOOGLE_MAPS_API_KEY=your_api_key_here

# Optional - Analysis Parameters
SEARCH_RADIUS=5000          # Search radius in meters
RATE_LIMIT=10              # API requests per second
MAX_RESULTS=60             # Max results per location

# Optional - Grid Search
GRID_SIZE=0.005            # Grid size in decimal degrees
OVERLAP_FACTOR=1.5         # Overlap between search areas
```

### Search Configuration

Modify `data/raw/queries.csv` to customize search terms:
```csv
query,category
pet shop,retail
veterinary clinic,medical
pet grooming,service
```

Modify `data/raw/search_zones.csv` to define search areas:
```csv
zone_name,lat,lng,radius
Central Jakarta,-6.1862,106.8229,5000
South Jakarta,-6.2615,106.8106,5000
```

## 📊 Data Processing Pipeline

1. **Data Collection**
   - Grid-based search strategy for complete coverage
   - Automatic retry logic for failed requests
   - Rate limiting to respect API quotas

2. **Data Cleaning**
   - Duplicate detection and removal
   - Address standardization
   - Missing data imputation

3. **Analysis**
   - Competition density analysis
   - Market opportunity identification
   - Community infrastructure assessment

4. **Export**
   - Multiple format support (CSV, JSON)
   - QGIS-compatible exports
   - Comprehensive reporting

## 🧪 Testing

Run the test suite:
```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=src tests/
```

Verify API setup:
```bash
python src/utils/test_api_key.py
```

## 📈 Output Files

The analysis generates several output files:

- `data/processed/jakarta_pet_market_COMPLETE_[timestamp].csv` - Full dataset
- `data/processed/jakarta_pet_market_CLEAN_[timestamp].csv` - Cleaned data
- `data/analysis/market_analysis_[timestamp].json` - Analysis results
- `reports/market_report_[timestamp].pdf` - Generated report (if enabled)

### Output Schema

```csv
name,address,lat,lng,rating,user_ratings_total,types,place_id,website,phone,opening_hours
Pet Store Jakarta,"Jl. Example No. 1",-6.2088,106.8456,4.5,234,["pet_store","store"],...
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Follow the project structure and coding standards
4. Write tests for new functionality
5. Update documentation
6. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
7. Push to the branch (`git push origin feature/AmazingFeature`)
8. Open a Pull Request

## 📝 Development

### Code Style

We use Black for code formatting and isort for import sorting:
```bash
black src/
isort src/
```

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Verify API key is correctly set in `.env`
   - Check that required APIs are enabled in Google Cloud Console
   - Run `python src/utils/test_api_key.py` to diagnose

2. **Rate Limiting**
   - Adjust `RATE_LIMIT` in `.env`
   - Enable automatic retry logic
   - Consider using batch processing

3. **Memory Issues with Large Datasets**
   - Process data in chunks
   - Use `data/processed/` for intermediate results
   - Increase system swap space if needed

## 📊 Performance Metrics

- Average processing time: ~2-3 hours for full Jakarta analysis
- API calls required: ~10,000-15,000 for comprehensive coverage
- Data points collected: 5,000+ unique locations
- Coverage area: 600+ km² of Jakarta

## 🔒 Security

- Never commit API keys or `.env` files
- Use environment variables for sensitive data
- Regularly rotate API keys
- Monitor API usage in Google Cloud Console

## 📄 License

This project is proprietary software owned by Hansel Wahjono.

## 🔗 Links

- **Organization**: [Mapping AI](https://github.com/hanselhansel/mapping-ai)
- **Author**: Hansel Wahjono
- **Email**: hansel.wahjono@gmail.com

## 🙏 Acknowledgments

- Google Maps Platform for location data
- The Mapping AI organization for standardized templates
- Based on the toko-cat-bengkulu project structure

---

*Part of the Mapping AI Organization - Professional location intelligence tools for Southeast Asia*