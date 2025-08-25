# Google Maps Market Analysis Scraper

This project uses the official Google Maps Platform API to collect data on points of interest for market analysis.

## Prerequisites

Before using this tool, you must:

1. **Create a Google Cloud Project:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (e.g., "Jakarta Market Analysis")

2. **Enable the Places API:**
   - In your project's dashboard, go to "APIs & Services" > "Library"
   - Search for **"Places API"** and click **Enable**

3. **Create and Secure an API Key:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - **Important:** Click on the new API key to edit it
   - Under "API restrictions," select "Restrict key" and choose "Places API"

4. **Set Up Billing:**
   - Link a credit card to your project (API is pay-as-you-go)
   - **Recommended:** Set up budget alerts to prevent unexpected charges

## Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key:**
   Open the `config.ini` file and replace `YOUR_API_KEY_HERE` with your actual Google Maps API key.

3. **Define Your Searches:**
   Edit the `queries.csv` file to add or remove the keywords and categories you want to search for.

## Running the Script

Execute the main script from your terminal:
```bash
python main.py
```

The script will:
- Display progress as it processes each search query
- Show a cost estimation upon completion
- Save results to `jakarta_market_analysis_output.csv`

## Configuration Options

### config.ini
- `api_key`: Your Google Maps Platform API key
- `latitude` & `longitude`: Center point for searches (default: Central Jakarta)
- `radius`: Search radius in meters (default: 50000m = 50km)

### queries.csv
- `keyword`: The search term to use
- `category`: A category label for grouping results

## Output Format

The output CSV file contains the following columns:
- `place_id`: Unique identifier for the place
- `name`: Business/location name
- `category`: Category from your queries.csv
- `address`: Full formatted address
- `latitude` & `longitude`: GPS coordinates
- `rating`: Average rating (if available)
- `review_count`: Number of reviews
- `website`: Website URL (if available)
- `types`: Google's categorization of the place
- `is_open_now`: Current open status (if available)

## Cost Management

The script provides real-time cost estimation based on:
- Text Search: ~$0.032 per call
- Place Details: ~$0.017 per call

**Note:** Actual pricing may vary. Always check current [Google Maps Platform pricing](https://developers.google.com/maps/billing/gmp-billing).

## Troubleshooting

- **"YOUR_API_KEY_HERE" error**: You need to edit config.ini with your actual API key
- **API errors**: Check that the Places API is enabled in your Google Cloud project
- **Billing errors**: Ensure billing is set up for your Google Cloud project
- **No results**: Try adjusting the search radius or keywords

## Security Best Practices

### API Key Security
- **NEVER commit real API keys to version control**
- Use environment variables (recommended) or `.env` file for API keys
- Copy `.env.example` to `.env` and add your actual API key
- The script prioritizes environment variables over config.ini for security
- Restrict your API key to only the Places API in Google Cloud Console
- Set up billing alerts to prevent unexpected charges
- Monitor API usage regularly

### Additional Security Features
- Input validation and sanitization for all user inputs
- Rate limiting to prevent API quota exhaustion
- Comprehensive error handling and logging
- Secure filename generation with timestamps
- API key format validation
- Coordinate and parameter validation

### Production Deployment
```bash
# Set environment variables (recommended)
export GOOGLE_MAPS_API_KEY="your_actual_api_key_here"
export SEARCH_LATITUDE="-6.2088"
export SEARCH_LONGITUDE="106.8456"
export SEARCH_RADIUS="50000"
export API_RATE_LIMIT="10"

# Or use .env file
cp .env.example .env
# Edit .env with your actual values
```

### File Security
- `config.ini`, `.env`, and output CSV files are in `.gitignore`
- Never share configuration files containing real API keys
- Use secure file permissions in production environments