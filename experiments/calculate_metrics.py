import json
import argparse

def calculate_chatbot_metrics(results_file):
    """Calculate API call accuracy, API arguments accuracy, and latency"""
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = data["results"]
    
    # 1. API CALL ACCURACY
    api_call_accuracy = calculate_api_call_accuracy(results)
    
    # 2. API ARGUMENTS ACCURACY  
    api_arguments_accuracy = calculate_api_arguments_accuracy(results)
    
    # 3. LATENCY
    latency_metrics = calculate_latency_metrics(results)
    
    # Print Results
    print_metrics(api_call_accuracy, api_arguments_accuracy, latency_metrics)
    
    return {
        "api_call_accuracy": api_call_accuracy,
        "api_arguments_accuracy": api_arguments_accuracy,
        "latency": latency_metrics
    }

def calculate_api_call_accuracy(results):
    """Calculate API call accuracy: correct API calls / total tests requiring API calls"""
    
    # Define which tests should require API calls
    should_call_api = {
        "Basic Order Tracking": "orderTracking",
        "Specific Order Status": "orderTracking",
        "Order Cancellation": "orderCancellation",
        "Email Extraction Variation 1": "orderTracking",
        "Order ID Extraction": "orderCancellation",
        "Missing Email": None,  # Should ask for email
        "Missing Order ID for Cancellation": None,  # Should ask for order ID
        "Failed Cancellation (Too Old)": "orderCancellation",
        "Multi-Turn Context": ["orderTracking", "orderCancellation"],
        "Invalid Email": None,  # Should handle gracefully
        "Non-existent Customer": "orderTracking",
    }
    
    correct_calls = 0
    total_required_calls = 0
    
    for result in results:
        test_name = result["name"]
        made_call = result["analysis"].get("made_function_call", False)
        function_called = result["analysis"].get("function_name")
        
        if test_name in should_call_api:
            expected = should_call_api[test_name]
            
            if expected is None:
                # Should NOT call API
                if not made_call:
                    correct_calls += 1
                total_required_calls += 1
            elif isinstance(expected, list):
                # Multi-turn context - simplified scoring
                total_required_calls += 1
                if made_call:
                    correct_calls += 1
            else:
                # Should call specific API
                total_required_calls += 1
                if made_call and function_called == expected:
                    correct_calls += 1
    
    accuracy_percentage = (correct_calls / total_required_calls) * 100 if total_required_calls > 0 else 0
    
    return {
        "correct_calls": correct_calls,
        "total_required": total_required_calls,
        "accuracy_percentage": accuracy_percentage
    }

def calculate_api_arguments_accuracy(results):
    """Calculate API arguments accuracy: correct arguments / total required arguments"""
    
    required_args = {
        "orderTracking": ["email"],
        "orderCancellation": ["email", "order_id"]
    }
    
    total_correct_args = 0
    total_required_args = 0
    
    for result in results:
        test_name = result["name"]
        made_call = result["analysis"].get("made_function_call", False)
        function_called = result["analysis"].get("function_name")
        
        if made_call and function_called in required_args:
            conversation_history = result.get("conversation_history", [])
            actual_args = extract_function_arguments(conversation_history, function_called)
            
            required_args_for_func = required_args[function_called].copy()
            
            # Special cases requiring order_id
            if test_name in ["Specific Order Status", "Order ID Extraction"] and function_called == "orderTracking":
                if "order_id" not in required_args_for_func:
                    required_args_for_func.append("order_id")
            
            for arg in required_args_for_func:
                if arg in actual_args and actual_args[arg] and actual_args[arg] not in ["user@email.com", "invalid-email"]:
                    total_correct_args += 1
                total_required_args += 1
    
    accuracy_percentage = (total_correct_args / total_required_args) * 100 if total_required_args > 0 else 0
    
    return {
        "correct_arguments": total_correct_args,
        "total_required": total_required_args,
        "accuracy_percentage": accuracy_percentage
    }

def extract_function_arguments(conversation_history, function_name):
    """Extract arguments from function execution in conversation history"""
    for msg in conversation_history:
        if msg["role"] == "system" and f"Function {function_name}" in msg["content"]:
            try:
                json_start = msg["content"].find("{")
                if json_start != -1:
                    result_json = json.loads(msg["content"][json_start:])
                    args = {}
                    
                    if "data" in result_json and result_json["data"]:
                        data = result_json["data"]
                        if "customer" in data:
                            args["email"] = data["customer"].get("email", "")
                        if "order" in data:
                            args["email"] = data["order"].get("customer", {}).get("email", "")
                            args["order_id"] = data["order"].get("order_id", "")
                        if "orders" in data and data["orders"]:
                            args["email"] = data["orders"][0].get("customer", {}).get("email", "")
                    
                    # Handle error cases
                    if not result_json.get("success", True):
                        message = result_json.get("message", "")
                        if "email:" in message:
                            import re
                            email_match = re.search(r'email:\s*([^\s]+)', message)
                            if email_match:
                                args["email"] = email_match.group(1)
                    
                    return args
            except:
                pass
    
    return {}

def calculate_latency_metrics(results):
    """Calculate latency metrics"""
    response_times = [result["response_time"] for result in results]
    
    avg_latency = sum(response_times) / len(response_times)
    min_latency = min(response_times)
    max_latency = max(response_times)
    
    return {
        "average_latency": avg_latency,
        "min_latency": min_latency,
        "max_latency": max_latency
    }

def print_metrics(api_call_accuracy, api_arguments_accuracy, latency_metrics):
    """Print clean metrics output"""
    print("CHATBOT PERFORMANCE METRICS")
    print("=" * 40)
    print(f"API_call_accuracy: {api_call_accuracy['accuracy_percentage']:.1f}%")
    print(f"API_arguments: {api_arguments_accuracy['accuracy_percentage']:.1f}%")
    print(f"Latency: {latency_metrics['average_latency']:.2f} seconds")

def main():
    parser = argparse.ArgumentParser(description='Calculate chatbot evaluation metrics')
    parser.add_argument('-r', '--report', required=True, help='Path to evaluation report JSON file')
    
    args = parser.parse_args()
    
    try:
        calculate_chatbot_metrics(args.report)
    except FileNotFoundError:
        print(f"Error: File '{args.report}' not found")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{args.report}'")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()