#!/usr/bin/env python3
"""
Simple Test for Smart Sentiment & Severity Analysis
Tests the core analysis methods without full initialization
"""

import sys
import os
import json
from datetime import datetime
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleSentimentTester:
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

    def test_text_preprocessing(self):
        """Test text preprocessing functionality"""
        try:
            def preprocess_text(text: str) -> str:
                """Preprocess text for analysis"""
                try:
                    # Remove extra whitespace
                    text = re.sub(r'\s+', ' ', text.strip())
                    
                    # Remove special characters but keep punctuation
                    text = re.sub(r'[^\w\s\.\,\!\?\-\'\"]', '', text)
                    
                    # Normalize quotes and apostrophes
                    text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
                    
                    return text
                    
                except Exception as e:
                    logger.error(f"Error preprocessing text: {e}")
                    return text
            
            test_cases = [
                {
                    "input": "  Hello   World!  ",
                    "expected": "Hello World!"
                },
                {
                    "input": "I'm very angry!!!",
                    "expected": "I'm very angry!!!"
                },
                {
                    "input": "This is a test with special chars: @#$%",
                    "expected": "This is a test with special chars"
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                result = preprocess_text(test_case["input"])
                success = result == test_case["expected"]
                
                self.log_test(f"Text Preprocessing {i+1}", success, 
                            f"Input: '{test_case['input']}' -> Output: '{result}'", {
                                "input": test_case["input"],
                                "expected": test_case["expected"],
                                "actual": result
                            })
                    
        except Exception as e:
            self.log_test("Text Preprocessing", False, f"Error: {str(e)}")

    def test_rule_based_sentiment(self):
        """Test rule-based sentiment analysis"""
        try:
            def analyze_sentiment_rules(text: str) -> dict:
                """Rule-based sentiment analysis"""
                try:
                    # Positive words and phrases
                    positive_patterns = [
                        r'\b(good|great|excellent|amazing|wonderful|fantastic|perfect|awesome|outstanding|superb)\b',
                        r'\b(happy|pleased|satisfied|content|delighted|thrilled|excited|joyful)\b',
                        r'\b(thank|thanks|appreciate|grateful|blessed|fortunate)\b',
                        r'\b(love|like|enjoy|adore|cherish|treasure)\b',
                        r'\b(helpful|useful|beneficial|valuable|worthwhile|productive)\b'
                    ]
                    
                    # Negative words and phrases
                    negative_patterns = [
                        r'\b(bad|terrible|awful|horrible|dreadful|atrocious|abysmal|appalling)\b',
                        r'\b(angry|furious|mad|irritated|annoyed|frustrated|upset|disappointed)\b',
                        r'\b(hate|dislike|loathe|despise|abhor|detest)\b',
                        r'\b(useless|worthless|pointless|meaningless|futile|hopeless)\b',
                        r'\b(pain|suffering|agony|misery|distress|anguish)\b'
                    ]
                    
                    # Intensifiers
                    intensifiers = [
                        r'\b(very|extremely|absolutely|completely|totally|utterly|entirely)\b',
                        r'\b(really|truly|genuinely|sincerely|honestly)\b'
                    ]
                    
                    text_lower = text.lower()
                    
                    # Count positive and negative matches
                    positive_count = sum(len(re.findall(pattern, text_lower)) for pattern in positive_patterns)
                    negative_count = sum(len(re.findall(pattern, text_lower)) for pattern in negative_patterns)
                    intensifier_count = sum(len(re.findall(pattern, text_lower)) for pattern in intensifiers)
                    
                    # Calculate sentiment score
                    total_words = len(text.split())
                    if total_words == 0:
                        return {"sentiment_score": 0.0, "polarity": "neutral", "method": "rules"}
                    
                    # Base sentiment
                    if positive_count > negative_count:
                        base_score = positive_count / total_words
                    elif negative_count > positive_count:
                        base_score = -negative_count / total_words
                    else:
                        base_score = 0.0
                    
                    # Apply intensifier multiplier
                    intensifier_multiplier = 1.0 + (intensifier_count * 0.2)
                    final_score = max(-1.0, min(1.0, base_score * intensifier_multiplier))
                    
                    # Determine polarity
                    if final_score >= 0.1:
                        polarity = "positive"
                    elif final_score <= -0.1:
                        polarity = "negative"
                    else:
                        polarity = "neutral"
                    
                    return {
                        "sentiment_score": final_score,
                        "polarity": polarity,
                        "positive_count": positive_count,
                        "negative_count": negative_count,
                        "intensifier_count": intensifier_count,
                        "method": "rules"
                    }
                    
                except Exception as e:
                    logger.error(f"Error in rule-based sentiment analysis: {e}")
                    return {"sentiment_score": 0.0, "polarity": "neutral", "method": "error"}
            
            test_cases = [
                {
                    "text": "I'm very happy with the service!",
                    "expected_polarity": "positive"
                },
                {
                    "text": "I'm extremely angry about this issue!",
                    "expected_polarity": "negative"
                },
                {
                    "text": "This is just a normal question.",
                    "expected_polarity": "neutral"
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                result = analyze_sentiment_rules(test_case["text"])
                success = result["polarity"] == test_case["expected_polarity"]
                
                self.log_test(f"Rule-based Sentiment {i+1}", success, 
                            f"Analyzed: '{test_case['text'][:30]}...'", {
                                "sentiment_score": result["sentiment_score"],
                                "polarity": result["polarity"],
                                "positive_count": result["positive_count"],
                                "negative_count": result["negative_count"]
                            })
                    
        except Exception as e:
            self.log_test("Rule-based Sentiment", False, f"Error: {str(e)}")

    def test_severity_assessment(self):
        """Test severity assessment"""
        try:
            def assess_severity(text: str, sentiment_score: float) -> dict:
                """Assess severity of the issue"""
                try:
                    # Severity indicators
                    severity_indicators = {
                        "critical": [
                            r'\b(emergency|urgent|critical|immediate|asap|right now)\b',
                            r'\b(dangerous|hazardous|unsafe|risky|life-threatening)\b',
                            r'\b(legal|lawyer|attorney|sue|lawsuit|court)\b',
                            r'\b(ceo|president|executive|management|escalate)\b',
                            r'\b(media|press|journalist|reporter|news|social media)\b'
                        ],
                        "high": [
                            r'\b(very angry|extremely upset|furious|livid|outraged)\b',
                            r'\b(unacceptable|intolerable|unbearable|insufferable)\b',
                            r'\b(never|ever again|boycott|cancel|terminate)\b',
                            r'\b(complaint|formal complaint|official complaint)\b'
                        ],
                        "medium": [
                            r'\b(disappointed|frustrated|annoyed|bothered)\b',
                            r'\b(problem|issue|concern|matter)\b',
                            r'\b(help|assist|support|resolve)\b'
                        ],
                        "low": [
                            r'\b(suggestion|feedback|improvement|enhancement)\b',
                            r'\b(question|inquiry|information|details)\b',
                            r'\b(thank|appreciate|grateful|satisfied)\b'
                        ]
                    }
                    
                    text_lower = text.lower()
                    severity_scores = {}
                    
                    # Calculate severity scores for each level
                    for level, patterns in severity_indicators.items():
                        score = sum(len(re.findall(pattern, text_lower)) for pattern in patterns)
                        severity_scores[level] = score
                    
                    # Determine primary severity level
                    max_score = max(severity_scores.values())
                    primary_severity = "low"  # default
                    
                    if max_score > 0:
                        for level in ["critical", "high", "medium", "low"]:
                            if severity_scores[level] == max_score:
                                primary_severity = level
                                break
                    
                    # Adjust severity based on sentiment
                    if sentiment_score < -0.5 and primary_severity == "low":
                        primary_severity = "medium"
                    elif sentiment_score < -0.8 and primary_severity in ["low", "medium"]:
                        primary_severity = "high"
                    
                    # Calculate confidence
                    total_indicators = sum(severity_scores.values())
                    confidence = min(1.0, total_indicators / 10.0) if total_indicators > 0 else 0.5
                    
                    return {
                        "primary_severity": primary_severity,
                        "severity_scores": severity_scores,
                        "confidence": confidence,
                        "sentiment_influence": abs(sentiment_score)
                    }
                    
                except Exception as e:
                    logger.error(f"Error assessing severity: {e}")
                    return {
                        "primary_severity": "medium",
                        "severity_scores": {"low": 0, "medium": 1, "high": 0, "critical": 0},
                        "confidence": 0.5,
                        "sentiment_influence": 0.0
                    }
            
            test_cases = [
                {
                    "text": "This is an emergency!",
                    "sentiment_score": -0.8,
                    "expected_severity": "critical"
                },
                {
                    "text": "I'm very angry about this issue!",
                    "sentiment_score": -0.7,
                    "expected_severity": "high"
                },
                {
                    "text": "I have a problem with my order.",
                    "sentiment_score": -0.3,
                    "expected_severity": "medium"
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                result = assess_severity(test_case["text"], test_case["sentiment_score"])
                success = result["primary_severity"] == test_case["expected_severity"]
                
                self.log_test(f"Severity Assessment {i+1}", success, 
                            f"Assessed: '{test_case['text'][:30]}...'", {
                                "severity": result["primary_severity"],
                                "confidence": result["confidence"],
                                "sentiment_influence": result["sentiment_influence"]
                            })
                    
        except Exception as e:
            self.log_test("Severity Assessment", False, f"Error: {str(e)}")

    def test_emotion_detection(self):
        """Test emotion detection"""
        try:
            def detect_emotions(text: str) -> dict:
                """Detect emotions in the text"""
                try:
                    # Emotion patterns
                    emotion_patterns = {
                        "anger": [
                            r'\b(angry|furious|livid|irate|enraged|outraged|mad|fuming)\b',
                            r'\b(rage|wrath|temper|outburst|explosion)\b'
                        ],
                        "frustration": [
                            r'\b(frustrated|annoyed|irritated|bothered|aggravated)\b',
                            r'\b(fed up|sick of|tired of|had enough)\b'
                        ],
                        "sadness": [
                            r'\b(sad|depressed|upset|disappointed|heartbroken|devastated)\b',
                            r'\b(crying|tears|sorrow|grief|melancholy)\b'
                        ],
                        "fear": [
                            r'\b(scared|afraid|frightened|terrified|panicked|worried)\b',
                            r'\b(anxiety|stress|nervous|concerned|apprehensive)\b'
                        ],
                        "joy": [
                            r'\b(happy|joyful|delighted|thrilled|excited|elated)\b',
                            r'\b(pleased|satisfied|content|grateful|blessed)\b'
                        ],
                        "surprise": [
                            r'\b(surprised|shocked|amazed|astonished|stunned)\b',
                            r'\b(unexpected|unbelievable|incredible|wow)\b'
                        ],
                        "disgust": [
                            r'\b(disgusted|revolted|appalled|sickened|repulsed)\b',
                            r'\b(gross|nasty|vile|repulsive|offensive)\b'
                        ]
                    }
                    
                    text_lower = text.lower()
                    emotion_scores = {}
                    
                    # Calculate emotion scores
                    for emotion, patterns in emotion_patterns.items():
                        score = sum(len(re.findall(pattern, text_lower)) for pattern in patterns)
                        emotion_scores[emotion] = score
                    
                    # Find primary emotion
                    max_score = max(emotion_scores.values())
                    primary_emotion = "neutral"
                    
                    if max_score > 0:
                        for emotion, score in emotion_scores.items():
                            if score == max_score:
                                primary_emotion = emotion
                                break
                    
                    # Calculate emotion intensity
                    total_emotion_words = sum(emotion_scores.values())
                    intensity = min(1.0, total_emotion_words / 5.0) if total_emotion_words > 0 else 0.0
                    
                    return {
                        "primary_emotion": primary_emotion,
                        "emotion_scores": emotion_scores,
                        "intensity": intensity,
                        "emotion_confidence": min(1.0, total_emotion_words / 3.0) if total_emotion_words > 0 else 0.5
                    }
                    
                except Exception as e:
                    logger.error(f"Error detecting emotions: {e}")
                    return {
                        "primary_emotion": "neutral",
                        "emotion_scores": {},
                        "intensity": 0.0,
                        "emotion_confidence": 0.5
                    }
            
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
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                result = detect_emotions(test_case["text"])
                success = result["primary_emotion"] == test_case["expected_emotion"]
                
                self.log_test(f"Emotion Detection {i+1}", success, 
                            f"Detected: '{test_case['text'][:30]}...'", {
                                "emotion": result["primary_emotion"],
                                "intensity": result["intensity"],
                                "confidence": result["emotion_confidence"]
                            })
                    
        except Exception as e:
            self.log_test("Emotion Detection", False, f"Error: {str(e)}")

    def test_toxicity_analysis(self):
        """Test toxicity analysis"""
        try:
            def analyze_toxicity(text: str) -> dict:
                """Analyze toxicity and abuse in text"""
                try:
                    # Enhanced toxic patterns
                    toxic_patterns = [
                        r'\b(abuse|abusive)\b',
                        r'\b(hate|hatred)\b',
                        r'\b(violent|violence)\b',
                        r'\b(threat|threatening)\b',
                        r'\b(insult|insulting)\b',
                        r'\b(profanity|curse|swear)\b',
                        r'\b(racist|racism)\b',
                        r'\b(sexist|sexism)\b',
                        r'\b(discriminat|discrimination)\b',
                        r'\b(harass|harassment)\b'
                    ]
                    
                    # Additional abuse patterns
                    abuse_patterns = {
                        "verbal_abuse": [
                            r'\b(idiot|stupid|dumb|moron|fool|imbecile)\b',
                            r'\b(worthless|useless|pathetic|incompetent)\b'
                        ],
                        "threats": [
                            r'\b(kill|murder|attack|harm|hurt|destroy)\b',
                            r'\b(sue|legal|court|lawyer|attorney)\b',
                            r'\b(fire|terminate|dismiss|remove)\b'
                        ],
                        "discrimination": [
                            r'\b(racist|sexist|homophobic|transphobic)\b',
                            r'\b(discriminat|bias|prejudice|stereotype)\b'
                        ],
                        "harassment": [
                            r'\b(harass|stalk|bully|intimidate|threaten)\b',
                            r'\b(unwanted|unwelcome|inappropriate|offensive)\b'
                        ]
                    }
                    
                    text_lower = text.lower()
                    
                    # Calculate toxicity score
                    toxicity_count = 0
                    for pattern in toxic_patterns:
                        if re.search(pattern, text_lower):
                            toxicity_count += 1
                    
                    # Normalize score
                    max_patterns = len(toxic_patterns)
                    toxicity_score = min(toxicity_count / max_patterns, 1.0)
                    
                    # Calculate abuse scores
                    abuse_scores = {}
                    for abuse_type, patterns in abuse_patterns.items():
                        score = sum(len(re.findall(pattern, text_lower)) for pattern in patterns)
                        abuse_scores[abuse_type] = score
                    
                    # Overall abuse score
                    total_abuse_score = sum(abuse_scores.values()) / len(abuse_scores) if abuse_scores else 0.0
                    total_abuse_score = min(1.0, total_abuse_score)
                    
                    # Combine with toxicity score
                    combined_abuse_score = max(toxicity_score, total_abuse_score)
                    
                    # Determine abuse level
                    if combined_abuse_score >= 0.7:
                        abuse_level = "high"
                    elif combined_abuse_score >= 0.4:
                        abuse_level = "medium"
                    else:
                        abuse_level = "low"
                    
                    return {
                        "toxicity_score": toxicity_score,
                        "abuse_scores": abuse_scores,
                        "combined_abuse_score": combined_abuse_score,
                        "abuse_level": abuse_level,
                        "abuse_types": [k for k, v in abuse_scores.items() if v > 0],
                        "requires_escalation": combined_abuse_score >= 0.6
                    }
                    
                except Exception as e:
                    logger.error(f"Error analyzing toxicity: {e}")
                    return {
                        "toxicity_score": 0.0,
                        "abuse_scores": {},
                        "combined_abuse_score": 0.0,
                        "abuse_level": "low",
                        "abuse_types": [],
                        "requires_escalation": False
                    }
            
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
                result = analyze_toxicity(test_case["text"])
                success = result["abuse_level"] == test_case["expected_toxicity"]
                
                self.log_test(f"Toxicity Analysis {i+1}", success, 
                            f"Analyzed: '{test_case['text'][:30]}...'", {
                                "toxicity_score": result["toxicity_score"],
                                "abuse_level": result["abuse_level"],
                                "requires_escalation": result["requires_escalation"]
                            })
                    
        except Exception as e:
            self.log_test("Toxicity Analysis", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting Simple Smart Sentiment & Severity Analysis Tests")
        
        # Run all test methods
        test_methods = [
            self.test_text_preprocessing,
            self.test_rule_based_sentiment,
            self.test_severity_assessment,
            self.test_emotion_detection,
            self.test_toxicity_analysis
        ]
        
        for test_method in test_methods:
            try:
                test_method()
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
        logger.info("📊 SIMPLE SMART SENTIMENT & SEVERITY ANALYSIS TEST SUMMARY")
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
        with open("simple_sentiment_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info("📄 Detailed results saved to: simple_sentiment_test_results.json")

if __name__ == "__main__":
    tester = SimpleSentimentTester()
    tester.run_all_tests() 