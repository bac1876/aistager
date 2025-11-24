"""
Test script for alternative AI staging APIs
Based on the API assessment research
"""

import os
from dotenv import load_dotenv

load_dotenv('.env.local')

# Test image URL (empty living room)
TEST_IMAGE = "https://www.dropbox.com/scl/fi/ly7a7f3ijoh8ljm5vgqqt/002_dsc02663_859.jpg?rlkey=m0ovvg2lrfe6mr39gzrjcvjvn&dl=1"

print("="*60)
print("ALTERNATIVE AI STAGING APIS - COMPARISON GUIDE")
print("="*60)
print("\nBased on the comprehensive API assessment, here are the top alternatives to test:\n")

# Top alternatives based on research
alternatives = [
    {
        "name": "Gepetto",
        "website": "https://gepetto.app",
        "pricing": "€39/month (~$44) for unlimited generations",
        "free_trial": "50 API calls",
        "key_features": [
            "Virtual staging API",
            "Room clearing (furniture removal)",
            "Wall repainting",
            "Floor changes",
            "Lightning-fast processing (15-30 seconds)",
            "Well-documented API"
        ],
        "api_endpoints": {
            "base": "https://api.gepetto.app/v1",
            "virtual_staging": "/furnish",
            "room_clearing": "/declutter",
            "wall_paint": "/repaint"
        },
        "test_steps": """
        1. Sign up at https://gepetto.app
        2. Get API key from dashboard
        3. Test with their 50 free API calls
        4. Key parameters:
           - image_url: Your image URL
           - room_type: living_room, bedroom, etc.
           - style: modern, scandinavian, etc.
        """
    },
    {
        "name": "HomeDesigns.AI",
        "website": "https://homedesigns.ai",
        "pricing": "$29/month for unlimited designs (Pro plan)",
        "free_trial": "Free staging tool available",
        "key_features": [
            "Furniture removal API",
            "Virtual staging API",
            "Floor editor",
            "Paint visualizer",
            "Auto-fill empty spaces",
            "Masking support"
        ],
        "api_endpoints": {
            "base": "https://api.homedesigns.ai/v1",
            "virtual_staging": "/stage",
            "furniture_removal": "/remove",
            "floor_editor": "/floor",
            "paint": "/paint"
        },
        "test_steps": """
        1. Sign up at https://homedesigns.ai
        2. Get API access with Pro plan
        3. Test endpoints:
           - POST /stage with image_url and style
           - Supports selective masking
        """
    },
    {
        "name": "InstantDecoAI",
        "website": "https://instantdeco.ai",
        "pricing": "$39/month unlimited OR $4/image",
        "free_trial": "Yes",
        "key_features": [
            "AI Virtual Staging",
            "AI Virtual Renovation",
            "Remove clutter/furniture",
            "Wall/floor/ceiling upgrades",
            "Floor material selection"
        ],
        "test_steps": """
        1. Sign up for free trial
        2. Test virtual staging endpoint
        3. Compare quality with ReimagineHome
        """
    },
    {
        "name": "SofaBrain",
        "website": "https://sofabrain.com",
        "pricing": "$449/year for 500 images/month (Pro Plan)",
        "free_trial": "No (API for Pro users only)",
        "key_features": [
            "Well-documented RESTful API",
            "Furnishing empty rooms",
            "Selective color change",
            "Object replacement",
            "AI-driven furniture removal",
            "White-label integration",
            "SDK libraries"
        ],
        "test_steps": """
        1. Sign up for Pro Plan
        2. Access comprehensive API docs
        3. Use their SDKs for easier integration
        4. Test white-label options
        """
    },
    {
        "name": "Collov",
        "website": "https://collov.com",
        "pricing": "Contact for API pricing",
        "free_trial": "Web app available",
        "key_features": [
            "AI Virtual Staging",
            "Decluttering",
            "Material Fill tool",
            "Wall/floor/cabinet customization",
            "White-label solutions",
            "Dedicated support"
        ],
        "test_steps": """
        1. Contact for API access
        2. Test Material Fill tool
        3. Evaluate white-label options
        """
    }
]

print("TOP 5 ALTERNATIVES TO TEST:\n")

for i, api in enumerate(alternatives, 1):
    print(f"{i}. {api['name']}")
    print(f"   Website: {api['website']}")
    print(f"   Pricing: {api['pricing']}")
    print(f"   Free Trial: {api['free_trial']}")
    print(f"   Key Features:")
    for feature in api['key_features'][:3]:
        print(f"   - {feature}")
    print()

print("\n" + "="*60)
print("RECOMMENDED TESTING APPROACH:")
print("="*60)
print("""
1. GEPETTO (Best Value)
   - €39/month unlimited
   - 50 free API calls
   - Fast processing
   - Good documentation
   
2. HOMEDESIGNS.AI (Most Features)
   - $29/month unlimited
   - Comprehensive feature set
   - Free staging tool to test
   
3. INSTANTDECOAI (Flexible Pricing)
   - $39/month unlimited OR pay-per-image
   - Free trial available
   - Good for testing quality

To test these APIs:
1. Sign up for free trials where available
2. Use the same test image for fair comparison
3. Compare: Quality, Speed, Price, Documentation
4. Test both empty room staging AND furniture removal
""")

print("\n" + "="*60)
print("QUICK COMPARISON WITH REIMAGINEHOME:")
print("="*60)
print("""
ReimagineHome: $14/month for 30 creations
- Pros: Cheapest entry price, working implementation
- Cons: Variable quality, better for redesign than staging

Gepetto: €39/month unlimited
- Pros: Unlimited generations, fast, good docs
- Cons: Higher monthly cost

HomeDesigns.AI: $29/month unlimited
- Pros: Feature-rich, unlimited, masking support
- Cons: Need Pro plan for API

Best approach: Test Gepetto's 50 free calls first!
""")

# Create a simple test script template
test_template = '''
# Example test script for Gepetto API
import requests

GEPETTO_API_KEY = "your_api_key_here"
TEST_IMAGE = "{}"

headers = {{"Authorization": f"Bearer {{GEPETTO_API_KEY}}"}}

# Virtual staging request
response = requests.post(
    "https://api.gepetto.app/v1/furnish",
    headers=headers,
    json={{
        "image_url": TEST_IMAGE,
        "room_type": "living_room",
        "style": "modern",
        "quality": "high"
    }}
)

if response.status_code == 200:
    result = response.json()
    print(f"Staged image: {{result['output_url']}}")
else:
    print(f"Error: {{response.status_code}}")
'''.format(TEST_IMAGE)

# Save test template
with open('test_gepetto_example.py', 'w') as f:
    f.write(test_template)

print("\nCreated test_gepetto_example.py for testing Gepetto API")
print("\nNext steps:")
print("1. Sign up for Gepetto (50 free API calls)")
print("2. Update test_gepetto_example.py with your API key")
print("3. Run the test and compare quality with ReimagineHome")
print("4. Report findings to decide if switching is worthwhile")