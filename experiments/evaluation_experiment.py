import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd

sys.path.append('src')
from llm.chatbot import ChatBot

class ChatbotEvaluator:
    def __init__(self):
        self.chatbot = ChatBot(session_id="evaluation")
        self.results = []
        self.start_time = None
        
    def run_comprehensive_evaluation(self):
        """Run complete chatbot evaluation experiment"""
        print("CHATBOT EFFECTIVENESS EVALUATION EXPERIMENT")
        print("=" * 60)
        
        # Define test scenarios
        test_scenarios = self._define_test_scenarios()
        
        print(f"Testing {len(test_scenarios)} scenarios...")
        print("=" * 60)
        
        # Run each test scenario
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n Test {i}/{len(test_scenarios)}: {scenario['name']}")
            result = self._evaluate_scenario(scenario)
            self.results.append(result)
            
            # Print immediate feedback
            self._print_scenario_result(result)
        
        # Generate comprehensive report
        self._generate_report()
        
    def _define_test_scenarios(self) -> List[Dict]:
        """Define comprehensive test scenarios"""
        return [
            # 🔹 BASIC FUNCTION CALLING TESTS
            {
                "name": "Basic Order Tracking",
                "category": "function_calling",
                "user_input": "Track my orders for john@example.com",
                "expected_function": "orderTracking",
                "expected_params": {"email": "john@example.com"},
                "success_criteria": {
                    "makes_function_call": True,
                    "correct_function": True,
                    "correct_params": True,
                    "natural_response": True
                }
            },
            {
                "name": "Specific Order Status",
                "category": "function_calling",
                "user_input": "What is the status of order ORD001 for john@example.com?",
                "expected_function": "orderTracking",
                "expected_params": {"email": "john@example.com", "order_id": "ORD001"},
                "success_criteria": {
                    "makes_function_call": True,
                    "correct_function": True,
                    "correct_params": True,
                    "natural_response": True
                }
            },
            {
                "name": "Order Cancellation",
                "category": "function_calling",
                "user_input": "Cancel order ORD003 for jane@example.com",
                "expected_function": "orderCancellation",
                "expected_params": {"email": "jane@example.com", "order_id": "ORD003"},
                "success_criteria": {
                    "makes_function_call": True,
                    "correct_function": True,
                    "correct_params": True,
                    "natural_response": True
                }
            },
            
            # 🔹 PARAMETER EXTRACTION TESTS
            {
                "name": "Email Extraction Variation 1",
                "category": "parameter_extraction",
                "user_input": "I want to check my orders, my email is john@example.com",
                "expected_function": "orderTracking",
                "expected_params": {"email": "john@example.com"},
                "success_criteria": {
                    "makes_function_call": True,
                    "correct_params": True
                }
            },
            {
                "name": "Order ID Extraction",
                "category": "parameter_extraction",
                "user_input": "Please cancel ORD002 for john@example.com",
                "expected_function": "orderCancellation",
                "expected_params": {"email": "john@example.com", "order_id": "ORD002"},
                "success_criteria": {
                    "makes_function_call": True,
                    "correct_params": True
                }
            },
            
            # 🔹 MISSING INFORMATION HANDLING
            {
                "name": "Missing Email",
                "category": "error_handling",
                "user_input": "Track my orders",
                "expected_function": None,
                "expected_params": None,
                "success_criteria": {
                    "makes_function_call": False,
                    "asks_for_email": True,
                    "helpful_response": True
                }
            },
            {
                "name": "Missing Order ID for Cancellation",
                "category": "error_handling",
                "user_input": "Cancel my order for john@example.com",
                "expected_function": None,
                "expected_params": None,
                "success_criteria": {
                    "makes_function_call": False,
                    "asks_for_order_id": True,
                    "helpful_response": True
                }
            },
            
            # 🔹 BUSINESS LOGIC TESTS
            {
                "name": "Failed Cancellation (Too Old)",
                "category": "business_logic",
                "user_input": "Cancel order ORD002 for john@example.com",
                "expected_function": "orderCancellation",
                "expected_params": {"email": "john@example.com", "order_id": "ORD002"},
                "success_criteria": {
                    "makes_function_call": True,
                    "explains_failure_reason": True,
                    "mentions_policy": True,
                    "offers_alternative": True
                }
            },
            
            # 🔹 CONVERSATION FLOW TESTS
            {
                "name": "Multi-Turn Context",
                "category": "conversation_flow",
                "conversation": [
                    {"user": "Track my orders for john@example.com", "expected_function": "orderTracking"},
                    {"user": "Cancel ORD002", "expected_function": "orderCancellation"}
                ],
                "success_criteria": {
                    "maintains_context": True,
                    "uses_previous_email": True
                }
            },
            
            # 🔹 EDGE CASES
            {
                "name": "Invalid Email",
                "category": "edge_cases",
                "user_input": "Track orders for invalid-email",
                "expected_function": None,
                "success_criteria": {
                    "handles_gracefully": True,
                    "asks_for_valid_email": True
                }
            },
            {
                "name": "Non-existent Customer",
                "category": "edge_cases",
                "user_input": "Track orders for nonexistent@test.com",
                "expected_function": "orderTracking",
                "expected_params": {"email": "nonexistent@test.com"},
                "success_criteria": {
                    "makes_function_call": True,
                    "handles_not_found": True,
                    "helpful_error_message": True
                }
            }
        ]
    
    def _evaluate_scenario(self, scenario: Dict) -> Dict:
        """Evaluate a single test scenario"""
        start_time = time.time()
        
        result = {
            "name": scenario["name"],
            "category": scenario["category"],
            "user_input": scenario.get("user_input", ""),
            "timestamp": datetime.now().isoformat(),
            "response_time": 0,
            "success_score": 0,
            "details": {}
        }
        
        try:
            if "conversation" in scenario:
                # Multi-turn conversation test
                result.update(self._evaluate_conversation(scenario))
            else:
                # Single-turn test
                result.update(self._evaluate_single_turn(scenario))
            
            result["response_time"] = time.time() - start_time
            result["success_score"] = self._calculate_success_score(result, scenario)
            
        except Exception as e:
            result["error"] = str(e)
            result["success_score"] = 0
        
        return result
    
    def _evaluate_single_turn(self, scenario: Dict) -> Dict:
        """Evaluate single-turn conversation"""
        user_input = scenario["user_input"]
        conversation_history = []
        
        # Get chatbot response
        response, updated_history = self.chatbot.chat(user_input, conversation_history)
        
        # Analyze the decision-making process
        analysis = self._analyze_decision_process(updated_history, scenario)
        
        return {
            "bot_response": response,
            "conversation_history": updated_history,
            "analysis": analysis
        }
    
    def _evaluate_conversation(self, scenario: Dict) -> Dict:
        """Evaluate multi-turn conversation"""
        conversation_history = []
        responses = []
        
        for turn in scenario["conversation"]:
            user_input = turn["user"]
            response, conversation_history = self.chatbot.chat(user_input, conversation_history)
            responses.append({
                "user": user_input,
                "bot": response,
                "expected_function": turn.get("expected_function")
            })
        
        analysis = self._analyze_conversation_flow(conversation_history, scenario)
        
        return {
            "responses": responses,
            "conversation_history": conversation_history,
            "analysis": analysis
        }
    
    def _analyze_decision_process(self, conversation_history: List[Dict], scenario: Dict) -> Dict:
        """Analyze the chatbot's decision-making process"""
        analysis = {
            "made_function_call": False,
            "function_name": None,
            "extracted_params": {},
            "response_quality": "unknown",
            "followed_business_logic": "unknown"
        }
        
        # Check for function calls in conversation history
        function_calls = []
        for msg in conversation_history:
            if msg["role"] == "system" and "Function" in msg["content"]:
                # Parse function execution
                try:
                    parts = msg["content"].split(" ")
                    func_name = parts[1] if len(parts) > 1 else "unknown"
                    json_start = msg["content"].find("{")
                    if json_start != -1:
                        result_json = json.loads(msg["content"][json_start:])
                        function_calls.append({
                            "function": func_name,
                            "result": result_json
                        })
                except:
                    pass
        
        if function_calls:
            analysis["made_function_call"] = True
            analysis["function_name"] = function_calls[0]["function"]
            analysis["function_result"] = function_calls[0]["result"]
        
        # Analyze response quality
        final_response = conversation_history[-1]["content"] if conversation_history else ""
        analysis["response_quality"] = self._assess_response_quality(final_response, scenario)
        
        return analysis
    
    def _analyze_conversation_flow(self, conversation_history: List[Dict], scenario: Dict) -> Dict:
        """Analyze multi-turn conversation flow"""
        return {
            "maintained_context": self._check_context_maintenance(conversation_history),
            "appropriate_responses": self._check_response_appropriateness(conversation_history)
        }
    
    def _assess_response_quality(self, response: str, scenario: Dict) -> Dict:
        """Assess the quality of the chatbot response"""
        quality_metrics = {
            "is_natural": not any(phrase in response.lower() for phrase in ["function_call:", "{", "}", "system:"]),
            "is_helpful": len(response) > 20 and any(word in response.lower() for word in ["help", "found", "cancel", "track"]),
            "is_accurate": True,  # This would need more sophisticated checking
            "follows_policy": "policy" in response.lower() or "return" in response.lower() if "cannot" in response.lower() else True
        }
        
        return quality_metrics
    
    def _calculate_success_score(self, result: Dict, scenario: Dict) -> float:
        """Calculate overall success score (0-100)"""
        criteria = scenario.get("success_criteria", {})
        score = 0
        total_criteria = len(criteria)
        
        if total_criteria == 0:
            return 50  # Default score if no criteria
        
        analysis = result.get("analysis", {})
        
        # Check each success criterion
        for criterion, expected in criteria.items():
            if criterion == "makes_function_call":
                if analysis.get("made_function_call") == expected:
                    score += 1
            elif criterion == "correct_function":
                if analysis.get("function_name") == scenario.get("expected_function"):
                    score += 1
            elif criterion == "natural_response":
                quality = analysis.get("response_quality", {})
                if isinstance(quality, dict) and quality.get("is_natural", False):
                    score += 1
            elif criterion == "helpful_response":
                quality = analysis.get("response_quality", {})
                if isinstance(quality, dict) and quality.get("is_helpful", False):
                    score += 1
            # Add more criteria checks as needed
        
        return (score / total_criteria) * 100
    
    def _check_context_maintenance(self, conversation_history: List[Dict]) -> bool:
        """Check if context is maintained across turns"""
        # Look for email reuse across turns
        emails = []
        for msg in conversation_history:
            if msg["role"] == "user":
                import re
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', msg["content"])
                if email_match:
                    emails.append(email_match.group())
        
        return len(set(emails)) <= 1 if emails else True
    
    def _check_response_appropriateness(self, conversation_history: List[Dict]) -> bool:
        """Check if responses are appropriate for the context"""
        return True  # Simplified for now
    
    def _print_scenario_result(self, result: Dict):
        """Print immediate feedback for a scenario"""
        score = result["success_score"]
        status = "SUCCESS" if score >= 80 else "REGULAR" if score >= 60 else "FAILURE"
        
        print(f"   {status} Score: {score:.1f}% | Time: {result['response_time']:.2f}s")
        if result.get("analysis", {}).get("made_function_call"):
            func_name = result["analysis"].get("function_name", "unknown")
            print(f"   Function called: {func_name}")
        
        if "error" in result:
            print(f"   Error: {result['error']}")
    
    def _generate_report(self):
        """Generate comprehensive evaluation report"""
        print("\n" + "=" * 60)
        print("COMPREHENSIVE EVALUATION REPORT")
        print("=" * 60)
        
        # Overall statistics
        total_tests = len(self.results)
        avg_score = sum(r["success_score"] for r in self.results) / total_tests
        avg_response_time = sum(r["response_time"] for r in self.results) / total_tests
        
        print(f"\nOVERALL PERFORMANCE:")
        print(f"   • Total Tests: {total_tests}")
        print(f"   • Average Score: {avg_score:.1f}%")
        print(f"   • Average Response Time: {avg_response_time:.3f}s")
        
        # Performance by category
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"scores": [], "times": []}
            categories[cat]["scores"].append(result["success_score"])
            categories[cat]["times"].append(result["response_time"])
        
        print(f"\nPERFORMANCE BY CATEGORY:")
        for category, data in categories.items():
            avg_cat_score = sum(data["scores"]) / len(data["scores"])
            avg_cat_time = sum(data["times"]) / len(data["times"])
            print(f"   • {category.replace('_', ' ').title()}: {avg_cat_score:.1f}% (avg {avg_cat_time:.3f}s)")
        
        # Detailed results
        print(f"\nDETAILED RESULTS:")
        for result in self.results:
            score = result["success_score"]
            status = "SUCCESS" if score >= 80 else "REGULAR" if score >= 60 else "FAILURE"
            print(f"   {status} {result['name']}: {score:.1f}%")
        
        # Key insights
        self._generate_insights()
        
        # Save results to file
        self._save_results()
    
    def _generate_insights(self):
        """Generate key insights from the evaluation"""
        print(f"\n KEY INSIGHTS:")
        
        # Function calling accuracy
        function_tests = [r for r in self.results if r["category"] == "function_calling"]
        if function_tests:
            func_avg = sum(r["success_score"] for r in function_tests) / len(function_tests)
            print(f"   • Function Calling Accuracy: {func_avg:.1f}%")
        
        # Error handling performance
        error_tests = [r for r in self.results if r["category"] == "error_handling"]
        if error_tests:
            error_avg = sum(r["success_score"] for r in error_tests) / len(error_tests)
            print(f"   • Error Handling Quality: {error_avg:.1f}%")
        
        # Response time analysis
        fast_responses = sum(1 for r in self.results if r["response_time"] < 2.0)
        print(f"   • Fast Responses (<2s): {fast_responses}/{len(self.results)} ({fast_responses/len(self.results)*100:.1f}%)")
        
        # Success rate by score threshold
        excellent = sum(1 for r in self.results if r["success_score"] >= 90)
        good = sum(1 for r in self.results if r["success_score"] >= 70)
        print(f"   • Excellent Performance (≥90%): {excellent}/{len(self.results)} ({excellent/len(self.results)*100:.1f}%)")
        print(f"   • Good Performance (≥70%): {good}/{len(self.results)} ({good/len(self.results)*100:.1f}%)")
    
    def _save_results(self):
        """Save detailed results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/evaluation_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "experiment_info": {
                    "timestamp": datetime.now().isoformat(),
                    "total_tests": len(self.results),
                    "model_info": getattr(self.chatbot, 'current_model', 'unknown')
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: {filename}")

if __name__ == "__main__":
    evaluator = ChatbotEvaluator()
    evaluator.run_comprehensive_evaluation()