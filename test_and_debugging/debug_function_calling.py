import sys
import os
sys.path.append('src')

from interfaces.cli_chat import CLIChatBot

def debug_function_calls():
    """Debug function calling specifically"""
    print("🔍 DEBUGGING FUNCTION CALLING")
    print("="*50)
    
    try:
        cli_bot = CLIChatBot()
        
        test_cases = [
            "Track my orders for john@example.com",
            "What is the status of order ORD001 for john@example.com?",
            "Cancel order ORD002 for john@example.com"
        ]
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"\n--- DEBUG Test {i} ---")
            print(f"Input: {test_input}")
            
            # Get raw LLM response
            conversation_history = [{"role": "user", "content": test_input}]
            raw_response = cli_bot.bot._call_llm(conversation_history)
            print(f"Raw LLM Response: '{raw_response}'")
            
            # Check function parsing
            func_name, params = cli_bot.bot._parse_function_call(raw_response)
            print(f"Parsed Function: {func_name}")
            print(f"Parsed Params: {params}")
            
            # Get full chat response
            response, history = cli_bot.bot.chat(test_input, [])
            print(f"Final Response: {response}")
            print("-" * 30)
        
    except Exception as e:
        print(f" Debug failed: {e}")

if __name__ == "__main__":
    debug_function_calls()