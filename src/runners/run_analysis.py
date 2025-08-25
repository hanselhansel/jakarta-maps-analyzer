#!/usr/bin/env python3
"""
Automated Market Analysis Runner
Handles all the setup and execution automatically
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from pathlib import Path

def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking requirements...")
    
    # Check for .env file and API key
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found")
        return False
    
    with open('.env', 'r') as f:
        env_content = f.read()
        if 'GOOGLE_MAPS_API_KEY=' not in env_content:
            print("❌ Error: API key not found in .env")
            return False
        if 'YOUR_API_KEY_HERE' in env_content:
            print("❌ Error: Please replace YOUR_API_KEY_HERE with actual API key")
            return False
    
    # Check for required files
    required_files = [
        'main_comprehensive.py',
        'queries_comprehensive.csv',
        'search_zones.csv'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Error: Required file {file} not found")
            return False
    
    print("✅ All requirements met!")
    return True


def show_menu():
    """Display analysis options."""
    print("\n🐾 Pet Wellness Market Analysis")
    print("=" * 50)
    print("\nChoose analysis type:")
    print("\n1. 🚀 Quick Demo (Kemang area only)")
    print("   - 1 zone, 4 key searches")
    print("   - Time: ~2 minutes")
    print("   - Cost: ~$0.50")
    print("   - Perfect for testing")
    
    print("\n2. 🎯 Targeted Analysis (Choose area & category)")
    print("   - 1 zone, specific category")
    print("   - Time: ~5-10 minutes")
    print("   - Cost: ~$2-5")
    print("   - Good for focused research")
    
    print("\n3. 📊 Area Comprehensive (One area, all categories)")
    print("   - 1 zone, all 40 searches")
    print("   - Time: ~15 minutes")
    print("   - Cost: ~$5-8")
    print("   - Complete analysis for one area")
    
    print("\n4. 🌟 Full Comprehensive (All areas, all categories)")
    print("   - 10 zones, all 40 searches")
    print("   - Time: ~45 minutes")
    print("   - Cost: ~$20-30")
    print("   - Complete Jakarta analysis")
    
    print("\n5. ❌ Exit")
    
    return input("\nSelect option (1-5): ").strip()


def run_demo():
    """Run the demo analysis."""
    print("\n🚀 Running Demo Analysis...")
    
    # Create demo files
    import pandas as pd
    
    # Demo zone - Kemang only
    demo_zones = pd.DataFrame([{
        'zone_name': 'Kemang_Demo',
        'latitude': -6.2600,
        'longitude': 106.8130,
        'radius': 5000
    }])
    
    # Demo queries - key searches only
    demo_queries = pd.DataFrame([
        {'keyword': 'klinik hewan', 'category': 'Competitor', 'sub_category': 'Clinic_General'},
        {'keyword': 'pet grooming', 'category': 'Competitor', 'sub_category': 'Grooming_Only'},
        {'keyword': 'Ranch Market', 'category': 'Affluence_Proxy', 'sub_category': 'Premium_Supermarket'},
        {'keyword': 'pet cafe', 'category': 'Lifestyle_Proxy', 'sub_category': 'Pet_Cafe'},
    ])
    
    # Backup existing files
    backup_files()
    
    # Save demo files
    demo_zones.to_csv('search_zones.csv', index=False)
    demo_queries.to_csv('queries_comprehensive.csv', index=False)
    
    # Run analysis
    run_comprehensive_analysis()
    
    # Restore files
    restore_files()


def run_targeted():
    """Run targeted analysis with user selection."""
    import pandas as pd
    
    print("\n🎯 Targeted Analysis Setup")
    print("-" * 40)
    
    # Area selection
    areas = {
        '1': ('South_Jakarta_Kemang', -6.2600, 106.8130, 8000),
        '2': ('South_Jakarta_Pondok_Indah', -6.2840, 106.7810, 8000),
        '3': ('Central_Jakarta', -6.2088, 106.8456, 10000),
        '4': ('North_Jakarta_PIK', -6.1090, 106.7380, 8000),
        '5': ('BSD_City', -6.3019, 106.6527, 10000),
        '6': ('Gading_Serpong', -6.2351, 106.6289, 8000),
        '7': ('Alam_Sutera', -6.2247, 106.6534, 8000),
        '8': ('Bintaro', -6.2716, 106.7569, 8000)
    }
    
    print("\nSelect area:")
    for key, (name, _, _, _) in areas.items():
        print(f"{key}. {name.replace('_', ' ')}")
    
    area_choice = input("\nEnter area number: ").strip()
    if area_choice not in areas:
        print("❌ Invalid selection")
        return
    
    zone_name, lat, lon, radius = areas[area_choice]
    
    # Category selection
    print("\nSelect category:")
    print("1. Competitors only")
    print("2. Affluence indicators only")
    print("3. Pet lifestyle only")
    print("4. All categories")
    
    cat_choice = input("\nEnter category number: ").strip()
    
    # Prepare files
    backup_files()
    
    # Create zone file
    zone_df = pd.DataFrame([{
        'zone_name': zone_name,
        'latitude': lat,
        'longitude': lon,
        'radius': radius
    }])
    zone_df.to_csv('search_zones.csv', index=False)
    
    # Filter queries
    all_queries = pd.read_csv('queries_comprehensive.csv.bak')
    
    if cat_choice == '1':
        queries = all_queries[all_queries['category'] == 'Competitor']
    elif cat_choice == '2':
        queries = all_queries[all_queries['category'] == 'Affluence_Proxy']
    elif cat_choice == '3':
        queries = all_queries[all_queries['category'] == 'Lifestyle_Proxy']
    else:
        queries = all_queries
    
    queries.to_csv('queries_comprehensive.csv', index=False)
    
    print(f"\n📍 Area: {zone_name.replace('_', ' ')}")
    print(f"🔍 Searches: {len(queries)} queries")
    print(f"💰 Estimated cost: ${len(queries) * 0.10:.2f}")
    
    # Run analysis
    run_comprehensive_analysis()
    
    # Restore files
    restore_files()


def run_area_comprehensive():
    """Run comprehensive analysis for one area."""
    import pandas as pd
    
    print("\n📊 Area Comprehensive Analysis")
    print("-" * 40)
    
    # Area selection (same as targeted)
    areas = {
        '1': ('South_Jakarta_Kemang', -6.2600, 106.8130, 8000),
        '2': ('South_Jakarta_Pondok_Indah', -6.2840, 106.7810, 8000),
        '3': ('Central_Jakarta', -6.2088, 106.8456, 10000),
        '4': ('North_Jakarta_PIK', -6.1090, 106.7380, 8000),
        '5': ('BSD_City', -6.3019, 106.6527, 10000),
        '6': ('Gading_Serpong', -6.2351, 106.6289, 8000),
    }
    
    print("\nSelect area for comprehensive analysis:")
    for key, (name, _, _, _) in areas.items():
        print(f"{key}. {name.replace('_', ' ')}")
    
    area_choice = input("\nEnter area number: ").strip()
    if area_choice not in areas:
        print("❌ Invalid selection")
        return
    
    zone_name, lat, lon, radius = areas[area_choice]
    
    # Prepare files
    backup_files()
    
    # Create zone file
    zone_df = pd.DataFrame([{
        'zone_name': zone_name,
        'latitude': lat,
        'longitude': lon,
        'radius': radius
    }])
    zone_df.to_csv('search_zones.csv', index=False)
    
    # Use all queries (already in queries_comprehensive.csv)
    
    print(f"\n📍 Area: {zone_name.replace('_', ' ')}")
    print(f"🔍 Searches: All 40 queries")
    print(f"💰 Estimated cost: $5-8")
    
    # Run analysis
    run_comprehensive_analysis()
    
    # Restore files
    restore_files()


def run_full_comprehensive():
    """Run full comprehensive analysis."""
    print("\n🌟 Full Comprehensive Analysis")
    print("-" * 40)
    print("This will analyze:")
    print("- 10 strategic zones across Jakarta")
    print("- 40 different search queries")
    print("- ~400 total searches")
    print("\n⏱️  Estimated time: 45 minutes")
    print("💰 Estimated cost: $20-30")
    
    confirm = input("\nProceed with full analysis? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Analysis cancelled")
        return
    
    # No need to modify files - use existing comprehensive files
    run_comprehensive_analysis()


def backup_files():
    """Backup original files."""
    files = ['search_zones.csv', 'queries_comprehensive.csv']
    for file in files:
        if os.path.exists(file):
            os.rename(file, f"{file}.bak")


def restore_files():
    """Restore original files."""
    files = ['search_zones.csv', 'queries_comprehensive.csv']
    for file in files:
        if os.path.exists(f"{file}.bak"):
            if os.path.exists(file):
                os.remove(file)
            os.rename(f"{file}.bak", file)


def run_comprehensive_analysis():
    """Execute the main comprehensive analysis script."""
    print("\n🔄 Starting analysis...")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Run the analysis
        result = subprocess.run(
            [sys.executable, 'main_comprehensive.py'],
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        if result.returncode == 0:
            elapsed = time.time() - start_time
            print(f"\n✅ Analysis completed in {elapsed/60:.1f} minutes!")
            
            # Find the latest output file
            import glob
            csv_files = glob.glob('jakarta_pet_market_analysis_*.csv')
            if csv_files:
                latest_file = max(csv_files)
                print(f"\n📁 Results saved to: {latest_file}")
                
                # Quick stats
                import pandas as pd
                df = pd.read_csv(latest_file)
                print(f"\n📊 Quick Stats:")
                print(f"   Total locations found: {len(df)}")
                if 'category' in df.columns:
                    for cat, count in df['category'].value_counts().items():
                        print(f"   - {cat}: {count}")
        else:
            print("\n❌ Analysis failed. Check error messages above.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main entry point."""
    print("🐾 Pet Wellness Market Analysis - Automated Runner")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please fix the issues above and try again.")
        return
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            run_demo()
        elif choice == '2':
            run_targeted()
        elif choice == '3':
            run_area_comprehensive()
        elif choice == '4':
            run_full_comprehensive()
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid selection. Please try again.")
        
        if choice in ['1', '2', '3', '4']:
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()