import google.generativeai as genai
import os
import base64
import json
from typing import Dict, Optional
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

class GeminiItemAnalyzer:
    """Singleton class for Gemini Vision-based item analysis"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_key_here":
            print("⚠️ WARNING: GEMINI_API_KEY not set. Using mock responses.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def analyze_item_photo(self, image_path: str) -> Dict:
        """
        Analyze item photo using Gemini Vision
        Returns structured JSON with item details
        """
        
        # If no API key, return mock data
        if not self.model:
            return self._get_mock_analysis(image_path)
        
        try:
            # Load and prepare image
            img = Image.open(image_path)
            
            # Create detailed prompt for Gemini
            prompt = """
            Analyze this image of a campus item and provide a detailed JSON response with the following structure:
            {
                "item_name": "specific name of the item",
                "category": "category (e.g., textbook, lab equipment, stationery, clothing, electronics)",
                "condition": "condition (excellent, good, fair, poor)",
                "estimated_department": "likely academic department (Mechanical, Computer Science, Electrical, Civil, etc.)",
                "description": "brief 1-2 sentence description",
                "suggested_wants": ["3 items students might want to swap for this"],
                "eco_value": 8,
                "confidence": 0.95,
                "reusability_score": 9
            }
            
            Be specific and practical. Focus on campus-relevant items.
            """
            
            # Generate content
            response = self.model.generate_content([prompt, img])
            
            # Parse JSON from response
            response_text = response.text.strip()
            
            # Extract JSON from markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(response_text)
            
            # Validate required fields
            required_fields = ["item_name", "category", "condition", "description"]
            for field in required_fields:
                if field not in analysis:
                    analysis[field] = "Unknown"
            
            # Set defaults for optional fields
            analysis.setdefault("estimated_department", None)
            analysis.setdefault("suggested_wants", ["Books", "Stationery", "Lab Equipment"])
            analysis.setdefault("eco_value", 7)
            analysis.setdefault("confidence", 0.85)
            analysis.setdefault("reusability_score", 8)
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing image with Gemini: {e}")
            return self._get_mock_analysis(image_path)
    
    def _get_mock_analysis(self, image_path: str) -> Dict:
        """Return mock analysis when Gemini API is not available"""
        filename = os.path.basename(image_path).lower()
        
        # Simple keyword-based mock responses
        if "book" in filename or "text" in filename:
            return {
                "item_name": "Engineering Textbook",
                "category": "textbook",
                "condition": "good",
                "estimated_department": "Mechanical Engineering",
                "description": "Standard engineering textbook in good condition, suitable for semester coursework.",
                "suggested_wants": ["Lab Equipment", "Drafting Tools", "Scientific Calculator"],
                "eco_value": 8,
                "confidence": 0.90,
                "reusability_score": 9
            }
        elif "lab" in filename or "coat" in filename:
            return {
                "item_name": "Laboratory Coat",
                "category": "lab equipment",
                "condition": "excellent",
                "estimated_department": "Chemistry",
                "description": "White laboratory coat, barely used, perfect for lab sessions.",
                "suggested_wants": ["Safety Goggles", "Lab Manual", "Textbooks"],
                "eco_value": 7,
                "confidence": 0.88,
                "reusability_score": 8
            }
        elif "draft" in filename or "compass" in filename:
            return {
                "item_name": "Drafting Compass Set",
                "category": "drafting tools",
                "condition": "good",
                "estimated_department": "Mechanical Engineering",
                "description": "Professional drafting compass with accessories, ideal for technical drawing.",
                "suggested_wants": ["Textbooks", "Lab Equipment", "Calculator"],
                "eco_value": 9,
                "confidence": 0.92,
                "reusability_score": 10
            }
        else:
            return {
                "item_name": "Campus Item",
                "category": "general",
                "condition": "good",
                "estimated_department": None,
                "description": "Reusable campus item in good condition.",
                "suggested_wants": ["Books", "Stationery", "Equipment"],
                "eco_value": 7,
                "confidence": 0.80,
                "reusability_score": 7
            }
    
    async def generate_swap_proposal(self, match_data: Dict) -> str:
        """Generate a natural language swap proposal (optional advanced feature)"""
        if not self.model:
            return "Swap proposal: All parties exchange items as matched."
        
        try:
            prompt = f"""
            Generate a friendly, encouraging swap proposal message for this match:
            {json.dumps(match_data, indent=2)}
            
            Make it enthusiastic and highlight the environmental benefit.
            Keep it under 100 words.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return "Great match found! Complete this swap to earn Eco-Credits and reduce campus waste."

# Singleton instance
_gemini_analyzer = None

def get_gemini_analyzer() -> GeminiItemAnalyzer:
    """Get or create singleton Gemini analyzer instance"""
    global _gemini_analyzer
    if _gemini_analyzer is None:
        _gemini_analyzer = GeminiItemAnalyzer()
    return _gemini_analyzer
