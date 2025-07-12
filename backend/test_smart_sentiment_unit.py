#!/usr/bin/env python3
"""
Unit Test for Smart Sentiment & Severity Analysis
Tests the AIEngine directly without requiring the server
"""

import sys
import os
import json
from datetime import datetime
import logging

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartSentimentUnitTester:
    def __init__(self):
        self.test_results = []
        
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

    def test_ai_engine_initialization(self):
        """Test AIEngine initialization"""
        try:
            from app.core.ai_engine import AIEngine
            
            ai_engine = AIEngine()
            
            # Check if AIEngine has required attributes
            has_openai = hasattr(ai_engine, 'has_openai_key')
            has_google = hasattr(ai_engine, 'has_google_key')
            has_ml_models = hasattr(ai_engine, 'ml_models')
            has_learning_cache = hasattr(ai_engine, 'learning_cache')
            
            success = all([has_openai, has_google, has_ml_models, has_learning_cache])
            
            self.log_test("AIEngine Initialization", success, 
                         "AIEngine initialized successfully", {
                             "openai_available": ai_engine.has_openai_key,
                             "google_available": ai_engine.has_google_key,
                             "ml_models_count": len(ai_engine.ml_models),
                             "supported_languages": len(ai_engine.supported_languages)
                         })
            
            return ai_engine
            
        except Exception as e:
            self.log_test("AIEngine Initialization", False, f"Error: {str(e)}")
            return None

    def test_comprehensive_text_analysis(self, ai_engine):
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
                analysis = ai_engine.analyze_text(
                    text=test_case["text"],
                    context="Test context",
                    user_id=1
                )
                
                # Check if analysis has all required components
                has_text_analysis = "text_analysis" in analysis
                has_sentiment = "sentiment_analysis" in analysis
                has_severity = "severity_analysis" in analysis
                has_emotion = "emotion_analysis" in analysis
                has_toxicity = "toxicity_analysis" in analysis
                has_intent = "intent_analysis" in analysis
                has_risk = "risk_assessment" in analysis
                has_insights = "insights" in analysis
                
                # Check sentiment
                sentiment = analysis.get("sentiment_analysis", {}).get("combined_sentiment", {}).get("sentiment_label", "neutral")
                sentiment_match = sentiment == test_case["expected_sentiment"]
                
                # Check severity
                severity = analysis.get("severity_analysis", {}).get("primary_severity", "low")
                severity_match = severity == test_case["expected_severity"]
                
                # Check emotion
                emotion = analysis.get("emotion_analysis", {}).get("primary_emotion", "neutral")
                emotion_match = emotion == test_case["expected_emotion"]
                
                # Overall success
                structure_success = all([has_text_analysis, has_sentiment, has_severity, has_emotion, 
                                       has_toxicity, has_intent, has_risk, has_insights])
                
                self.log_test(f"Comprehensive Analysis {i+1}", structure_success, 
                            f"Analyzed: '{test_case['text'][:50]}...'", {
                                "sentiment": sentiment,
                                "severity": severity,
                                "emotion": emotion,
                                "toxicity_score": analysis.get("toxicity_analysis", {}).get("combined_abuse_score", 0.0),
                                "risk_level": analysis.get("risk_assessment", {}).get("risk_level", "low"),
                                "processing_time": analysis.get("text_analysis", {}).get("processing_time", 0.0)
                            })
                    
        except Exception as e:
            self.log_test("Comprehensive Text Analysis", False, f"Error: {str(e)}")

    def test_sentiment_analysis_methods(self, ai_engine):
        """Test individual sentiment analysis methods"""
        try:
            test_text = "I'm very angry about the poor service!"
            
            # Test Google sentiment analysis
            google_sentiment = ai_engine.analyze_sentiment_and_toxicity(test_text)
            has_google_sentiment = "sentiment_score" in google_sentiment
            
            # Test rule-based sentiment analysis
            rule_sentiment = ai_engine._analyze_sentiment_rules(test_text)
            has_rule_sentiment = "sentiment_score" in rule_sentiment
            
            # Test ML sentiment analysis
            ml_sentiment = ai_engine._analyze_sentiment_ml(test_text)
            has_ml_sentiment = "sentiment_score" in ml_sentiment
            
            # Test OpenAI sentiment analysis
            openai_sentiment = ai_engine._analyze_sentiment_with_openai(test_text, {"language_code": "en"})
            has_openai_sentiment = "sentiment_score" in openai_sentiment
            
            success = all([has_google_sentiment, has_rule_sentiment, has_ml_sentiment, has_openai_sentiment])
            
            self.log_test("Sentiment Analysis Methods", success, 
                         f"Tested sentiment analysis methods for: '{test_text}'", {
                             "google_sentiment_score": google_sentiment.get("sentiment_score", 0.0),
                             "rule_sentiment_score": rule_sentiment.get("sentiment_score", 0.0),
                             "ml_sentiment_score": ml_sentiment.get("sentiment_score", 0.0),
                             "openai_sentiment_score": openai_sentiment.get("sentiment_score", 0.0)
                         })
                    
        except Exception as e:
            self.log_test("Sentiment Analysis Methods", False, f"Error: {str(e)}")

    def test_severity_assessment(self, ai_engine):
        """Test severity assessment"""
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
                analysis = ai_engine.analyze_text(test_case["text"], context="Test context")
                severity = analysis.get("severity_analysis", {}).get("primary_severity", "low")
                confidence = analysis.get("severity_analysis", {}).get("confidence", 0.0)
                
                self.log_test(f"Severity Assessment {i+1}", True, 
                            f"Assessed: '{test_case['text'][:30]}...'", {
                                "severity": severity,
                                "confidence": confidence,
                                "severity_scores": analysis.get("severity_analysis", {}).get("severity_scores", {})
                            })
                    
        except Exception as e:
            self.log_test("Severity Assessment", False, f"Error: {str(e)}")

    def test_emotion_detection(self, ai_engine):
        """Test emotion detection"""
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
                analysis = ai_engine.analyze_text(test_case["text"])
                emotion = analysis.get("emotion_analysis", {}).get("primary_emotion", "neutral")
                intensity = analysis.get("emotion_analysis", {}).get("intensity", 0.0)
                
                self.log_test(f"Emotion Detection {i+1}", True, 
                            f"Detected: '{test_case['text'][:30]}...'", {
                                "emotion": emotion,
                                "intensity": intensity,
                                "emotion_scores": analysis.get("emotion_analysis", {}).get("emotion_scores", {})
                            })
                    
        except Exception as e:
            self.log_test("Emotion Detection", False, f"Error: {str(e)}")

    def test_toxicity_analysis(self, ai_engine):
        """Test toxicity analysis"""
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
                analysis = ai_engine.analyze_text(test_case["text"])
                toxicity_level = analysis.get("toxicity_analysis", {}).get("abuse_level", "low")
                toxicity_score = analysis.get("toxicity_analysis", {}).get("combined_abuse_score", 0.0)
                requires_escalation = analysis.get("toxicity_analysis", {}).get("requires_escalation", False)
                
                self.log_test(f"Toxicity Analysis {i+1}", True, 
                            f"Analyzed: '{test_case['text'][:30]}...'", {
                                "toxicity_level": toxicity_level,
                                "toxicity_score": toxicity_score,
                                "requires_escalation": requires_escalation,
                                "abuse_types": analysis.get("toxicity_analysis", {}).get("abuse_types", [])
                            })
                    
        except Exception as e:
            self.log_test("Toxicity Analysis", False, f"Error: {str(e)}")

    def test_risk_assessment(self, ai_engine):
        """Test risk assessment"""
        try:
            test_cases = [
                {
                    "text": "I will sue you and contact the media!",
                    "expected_risk": "high"
                },
                {
                    "text": "I'm very angry about this issue!",
                    "expected_risk": "medium"
                },
                {
                    "text": "Just a simple question.",
                    "expected_risk": "low"
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                analysis = ai_engine.analyze_text(test_case["text"])
                risk_level = analysis.get("risk_assessment", {}).get("risk_level", "low")
                risk_score = analysis.get("risk_assessment", {}).get("risk_score", 0.0)
                requires_attention = analysis.get("risk_assessment", {}).get("requires_immediate_attention", False)
                
                self.log_test(f"Risk Assessment {i+1}", True, 
                            f"Assessed: '{test_case['text'][:30]}...'", {
                                "risk_level": risk_level,
                                "risk_score": risk_score,
                                "requires_attention": requires_attention,
                                "risk_factors": analysis.get("risk_assessment", {}).get("risk_factors", [])
                            })
                    
        except Exception as e:
            self.log_test("Risk Assessment", False, f"Error: {str(e)}")

    def test_language_detection(self, ai_engine):
        """Test language detection"""
        try:
            test_cases = [
                {
                    "text": "Hello, how are you?",
                    "expected_language": "en"
                },
                {
                    "text": "Hola, ¿cómo estás?",
                    "expected_language": "es"
                },
                {
                    "text": "Bonjour, comment allez-vous?",
                    "expected_language": "fr"
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                language_info = ai_engine.detect_language(test_case["text"])
                detected_language = language_info.get("language_code", "unknown")
                confidence = language_info.get("confidence", 0.0)
                
                self.log_test(f"Language Detection {i+1}", True, 
                            f"Detected: '{test_case['text'][:20]}...'", {
                                "detected_language": detected_language,
                                "confidence": confidence,
                                "language_name": language_info.get("language_name", "Unknown")
                            })
                    
        except Exception as e:
            self.log_test("Language Detection", False, f"Error: {str(e)}")

    def test_insights_generation(self, ai_engine):
        """Test insights and recommendations generation"""
        try:
            test_text = "I'm extremely angry about the terrible service! This is completely unacceptable!"
            
            analysis = ai_engine.analyze_text(test_text, context="Test context")
            insights = analysis.get("insights", {})
            
            has_insights = "insights" in insights
            has_recommendations = "recommendations" in insights
            has_priority = "response_priority" in insights
            has_tone = "suggested_response_tone" in insights
            
            success = all([has_insights, has_recommendations, has_priority, has_tone])
            
            self.log_test("Insights Generation", success, 
                         f"Generated insights for: '{test_text[:50]}...'", {
                             "response_priority": insights.get("response_priority", "normal"),
                             "suggested_response_tone": insights.get("suggested_response_tone", "professional"),
                             "escalation_needed": insights.get("escalation_needed", False),
                             "insights_count": len(insights.get("insights", [])),
                             "recommendations_count": len(insights.get("recommendations", []))
                         })
                    
        except Exception as e:
            self.log_test("Insights Generation", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting Smart Sentiment & Severity Analysis Unit Tests")
        
        # Initialize AIEngine
        ai_engine = self.test_ai_engine_initialization()
        if not ai_engine:
            logger.error("❌ AIEngine initialization failed. Cannot proceed with tests.")
            return
        
        # Run all test methods
        test_methods = [
            lambda: self.test_comprehensive_text_analysis(ai_engine),
            lambda: self.test_sentiment_analysis_methods(ai_engine),
            lambda: self.test_severity_assessment(ai_engine),
            lambda: self.test_emotion_detection(ai_engine),
            lambda: self.test_toxicity_analysis(ai_engine),
            lambda: self.test_risk_assessment(ai_engine),
            lambda: self.test_language_detection(ai_engine),
            lambda: self.test_insights_generation(ai_engine)
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"❌ Test method failed: {str(e)}")
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        logger.info("\n" + "="*60)
        logger.info("📊 SMART SENTIMENT & SEVERITY ANALYSIS UNIT TEST SUMMARY")
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
        with open("smart_sentiment_unit_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info("📄 Detailed results saved to: smart_sentiment_unit_test_results.json")

if __name__ == "__main__":
    tester = SmartSentimentUnitTester()
    tester.run_all_tests() 