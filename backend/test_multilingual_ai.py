#!/usr/bin/env python3
"""
Test script for multilingual AI capabilities including language detection and translation
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def test_language_detection():
    """Test language detection functionality"""
    print("=== Testing Language Detection ===")
    
    # Test different languages
    test_cases = [
        {
            "text": "Hello, I need help with my order",
            "expected_language": "en",
            "description": "English text"
        },
        {
            "text": "नमस्ते, मुझे मेरे ऑर्डर में मदद चाहिए",
            "expected_language": "hi",
            "description": "Hindi text"
        },
        {
            "text": "Hola, necesito ayuda con mi pedido",
            "expected_language": "es",
            "description": "Spanish text"
        },
        {
            "text": "Bonjour, j'ai besoin d'aide avec ma commande",
            "expected_language": "fr",
            "description": "French text"
        },
        {
            "text": "Hallo, ich brauche Hilfe mit meiner Bestellung",
            "expected_language": "de",
            "description": "German text"
        }
    ]
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/ai/detect-language",
                params={"text": test_case["text"]},
                headers={"Authorization": f"Bearer {get_admin_token()}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                detected_language = data.get("detection_result", {}).get("language_code")
                confidence = data.get("detection_result", {}).get("confidence", 0)
                
                if detected_language == test_case["expected_language"]:
                    print(f"✅ {test_case['description']} - Success (confidence: {confidence:.2f})")
                else:
                    print(f"⚠️ {test_case['description']} - Detected: {detected_language}, Expected: {test_case['expected_language']} (confidence: {confidence:.2f})")
            else:
                print(f"❌ {test_case['description']} - Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test_case['description']} - Error: {e}")

def test_text_translation():
    """Test text translation functionality"""
    print("\n=== Testing Text Translation ===")
    
    # Test translation pairs
    test_cases = [
        {
            "text": "Hello, I have a complaint about your service",
            "source_language": "en",
            "target_language": "hi",
            "description": "English to Hindi"
        },
        {
            "text": "नमस्ते, मुझे आपकी सेवा के बारे में शिकायत है",
            "source_language": "hi",
            "target_language": "en",
            "description": "Hindi to English"
        },
        {
            "text": "Hola, tengo una queja sobre su servicio",
            "source_language": "es",
            "target_language": "en",
            "description": "Spanish to English"
        },
        {
            "text": "Bonjour, j'ai une plainte concernant votre service",
            "source_language": "fr",
            "target_language": "en",
            "description": "French to English"
        }
    ]
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/ai/translate-text",
                params={
                    "text": test_case["text"],
                    "target_language": test_case["target_language"],
                    "source_language": test_case["source_language"]
                },
                headers={"Authorization": f"Bearer {get_admin_token()}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                translated_text = data.get("translation_result", {}).get("translated_text")
                confidence = data.get("translation_result", {}).get("confidence", 0)
                
                if translated_text and translated_text != test_case["text"]:
                    print(f"✅ {test_case['description']} - Success (confidence: {confidence:.2f})")
                    print(f"   Original: {test_case['text'][:50]}...")
                    print(f"   Translated: {translated_text[:50]}...")
                else:
                    print(f"⚠️ {test_case['description']} - No translation performed (confidence: {confidence:.2f})")
            else:
                print(f"❌ {test_case['description']} - Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test_case['description']} - Error: {e}")

def test_auto_detect_translate():
    """Test automatic language detection and translation"""
    print("\n=== Testing Auto Detect and Translate ===")
    
    # Test auto detection and translation
    test_cases = [
        {
            "text": "मुझे आपकी सेवा में समस्या है",
            "target_language": "en",
            "description": "Hindi to English auto-detect"
        },
        {
            "text": "Tengo un problema con su servicio",
            "target_language": "en",
            "description": "Spanish to English auto-detect"
        },
        {
            "text": "J'ai un problème avec votre service",
            "target_language": "en",
            "description": "French to English auto-detect"
        },
        {
            "text": "I have a problem with your service",
            "target_language": "hi",
            "description": "English to Hindi auto-detect"
        }
    ]
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/ai/auto-detect-translate",
                params={
                    "text": test_case["text"],
                    "target_language": test_case["target_language"]
                },
                headers={"Authorization": f"Bearer {get_admin_token()}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                detected_language = data.get("detected_language", {}).get("language_code")
                translated_text = data.get("translation", {}).get("translated_text")
                detection_confidence = data.get("detected_language", {}).get("confidence", 0)
                translation_confidence = data.get("translation", {}).get("confidence", 0)
                
                print(f"✅ {test_case['description']} - Success")
                print(f"   Detected: {detected_language} (confidence: {detection_confidence:.2f})")
                print(f"   Translated: {translated_text[:50]}... (confidence: {translation_confidence:.2f})")
            else:
                print(f"❌ {test_case['description']} - Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test_case['description']} - Error: {e}")

def test_multilingual_message_processing():
    """Test complete multilingual message processing pipeline"""
    print("\n=== Testing Multilingual Message Processing ===")
    
    # Test complete processing pipeline
    test_cases = [
        {
            "text": "मुझे आपकी सेवा में बहुत समस्या है और मैं बहुत नाराज हूं",
            "target_language": "en",
            "description": "Hindi complaint processing"
        },
        {
            "text": "Tengo una queja muy seria sobre su servicio y estoy muy molesto",
            "target_language": "en",
            "description": "Spanish complaint processing"
        },
        {
            "text": "J'ai une plainte très sérieuse concernant votre service et je suis très contrarié",
            "target_language": "en",
            "description": "French complaint processing"
        },
        {
            "text": "I have a very serious complaint about your service and I am very angry",
            "target_language": "hi",
            "description": "English complaint processing to Hindi"
        }
    ]
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/ai/process-multilingual",
                params={
                    "text": test_case["text"],
                    "target_language": test_case["target_language"]
                },
                headers={"Authorization": f"Bearer {get_admin_token()}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                multilingual_result = data.get("multilingual_processing", {})
                ai_analysis = data.get("ai_analysis", {})
                sentiment_analysis = data.get("sentiment_analysis", {})
                
                detected_language = multilingual_result.get("detected_language", {}).get("language_code")
                translated_text = multilingual_result.get("translation", {}).get("translated_text")
                category = ai_analysis.get("category")
                urgency = ai_analysis.get("urgency")
                sentiment_score = sentiment_analysis.get("sentiment_score", 0)
                
                print(f"✅ {test_case['description']} - Success")
                print(f"   Detected Language: {detected_language}")
                print(f"   Category: {category}, Urgency: {urgency}")
                print(f"   Sentiment Score: {sentiment_score:.2f}")
                print(f"   Translated: {translated_text[:50]}...")
            else:
                print(f"❌ {test_case['description']} - Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test_case['description']} - Error: {e}")

def test_supported_languages():
    """Test getting supported languages"""
    print("\n=== Testing Supported Languages ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/ai/supported-languages",
            headers={"Authorization": f"Bearer {get_admin_token()}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            languages = data.get("languages", {})
            total_count = data.get("total_count", 0)
            
            print(f"✅ Supported Languages - Success")
            print(f"   Total Languages: {total_count}")
            print(f"   Primary Language: {data.get('primary_language')}")
            print(f"   Detection Methods: {', '.join(data.get('detection_methods', []))}")
            print(f"   Translation Methods: {', '.join(data.get('translation_methods', []))}")
            
            # Show some example languages
            print("   Example Languages:")
            for code, name in list(languages.items())[:10]:
                print(f"     {code}: {name}")
                
        else:
            print(f"❌ Supported Languages - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Supported Languages - Error: {e}")

def test_multilingual_conversation():
    """Test multilingual conversation flow"""
    print("\n=== Testing Multilingual Conversation Flow ===")
    
    # Test conversation in different languages
    conversation_tests = [
        {
            "language": "hi",
            "messages": [
                "नमस्ते, मुझे मदद चाहिए",
                "मेरे ऑर्डर में समस्या है",
                "धन्यवाद"
            ],
            "description": "Hindi conversation"
        },
        {
            "language": "es",
            "messages": [
                "Hola, necesito ayuda",
                "Tengo un problema con mi pedido",
                "Gracias"
            ],
            "description": "Spanish conversation"
        }
    ]
    
    for test in conversation_tests:
        print(f"\n--- {test['description']} ---")
        
        for i, message in enumerate(test["messages"]):
            try:
                response = requests.post(
                    f"{BASE_URL}/api/v1/ai/process-multilingual",
                    params={
                        "text": message,
                        "target_language": "en"
                    },
                    headers={"Authorization": f"Bearer {get_admin_token()}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    detected_language = data.get("multilingual_processing", {}).get("detected_language", {}).get("language_code")
                    translated_text = data.get("multilingual_processing", {}).get("translation", {}).get("translated_text")
                    
                    print(f"  Message {i+1}: {message}")
                    print(f"    Detected: {detected_language}")
                    print(f"    Translated: {translated_text}")
                else:
                    print(f"  Message {i+1}: Failed - {response.status_code}")
                    
            except Exception as e:
                print(f"  Message {i+1}: Error - {e}")

def test_multilingual_error_handling():
    """Test error handling in multilingual processing"""
    print("\n=== Testing Multilingual Error Handling ===")
    
    # Test edge cases
    edge_cases = [
        {
            "text": "",
            "description": "Empty text"
        },
        {
            "text": "1234567890",
            "description": "Numbers only"
        },
        {
            "text": "!@#$%^&*()",
            "description": "Special characters only"
        },
        {
            "text": "a" * 1000,
            "description": "Very long text"
        }
    ]
    
    for test_case in edge_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/ai/detect-language",
                params={"text": test_case["text"]},
                headers={"Authorization": f"Bearer {get_admin_token()}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                detected_language = data.get("detection_result", {}).get("language_code")
                confidence = data.get("detection_result", {}).get("confidence", 0)
                
                print(f"✅ {test_case['description']} - Handled (language: {detected_language}, confidence: {confidence:.2f})")
            else:
                print(f"❌ {test_case['description']} - Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test_case['description']} - Error: {e}")

def get_admin_token():
    """Get admin authentication token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Failed to get admin token: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting admin token: {e}")
        return None

def main():
    """Run all multilingual AI tests"""
    print("Starting Multilingual AI Tests")
    print("=" * 60)
    
    # Test language detection
    test_language_detection()
    
    # Test text translation
    test_text_translation()
    
    # Test auto detect and translate
    test_auto_detect_translate()
    
    # Test multilingual message processing
    test_multilingual_message_processing()
    
    # Test supported languages
    test_supported_languages()
    
    # Test multilingual conversation flow
    test_multilingual_conversation()
    
    # Test error handling
    test_multilingual_error_handling()
    
    print("\n" + "=" * 60)
    print("Multilingual AI Tests Completed")

if __name__ == "__main__":
    main() 