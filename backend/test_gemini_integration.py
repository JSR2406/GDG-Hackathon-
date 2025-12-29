import asyncio
import os
import shutil
from app.services.gemini_agent import get_gemini_analyzer

async def test_gemini_integration():
    print("🧪 Starting Gemini Integration Test...")
    
    # 1. Setup Test Data
    test_image_path = "uploads/test_image.jpg"
    
    # Create a real (small) image if it doesn't exist processing might fail on "dummy text"
    # So we'll create a tiny 1x1 pixel image using PIL to be safe
    from PIL import Image
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save(test_image_path)
    print(f"✅ Created test image at {test_image_path}")
    
    # 2. Initialize Analyzer
    analyzer = get_gemini_analyzer()
    api_key_status = "✅ Present" if analyzer.model else "⚠️ Missing (Using Mock)"
    print(f"ℹ️ API Key Status: {api_key_status}")
    
    # 3. specific test for "textbook" behavior (mock trigger)
    # We rename the file to trigger specific mock logic if key is missing
    mock_trigger_path = "uploads/engineering_textbook.jpg"
    shutil.copy(test_image_path, mock_trigger_path)
    
    try:
        print("\n🔍 Analyzing Item 1 (Textbook Context)...")
        result = await analyzer.analyze_item_photo(mock_trigger_path)
        
        # 4. Validate Schema
        required_fields = [
            "item_name", "category", "condition", 
            "estimated_department", "description", 
            "suggested_wants", "eco_value", "confidence"
        ]
        
        missing_fields = [f for f in required_fields if f not in result]
        
        if missing_fields:
            print(f"❌ FAST FAIL: Missing fields in response: {missing_fields}")
        else:
            print("✅ Response Schema Valid")
            print(f"   Name: {result['item_name']}")
            print(f"   Category: {result['category']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Eco Value: {result['eco_value']}")
            
        # 5. Test Error Handling (Non-existent file)
        print("\n🔍 Testing Error Handling...")
        try:
            await analyzer.analyze_item_photo("non_existent_file.jpg")
            print("❌ Should have failed or handled non-existent file gracefully") 
            # Note: The current implementation catches exception and returns mock, 
            # so we check if it returns a valid "fallback" response or valid mock
        except Exception as e:
            print(f"✅ Correctly caught exception: {e}") 

    except Exception as e:
        print(f"❌ Test Failed with Exception: {e}")
    finally:
        # Cleanup
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        if os.path.exists(mock_trigger_path):
            os.remove(mock_trigger_path)
        print("\n✨ Test Complete")

if __name__ == "__main__":
    asyncio.run(test_gemini_integration())
