#!/usr/bin/env python3
"""
Test Script for Self-Learning & AI Enhancement Features
Tests all AI management, model training, and self-learning capabilities
"""

import requests
import json
import time
import random
from datetime import datetime
import sys
import os

# Configuration
API_BASE = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
BRAND_EMAIL = "brand@example.com"
BRAND_PASSWORD = "brand123"

class AISelfLearningTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.brand_token = None
        self.brand_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate(self):
        """Authenticate as admin and brand user"""
        try:
            # Admin login
            admin_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if admin_response.status_code == 200:
                self.admin_token = admin_response.json()["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_test("Admin Authentication", True, "Admin logged in successfully")
            else:
                self.log_test("Admin Authentication", False, f"Failed: {admin_response.text}")
                return False
            
            # Brand login
            brand_response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": BRAND_EMAIL,
                "password": BRAND_PASSWORD
            })
            
            if brand_response.status_code == 200:
                self.brand_token = brand_response.json()["access_token"]
                self.log_test("Brand Authentication", True, "Brand user logged in successfully")
                
                # Get brand ID
                profile_response = self.session.get(f"{API_BASE}/users/me")
                if profile_response.status_code == 200:
                    self.brand_id = profile_response.json().get("brand_id")
                    self.log_test("Brand ID Retrieval", True, f"Brand ID: {self.brand_id}")
                else:
                    self.log_test("Brand ID Retrieval", False, "Could not get brand ID")
                    return False
            else:
                self.log_test("Brand Authentication", False, f"Failed: {brand_response.text}")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Authentication", False, f"Error: {str(e)}")
            return False

    def test_ai_status(self):
        """Test AI status endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/ai/status")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("AI Status", True, "AI status retrieved successfully", {
                    "openai_available": data.get("ai_engine_status", {}).get("openai_available"),
                    "google_nlp_available": data.get("ai_engine_status", {}).get("google_nlp_available"),
                    "ml_models_loaded": data.get("ai_engine_status", {}).get("ml_models_loaded"),
                    "total_learning_data": data.get("training_status", {}).get("total_learning_data", 0)
                })
            else:
                self.log_test("AI Status", False, f"Failed: {response.text}")
                
        except Exception as e:
            self.log_test("AI Status", False, f"Error: {str(e)}")

    def test_brand_ai_insights(self):
        """Test brand AI insights"""
        try:
            response = self.session.get(f"{API_BASE}/ai/brand/{self.brand_id}/insights")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Brand AI Insights", True, "Brand insights retrieved successfully", {
                    "conversation_patterns": len(data.get("conversation_patterns", [])),
                    "knowledge_base_size": data.get("knowledge_base", {}).get("total_entries", 0),
                    "recent_learning_data": data.get("recent_learning_data", 0)
                })
            else:
                self.log_test("Brand AI Insights", False, f"Failed: {response.text}")
                
        except Exception as e:
            self.log_test("Brand AI Insights", False, f"Error: {str(e)}")

    def test_training_history(self):
        """Test training history endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/ai/training-history")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Training History", True, f"Retrieved {len(data)} training records", {
                    "records_count": len(data),
                    "latest_record": data[0] if data else None
                })
            else:
                self.log_test("Training History", False, f"Failed: {response.text}")
                
        except Exception as e:
            self.log_test("Training History", False, f"Error: {str(e)}")

    def test_add_brand_knowledge(self):
        """Test adding brand knowledge"""
        try:
            knowledge_data = {
                "type": "faq",
                "question": "How do I reset my password?",
                "answer": "You can reset your password by clicking the 'Forgot Password' link on the login page.",
                "keywords": ["password", "reset", "forgot"],
                "language": "en"
            }
            
            response = self.session.post(f"{API_BASE}/ai/brand/{self.brand_id}/knowledge", json=knowledge_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Add Brand Knowledge", True, "Knowledge added successfully", {
                    "status": data.get("status"),
                    "knowledge_id": data.get("knowledge_id")
                })
            else:
                self.log_test("Add Brand Knowledge", False, f"Failed: {response.text}")
                
        except Exception as e:
            self.log_test("Add Brand Knowledge", False, f"Error: {str(e)}")

    def test_get_brand_knowledge(self):
        """Test getting brand knowledge"""
        try:
            response = self.session.get(f"{API_BASE}/ai/brand/{self.brand_id}/knowledge")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Brand Knowledge", True, f"Retrieved {len(data)} knowledge entries", {
                    "entries_count": len(data),
                    "sample_entry": data[0] if data else None
                })
            else:
                self.log_test("Get Brand Knowledge", False, f"Failed: {response.text}")
                
        except Exception as e:
            self.log_test("Get Brand Knowledge", False, f"Error: {str(e)}")

    def test_add_response_template(self):
        """Test adding response template"""
        try:
            template_data = {
                "template_name": "Password Reset Response",
                "template_text": "I understand you're having trouble with your password. {solution}",
                "category": "support",
                "urgency": "medium",
                "language": "en",
                "variables": ["solution"]
            }
            
            response = self.session.post(f"{API_BASE}/ai/brand/{self.brand_id}/templates", json=template_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Add Response Template", True, "Template added successfully", {
                    "status": data.get("status"),
                    "template_id": data.get("template_id")
                })
            else:
                self.log_test("Add Response Template", False, f"Failed: {response.text}")
                
        except Exception as e:
            self.log_test("Add Response Template", False, f"Error: {str(e)}")

    def test_get_response_templates(self):
        """Test getting response templates"""
        try:
            response = self.session.get(f"{API_BASE}/ai/brand/{self.brand_id}/templates")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Response Templates", True, f"Retrieved {len(data)} templates", {
                    "templates_count": len(data),
                    "sample_template": data[0] if data else None
                })
            else:
                self.log_test("Get Response Templates", False, f"Failed: {response.text}")
                
        except Exception as e:
            self.log_test("Get Response Templates", False, f"Error: {str(e)}")

    def test_analyze_text(self):
        """Test text analysis"""
        try:
            test_texts = [
                "I'm very angry about the poor service I received!",
                "Can you help me with my order?",
                "I have a suggestion for improving your product",
                "Thank you for the excellent support"
            ]
            
            for i, text in enumerate(test_texts):
                response = self.session.post(f"{API_BASE}/ai/analyze-text", params={
                    "text": text,
                    "brand_id": self.brand_id
                })
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Text Analysis {i+1}", True, f"Analyzed: '{text[:30]}...'", {
                        "category": data.get("analysis", {}).get("category"),
                        "urgency": data.get("analysis", {}).get("urgency"),
                        "sentiment_score": data.get("sentiment", {}).get("sentiment_score"),
                        "toxicity_score": data.get("sentiment", {}).get("toxicity_score")
                    })
                else:
                    self.log_test(f"Text Analysis {i+1}", False, f"Failed: {response.text}")
                    
        except Exception as e:
            self.log_test("Text Analysis", False, f"Error: {str(e)}")

    def test_generate_response(self):
        """Test response generation"""
        try:
            conversation_data = {
                "history": [
                    {"role": "user", "content": "I need help with my order"},
                    {"role": "assistant", "content": "I'd be happy to help you with your order. Could you please provide your order number?"}
                ],
                "brand_id": self.brand_id,
                "language": "en",
                "context": "Customer service conversation"
            }
            
            response = self.session.post(f"{API_BASE}/ai/generate-response", json=conversation_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Generate Response", True, "Response generated successfully", {
                    "response": data.get("response", "")[:50] + "...",
                    "language": data.get("language"),
                    "brand_id": data.get("brand_id")
                })
            else:
                self.log_test("Generate Response", False, f"Failed: {response.text}")
                
        except Exception as e:
            self.log_test("Generate Response", False, f"Error: {str(e)}")

    def test_learning_data(self):
        """Test learning data retrieval"""
        try:
            response = self.session.get(f"{API_BASE}/ai/learning-data", params={
                "brand_id": self.brand_id,
                "days": 30,
                "limit": 10
            })
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Learning Data", True, f"Retrieved {len(data)} learning records", {
                    "records_count": len(data),
                    "sample_record": data[0] if data else None
                })
            else:
                self.log_test("Learning Data", False, f"Failed: {response.text}")
                
        except Exception as e:
            self.log_test("Learning Data", False, f"Error: {str(e)}")

    def test_model_training(self):
        """Test model training"""
        try:
            # First, try to schedule training
            response = self.session.post(f"{API_BASE}/ai/train", params={
                "brand_id": self.brand_id,
                "force": False
            })
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Schedule Training", True, data.get("message", "Training scheduled"), {
                    "status": data.get("status"),
                    "training_samples": data.get("training_samples", 0)
                })
            else:
                self.log_test("Schedule Training", False, f"Failed: {response.text}")
                
        except Exception as e:
            self.log_test("Schedule Training", False, f"Error: {str(e)}")

    def test_retrain_models(self):
        """Test model retraining"""
        try:
            response = self.session.post(f"{API_BASE}/ai/retrain", params={
                "brand_id": self.brand_id,
                "force": True
            })
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Retrain Models", True, data.get("message", "Models retrained"), {
                    "status": data.get("status"),
                    "accuracy": data.get("accuracy")
                })
            else:
                self.log_test("Retrain Models", False, f"Failed: {response.text}")
                
        except Exception as e:
            self.log_test("Retrain Models", False, f"Error: {str(e)}")

    def test_conversation_with_learning(self):
        """Test conversation with self-learning features"""
        try:
            # Test multiple conversations to trigger learning
            test_messages = [
                "How do I reset my password?",
                "I'm having trouble with my order",
                "Can you help me with billing?",
                "I want to complain about poor service"
            ]
            
            for i, message in enumerate(test_messages):
                response = self.session.post(f"{API_BASE}/chat/send", json={
                    "message": message,
                    "sessionId": f"learning_test_{i}_{int(time.time())}"
                })
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Learning Conversation {i+1}", True, f"Processed: '{message[:30]}...'", {
                        "response": data.get("response", "")[:50] + "...",
                        "session_id": data.get("sessionId")
                    })
                else:
                    self.log_test(f"Learning Conversation {i+1}", False, f"Failed: {response.text}")
                    
                time.sleep(1)  # Small delay between requests
                
        except Exception as e:
            self.log_test("Learning Conversations", False, f"Error: {str(e)}")

    def test_multilingual_ai(self):
        """Test multilingual AI capabilities"""
        try:
            multilingual_tests = [
                {"text": "Hello, I need help", "language": "en"},
                {"text": "नमस्ते, मुझे मदद चाहिए", "language": "hi"},
                {"text": "Hola, necesito ayuda", "language": "es"},
                {"text": "Bonjour, j'ai besoin d'aide", "language": "fr"}
            ]
            
            for test in multilingual_tests:
                response = self.session.post(f"{API_BASE}/ai/analyze-text", params={
                    "text": test["text"],
                    "brand_id": self.brand_id
                })
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Multilingual AI ({test['language']})", True, f"Analyzed {test['language']} text", {
                        "language": test["language"],
                        "category": data.get("analysis", {}).get("category"),
                        "sentiment_score": data.get("sentiment", {}).get("sentiment_score")
                    })
                else:
                    self.log_test(f"Multilingual AI ({test['language']})", False, f"Failed: {response.text}")
                    
        except Exception as e:
            self.log_test("Multilingual AI", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all AI self-learning tests"""
        print("🧠 AI Self-Learning & Enhancement Test Suite")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        print("\n🚀 Starting AI Self-Learning Tests...\n")
        
        # Core AI Management Tests
        self.test_ai_status()
        self.test_brand_ai_insights()
        self.test_training_history()
        
        # Knowledge Management Tests
        self.test_add_brand_knowledge()
        self.test_get_brand_knowledge()
        
        # Response Template Tests
        self.test_add_response_template()
        self.test_get_response_templates()
        
        # AI Analysis Tests
        self.test_analyze_text()
        self.test_generate_response()
        
        # Learning Data Tests
        self.test_learning_data()
        
        # Model Training Tests
        self.test_model_training()
        self.test_retrain_models()
        
        # Conversation Learning Tests
        self.test_conversation_with_learning()
        
        # Multilingual Tests
        self.test_multilingual_ai()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 AI Self-Learning Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_self_learning_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "test_suite": "AI Self-Learning & Enhancement",
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {filename}")
        
        if failed_tests == 0:
            print("\n🎉 All AI Self-Learning tests passed!")
        else:
            print(f"\n⚠️  {failed_tests} tests failed. Please check the implementation.")

if __name__ == "__main__":
    tester = AISelfLearningTester()
    tester.run_all_tests() 