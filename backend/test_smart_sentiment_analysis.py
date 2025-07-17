#!/usr/bin/env python3
"""
Test Script for Smart Sentiment & Severity Analysis
Tests the comprehensive sentiment and severity analysis pipeline
"""

import requests
import json
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_BASE = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

class SmartSentimentAnalysisTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        
    def log_test(self, test_name: str, success: bool, message: str, details: dict = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {message}")
        if details:
            logger.info(f"  Details: {json.dumps(details, indent=2)}")

    def authenticate(self):
        """Authenticate with the API"""
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("Authentication", True, "Successfully authenticated")
                return True
            else:
                self.log_test("Authentication", False, f"Failed to authenticate: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {str(e)}")
            return False

    def test_comprehensive_text_analysis(self):
        """Test comprehensive text analysis"""
        try:
            test_cases = [
                {
                    "text": "I'm absolutely furious about the terrible service I received yesterday! This is completely unacceptable and I demand immediate action!",
                    "expected_sentiment": "negative",
                    "expected_severity": "high",
                    "expected_emotion": "anger"
                },
                {
                    "text": "Thank you so much for the excellent support you provided. I'm very happy with the resolution!",
                    "expected_sentiment": "positive",
                    "expected_severity": "low",
                    "expected_emotion": "joy"
                },
                {
                    "text": "I have a simple question about my order. Can you help me?",
                    "expected_sentiment": "neutral",
                    "expected_severity": "low",
                    "expected_emotion": "neutral"
                },
                {
                    "text": "This is an emergency situation that requires immediate attention. Someone could get hurt!",
                    "expected_sentiment": "negative",
                    "expected_severity": "critical",
                    "expected_emotion": "fear"
                },
                {
                    "text": "I'm very disappointed with the quality of your product. It's not what I expected.",
                    "expected_sentiment": "negative",
                    "expected_severity": "medium",
                    "expected_emotion": "sadness"
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                response = self.session.post(f"{API_BASE}/ai/analyze-text", params={
                    "text": test_case["text"],
                    "context": "Test context"
                })
                
                if response.status_code == 200:
                    data = response.json()
                    analysis = data.get("analysis", {})
                    
                    # Check sentiment
                    sentiment = analysis.get("sentiment_analysis", {}).get("combined_sentiment", {}).get("sentiment_label", "neutral")
                    sentiment_match = sentiment == test_case["expected_sentiment"]
                    
                    # Check severity
                    severity = analysis.get("severity_analysis", {}).get("primary_severity", "low")
                    severity_match = severity == test_case["expected_severity"]
                    
                    # Check emotion
                    emotion = analysis.get("emotion_analysis", {}).get("primary_emotion", "neutral")
                    emotion_match = emotion == test_case["expected_emotion"]
                    
                    success = sentiment_match and severity_match and emotion_match
                    
                    self.log_test(f"Comprehensive Analysis {i+1}", success, 
                                f"Analyzed: '{test_case['text'][:50]}...'", {
                                    "sentiment": sentiment,
                                    "severity": severity,
                                    "emotion": emotion,
                                    "toxicity_score": analysis.get("toxicity_analysis", {}).get("combined_abuse_score", 0.0),
                                    "risk_level": analysis.get("risk_assessment", {}).get("risk_level", "low")
                                })
                else:
                    self.log_test(f"Comprehensive Analysis {i+1}", False, f"Failed: {response.text}")
                    
        except Exception as e:
            self.log_test("Comprehensive Text Analysis", False, f"Error: {str(e)}")

    def test_sentiment_analysis(self):
        """Test dedicated sentiment analysis endpoint"""
        try:
            test_texts = [
                "I'm very happy with the service!",
                "I'm extremely angry about this issue!",
                "This is just a normal question.",
                "I'm so frustrated with the poor quality!",
                "Thank you for the wonderful support!"
            ]
            
            for i, text in enumerate(test_texts):
                response = self.session.post(f"{API_BASE}/ai/sentiment-analysis", params={
                    "text": text
                })
                
                if response.status_code == 200:
                    data = response.json()
                    sentiment_analysis = data.get("sentiment_analysis", {})
                    emotion_analysis = data.get("emotion_analysis", {})
                    
                    self.log_test(f"Sentiment Analysis {i+1}", True, 
                                f"Analyzed: '{text[:30]}...'", {
                                    "sentiment_score": sentiment_analysis.get("combined_sentiment", {}).get("sentiment_score", 0.0),
                                    "sentiment_label": sentiment_analysis.get("combined_sentiment", {}).get("sentiment_label", "neutral"),
                                    "primary_emotion": emotion_analysis.get("primary_emotion", "neutral"),
                                    "toxicity_score": data.get("toxicity_analysis", {}).get("combined_abuse_score", 0.0)
                                })
                else:
                    self.log_test(f"Sentiment Analysis {i+1}", False, f"Failed: {response.text}")
                    
        except Exception as e:
            self.log_test("Sentiment Analysis", False, f"Error: {str(e)}")

    def test_severity_assessment(self):
        """Test severity assessment endpoint"""
        try:
            test_cases = [
                {
                    "text": "This is an emergency!",
                    "expected_severity": "critical"
                },
                {
                    "text": "I'm very angry about this issue!",
                    "expected_severity": "high"
                },
                {
                    "text": "I have a problem with my order.",
                    "expected_severity": "medium"
                },
                {
                    "text": "Just a simple question.",
                    "expected_severity": "low"
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                response = self.session.post(f"{API_BASE}/ai/severity-assessment", params={
                    "text": test_case["text"],
                    "context": "Test context"
                })
                
                if response.status_code == 200:
                    data = response.json()
                    severity = data.get("severity_analysis", {}).get("primary_severity", "low")
                    risk_level = data.get("risk_assessment", {}).get("risk_level", "low")
                    
                    success = severity == test_case["expected_severity"]
                    
                    self.log_test(f"Severity Assessment {i+1}", success, 
                                f"Assessed: '{test_case['text'][:30]}...'", {
                                    "severity": severity,
                                    "risk_level": risk_level,
                                    "confidence": data.get("severity_analysis", {}).get("confidence", 0.0)
                                })
                else:
                    self.log_test(f"Severity Assessment {i+1}", False, f"Failed: {response.text}")
                    
        except Exception as e:
            self.log_test("Severity Assessment", False, f"Error: {str(e)}")

    def test_emotion_detection(self):
        """Test emotion detection endpoint"""
        try:
            test_cases = [
                {
                    "text": "I'm so angry about this!",
                    "expected_emotion": "anger"
                },
                {
                    "text": "I'm very happy with the service!",
                    "expected_emotion": "joy"
                },
                {
                    "text": "I'm worried about this issue.",
                    "expected_emotion": "fear"
                },
                {
                    "text": "I'm disappointed with the quality.",
                    "expected_emotion": "sadness"
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                response = self.session.post(f"{API_BASE}/ai/emotion-detection", params={
                    "text": test_case["text"]
                })
                
                if response.status_code == 200:
                    data = response.json()
                    emotion = data.get("emotion_analysis", {}).get("primary_emotion", "neutral")
                    intensity = data.get("emotion_analysis", {}).get("intensity", 0.0)
                    
                    success = emotion == test_case["expected_emotion"]
                    
                    self.log_test(f"Emotion Detection {i+1}", success, 
                                f"Detected: '{test_case['text'][:30]}...'", {
                                    "emotion": emotion,
                                    "intensity": intensity,
                                    "sentiment_score": data.get("sentiment_analysis", {}).get("combined_sentiment", {}).get("sentiment_score", 0.0)
                                })
                else:
                    self.log_test(f"Emotion Detection {i+1}", False, f"Failed: {response.text}")
                    
        except Exception as e:
            self.log_test("Emotion Detection", False, f"Error: {str(e)}")

    def test_toxicity_analysis(self):
        """Test toxicity analysis endpoint"""
        try:
            test_cases = [
                {
                    "text": "You are an idiot and I hate your service!",
                    "expected_toxicity": "high"
                },
                {
                    "text": "I'm not happy with this situation.",
                    "expected_toxicity": "low"
                },
                {
                    "text": "This is completely unacceptable and I will sue you!",
                    "expected_toxicity": "medium"
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                response = self.session.post(f"{API_BASE}/ai/toxicity-analysis", params={
                    "text": test_case["text"]
                })
                
                if response.status_code == 200:
                    data = response.json()
                    toxicity_level = data.get("toxicity_analysis", {}).get("abuse_level", "low")
                    toxicity_score = data.get("toxicity_analysis", {}).get("combined_abuse_score", 0.0)
                    requires_escalation = data.get("requires_escalation", False)
                    
                    self.log_test(f"Toxicity Analysis {i+1}", True, 
                                f"Analyzed: '{test_case['text'][:30]}...'", {
                                    "toxicity_level": toxicity_level,
                                    "toxicity_score": toxicity_score,
                                    "requires_escalation": requires_escalation,
                                    "risk_level": data.get("risk_assessment", {}).get("risk_level", "low")
                                })
                else:
                    self.log_test(f"Toxicity Analysis {i+1}", False, f"Failed: {response.text}")
                    
        except Exception as e:
            self.log_test("Toxicity Analysis", False, f"Error: {str(e)}")

    def test_comprehensive_analysis_endpoint(self):
        """Test comprehensive analysis endpoint"""
        try:
            test_text = "I'm extremely angry about the terrible service! This is completely unacceptable and I demand immediate action!"
            
            response = self.session.post(f"{API_BASE}/ai/comprehensive-analysis", params={
                "text": test_text,
                "include_insights": True
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Check all analysis components
                has_text_analysis = "text_analysis" in data
                has_sentiment = "sentiment_analysis" in data
                has_severity = "severity_analysis" in data
                has_emotion = "emotion_analysis" in data
                has_toxicity = "toxicity_analysis" in data
                has_intent = "intent_analysis" in data
                has_risk = "risk_assessment" in data
                has_insights = "insights" in data
                
                success = all([has_text_analysis, has_sentiment, has_severity, has_emotion, 
                             has_toxicity, has_intent, has_risk, has_insights])
                
                self.log_test("Comprehensive Analysis Endpoint", success, 
                            f"Analyzed: '{test_text[:50]}...'", {
                                "sentiment_score": data.get("sentiment_analysis", {}).get("combined_sentiment", {}).get("sentiment_score", 0.0),
                                "severity": data.get("severity_analysis", {}).get("primary_severity", "low"),
                                "emotion": data.get("emotion_analysis", {}).get("primary_emotion", "neutral"),
                                "toxicity_score": data.get("toxicity_analysis", {}).get("combined_abuse_score", 0.0),
                                "risk_level": data.get("risk_assessment", {}).get("risk_level", "low"),
                                "response_priority": data.get("insights", {}).get("response_priority", "normal")
                            })
            else:
                self.log_test("Comprehensive Analysis Endpoint", False, f"Failed: {response.text}")
                
        except Exception as e:
            self.log_test("Comprehensive Analysis Endpoint", False, f"Error: {str(e)}")

    def test_analysis_stats(self):
        """Test analysis statistics endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/ai/analysis-stats")
            
            if response.status_code == 200:
                data = response.json()
                
                has_insights = "learning_insights" in data
                has_metadata = "model_metadata" in data
                has_languages = "supported_languages" in data
                has_models = "ml_models_loaded" in data
                has_history = "analysis_history_count" in data
                
                success = all([has_insights, has_metadata, has_languages, has_models, has_history])
                
                self.log_test("Analysis Stats", success, "Retrieved analysis statistics", {
                    "supported_languages": data.get("supported_languages", 0),
                    "ml_models_loaded": data.get("ml_models_loaded", 0),
                    "analysis_history_count": data.get("analysis_history_count", 0)
                })
            else:
                self.log_test("Analysis Stats", False, f"Failed: {response.text}")
                
        except Exception as e:
            self.log_test("Analysis Stats", False, f"Error: {str(e)}")

    def test_multilingual_sentiment(self):
        """Test sentiment analysis with different languages"""
        try:
            test_cases = [
                {
                    "text": "Estoy muy enojado con el servicio!",
                    "language": "es",
                    "expected_sentiment": "negative"
                },
                {
                    "text": "Je suis très heureux avec le service!",
                    "language": "fr",
                    "expected_sentiment": "positive"
                },
                {
                    "text": "Ich bin sehr enttäuscht von der Qualität.",
                    "language": "de",
                    "expected_sentiment": "negative"
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                response = self.session.post(f"{API_BASE}/ai/sentiment-analysis", params={
                    "text": test_case["text"],
                    "language": test_case["language"]
                })
                
                if response.status_code == 200:
                    data = response.json()
                    sentiment = data.get("sentiment_analysis", {}).get("combined_sentiment", {}).get("sentiment_label", "neutral")
                    
                    success = sentiment == test_case["expected_sentiment"]
                    
                    self.log_test(f"Multilingual Sentiment {i+1}", success, 
                                f"Analyzed {test_case['language']}: '{test_case['text'][:30]}...'", {
                                    "sentiment": sentiment,
                                    "language": data.get("language", test_case["language"])
                                })
                else:
                    self.log_test(f"Multilingual Sentiment {i+1}", False, f"Failed: {response.text}")
                    
        except Exception as e:
            self.log_test("Multilingual Sentiment", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting Smart Sentiment & Severity Analysis Tests")
        
        # Authenticate first
        if not self.authenticate():
            logger.error("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Run all test methods
        test_methods = [
            self.test_comprehensive_text_analysis,
            self.test_sentiment_analysis,
            self.test_severity_assessment,
            self.test_emotion_detection,
            self.test_toxicity_analysis,
            self.test_comprehensive_analysis_endpoint,
            self.test_analysis_stats,
            self.test_multilingual_sentiment
        ]
        
        for test_method in test_methods:
            try:
                test_method()
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                logger.error(f"❌ Test method {test_method.__name__} failed: {str(e)}")
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        logger.info("\n" + "="*60)
        logger.info("📊 SMART SENTIMENT & SEVERITY ANALYSIS TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%")
        
        if failed_tests > 0:
            logger.info("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"  - {result['test_name']}: {result['message']}")
        
        logger.info("\n" + "="*60)
        
        # Save detailed results
        with open("smart_sentiment_analysis_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info("📄 Detailed results saved to: smart_sentiment_analysis_test_results.json")

if __name__ == "__main__":
    tester = SmartSentimentAnalysisTester()
    tester.run_all_tests() 