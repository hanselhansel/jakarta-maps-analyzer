# Google Maps API Security Setup Guide

## 🔒 CRITICAL SECURITY WARNING

**NEVER share your API key in plain text or commit it to version control!**

If you have exposed your API key anywhere, you should:

1. **Regenerate this API key immediately** in the Google Cloud Console since it was exposed
2. **Review your Google Cloud Console** for any unauthorized usage
3. **Set up billing alerts** to monitor unexpected charges

## ✅ What We've Set Up

### 1. Environment Variables (.env file)
Your API key is now stored in `/Users/hansel/Library/CloudStorage/GoogleDrive-hansel.wahjono@gmail.com/Other computers/My MacBook Air 2024/Documents/mapping-ai/jakarta-maps-analyzer/.env`:

```env
GOOGLE_MAPS_API_KEY=your_actual_api_key_here
SEARCH_LATITUDE=-6.2088
SEARCH_LONGITUDE=106.8456
SEARCH_RADIUS=50000
API_RATE_LIMIT=10
```

### 2. Version Control Protection
The `.gitignore` file already includes:
- `.env` files
- `config.ini` files
- All output files (*.csv, *.json, *.xlsx)

### 3. Secure Code Implementation
The `main.py` already implements security best practices:
- Input validation and sanitization
- Rate limiting to prevent API abuse
- Proper error handling
- No hardcoded secrets

## 🚨 Current Issue: API Authorization

Your API key test revealed: `REQUEST_DENIED (This API project is not authorized to use this API.)`

## 🛠️ Required Google Cloud Setup

### Step 1: Enable Required APIs
In the Google Cloud Console, enable these APIs:
1. **Places API**
2. **Geocoding API** 
3. **Maps JavaScript API** (if using web interface)

### Step 2: Configure API Key Restrictions
For maximum security, restrict your API key:

1. **Application restrictions:**
   - Choose "IP addresses" 
   - Add your server/development machine IP

2. **API restrictions:**
   - Select "Restrict key"
   - Choose only the APIs you need:
     - Places API
     - Geocoding API

### Step 3: Set Up Billing
1. Enable billing on your Google Cloud project
2. Set up billing alerts for unexpected usage
3. Set daily quotas to limit costs

### Step 4: Regenerate Your API Key
Since the key was exposed, create a new one:
1. Go to Google Cloud Console → APIs & Services → Credentials
2. Delete the exposed key
3. Create a new API key
4. Apply restrictions immediately
5. Update your `.env` file with the new key

## 🧪 Testing Your Setup

Run the test script to verify everything works:

```bash
cd jakarta-maps-analyzer
python3 test_api_key.py
```

If successful, you'll see:
```
✓ Geocoding test passed - Jakarta coordinates: -6.2088, 106.8456
✓ Places search test passed - Found X restaurants
🎉 API key test completed successfully!
```

## 🔐 Additional Security Measures

### 1. Environment-Specific Keys
Consider using different API keys for:
- Development
- Testing  
- Production

### 2. Monitoring and Alerts
- Set up Google Cloud monitoring
- Enable API usage alerts
- Monitor for unusual traffic patterns

### 3. Code Security
The existing code already implements:
- ✅ Input sanitization
- ✅ Parameter validation
- ✅ Rate limiting
- ✅ Error handling
- ✅ No SQL injection risks
- ✅ Secure file handling

### 4. Regular Security Audits
- Review API usage monthly
- Rotate API keys quarterly
- Update dependencies regularly
- Monitor security advisories

## 🚀 Running the Application

Once your API key is properly configured:

```bash
# Test the API key
python3 test_api_key.py

# Run the main scraper
python3 main.py
```

## 📊 Cost Monitoring

The application includes cost estimation:
- Text Search API: $0.032 per request
- Place Details API: $0.017 per request

Set conservative quotas initially to avoid unexpected charges.

## 🆘 If Something Goes Wrong

1. **Unexpected charges:** Check Google Cloud billing dashboard
2. **API errors:** Verify API is enabled and key has correct permissions
3. **Rate limiting:** Adjust `API_RATE_LIMIT` in `.env` file
4. **Authentication issues:** Regenerate API key and check restrictions

## 📞 Support

If you need help:
1. Check Google Cloud Console error logs
2. Review Google Maps Platform documentation
3. Ensure billing is enabled and quotas are set appropriately

Remember: **Security first, functionality second!**