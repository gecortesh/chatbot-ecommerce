import sys
import os
sys.path.append('src')

from interfaces.cli_chat import CLIChatBot

def test_integration():
    """Test the complete chatbot integration"""
    print("Testing chatbot integration...")
    
    try:
        # Initialize CLI bot (this will load the model)
        print("1. Initializing chatbot...")
        cli_bot = CLIChatBot()
        
        # Test cases
        test_cases = [
            "Hello, I need help with my order",
            "Track my orders for john@example.com",
            "What is the status of order ORD001 for john@example.com?",
            "Cancel order ORD002 for john@example.com",
            "Check orders for jane@example.com"
        ]
        
        print("\n2. Testing conversation flow...")
        for i, test_input in enumerate(test_cases, 1):
            print(f"\n--- Test {i} ---")
            print(f"User: {test_input}")
            
            try:
                response, history = cli_bot.bot.chat(test_input, cli_bot.conversation_history)
                cli_bot.conversation_history = history
                print(f"Bot: {response}")
                print(" Success")
            except Exception as e:
                print(f" Error: {e}")
        
        print("\nIntegration test completed!")
        
    except Exception as e:
        print(f" Integration test failed: {e}")

if __name__ == "__main__":
    test_integration()