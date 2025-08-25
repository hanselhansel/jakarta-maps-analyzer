# Community Locations Extraction for Jakarta

This documentation covers the community-centered locations extraction system that adds community infrastructure and services data to the existing pet market dataset **without touching any existing competitor data**.

## 🎯 Purpose

Extract community-centered locations from Google Maps to enhance market analysis by understanding the local community infrastructure around pet wellness businesses in Jakarta.

## 📋 What Gets Extracted

### Community Categories:

1. **Community_Infrastructure**
   - posyandu (community health posts)
   - balai RT/RW (neighborhood halls)
   - pasar tradisional (traditional markets)
   - warung kopi (local coffee shops)
   - masjid, gereja, vihara, pura (religious places)

2. **Middle_Class_Accessibility**
   - Indomaret, Alfamart (convenience stores)
   - bank lokal (local banks: BRI, BNI, Mandiri)
   - halte bus/transjakarta (bus stops)
   - puskesmas (public health centers)

3. **Family_Services**
   - SD negeri (public elementary schools)
   - TK, PAUD (kindergarten, early childhood education)
   - taman bermain (playgrounds)
   - apotek (pharmacies)

4. **Value_Conscious_Retail**
   - rumah makan padang (Padang restaurants)
   - warung makan, warteg (local eateries)
   - laundry services
   - toko kelontong (grocery stores)

## 🔧 Scripts Overview

### 1. `community_extractor.py`
Main extraction script that searches for community locations using Indonesian language settings.

**Key Features:**
- Uses Indonesian language (`language='id'`) for better local results
- Applies appropriate radius (500-1500m) based on category
- Implements deduplication against existing dataset
- Outputs exact 21-column format matching existing data
- Conservative rate limiting (8 requests/second)

### 2. `merge_community_data.py`
Safely merges community data with existing pet market dataset.

**Key Features:**
- Preserves all existing competitor data
- Validates data integrity before and after merge
- Handles any unexpected overlaps
- Generates summary reports
- Creates timestamped merged datasets

### 3. `test_community_extractor.py`
Validation script to test setup before running full extraction.

**Tests:**
- Google Maps API key validation
- Required file dependencies
- Data loading functionality
- Limited extraction test

## 📁 Required Files

Before running, ensure these files exist:
- `existing_zones_info.csv` - Zone coordinates (28 zones)
- `jakarta_pet_market_CLEAN_20250805_102308.csv` - Existing dataset (2,350 records)
- `.env` file with `GOOGLE_MAPS_API_KEY=your_api_key_here`

## 🚀 Usage Instructions

### Step 1: Validate Setup
```bash
python test_community_extractor.py
```
This will verify all dependencies and run basic tests.

### Step 2: Run Community Extraction
```bash
python community_extractor.py
```
This will:
- Search all 28 zones for community locations
- Use Indonesian language settings
- Apply category-specific search radiuses
- Avoid duplicating existing data
- Generate timestamped output file: `jakarta_community_locations_YYYYMMDD_HHMMSS.csv`

### Step 3: Merge with Existing Data
```bash
python merge_community_data.py jakarta_community_locations_20250805_123456.csv
```
Or let it auto-detect the most recent community file:
```bash
python merge_community_data.py
```

## 📊 Output Format

All outputs maintain the exact 21-column structure:
```
place_id,name,category,sub_category,latitude,longitude,address,vicinity,rating,review_count,website,phone,price_level,types,is_operational,search_zone,search_keyword,is_open_now,timestamp,popularity_score,buffer_radius_m
```

## 💰 Estimated Costs

Based on Google Maps Platform pricing (2024):
- **Nearby Search:** $0.032 per call
- **Place Details:** $0.017 per call
- **Estimated total:** $15-25 for full Jakarta extraction (depending on results found)

## 🛡️ Safety Features

### Data Protection:
- **No existing data modification:** Community extraction is completely separate
- **Deduplication:** Automatically avoids extracting places already in dataset
- **Validation:** Multiple validation steps ensure data integrity

### API Safety:
- **Rate limiting:** Conservative 8 requests/second
- **Error handling:** Graceful handling of API errors and timeouts
- **Progress tracking:** Real-time progress with detailed logging

## 📈 Expected Results

Based on Jakarta's urban density and the 28 search zones:
- **Estimated community locations:** 1,500 - 3,000 places
- **Processing time:** 2-4 hours (depending on API response times)
- **Coverage:** Comprehensive across all Jakarta zones

## 🔍 Key Differences from Pet Market Extraction

| Aspect | Pet Market Extraction | Community Extraction |
|--------|----------------------|---------------------|
| **Language** | English | Indonesian (`language='id'`) |
| **Focus** | Pet businesses & affluence proxies | Community infrastructure |
| **Keywords** | Pet-related terms | Indonesian community terms |
| **Radius** | Fixed 50km | Variable 500-1500m by category |
| **Rate Limit** | 10 req/sec | 8 req/sec (more conservative) |

## 📋 Troubleshooting

### Common Issues:

1. **"No community locations file found"**
   - Run `community_extractor.py` first to generate community data

2. **"API key validation failed"**
   - Check `.env` file has correct `GOOGLE_MAPS_API_KEY`
   - Verify API key has Places API enabled

3. **"Missing required files"**
   - Ensure `existing_zones_info.csv` and existing dataset are present

4. **"Low results returned"**
   - Normal for some categories (e.g., posyandu are less common)
   - Indonesian language setting may return different results than English

### Performance Tips:

- Run during off-peak hours to minimize API latency
- Monitor API quotas in Google Cloud Console
- Use `test_community_extractor.py` first to verify setup

## 📞 Support

For issues with:
- **Google Maps API:** Check Google Cloud Console quotas and billing
- **Script errors:** Review log outputs for detailed error messages
- **Data validation:** Use merge script's validation reports

## 🎯 Next Steps After Extraction

1. **Quality Review:** Manually review a sample of extracted locations
2. **Data Analysis:** Use merged dataset for comprehensive market analysis
3. **Visualization:** Import merged data into QGIS for spatial analysis
4. **Business Intelligence:** Analyze community density around pet businesses

---

*This extraction system is designed to safely enhance the existing pet market dataset with valuable community context data while maintaining full data integrity.*