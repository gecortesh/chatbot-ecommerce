import os
import sys
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from llm.chatbot import ChatBot

class CLIChatBot:
    def __init__(self):
        session_id = f"cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Updated loading message for llama-cpp
        print("Initializing AI model... This may take a moment.")
        
        self.bot = ChatBot(session_id=session_id)
        self.conversation_history = []
        self.session_start = datetime.now()
        
        # Show what model is actually loaded
        model_info = getattr(self.bot, 'current_model', 'rule-based system')
        if hasattr(self.bot, 'llm') and self.bot.llm == "llama_cpp":
            print(f"AI model loaded: {os.path.basename(model_info)}")
        else:
            print("Enhanced rule-based system ready!")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print the chatbot header"""
        model_info = "llama-cpp + Phi-3.5" if hasattr(self.bot, 'llm') and self.bot.llm == "llama_cpp" else "Rule-based AI"
        
        print(" E-COMMERCE CUSTOMER SERVICE CHATBOT")
        print("="*60)
        print("I can help you with:")
        print("   • Order tracking - Check your order status")
        print("   • Order cancellation - Cancel eligible orders")
        print("   • Order information - Get detailed order info")
        print("")
        print("Available commands:")
        print("   • 'help' - Show detailed help menu")
        print("   • 'history' - Show conversation history")
        print("   • 'clear' - Clear screen")
        print("   • 'reset' - Start new conversation")
        print("   • 'quit' - Exit chatbot")
        print("="*60)
        print("Always include your email for order operations!")
        print("Example emails: john@example.com, jane@example.com")
        print(f"Powered by: {model_info}")
    
    def print_help(self):
        """Print comprehensive help information"""
        print("\n" + "="*50)
        print("CHATBOT HELP GUIDE")
        print("="*50)
        
        print("\n EMAIL VERIFICATION:")
        print("   • Always provide your email for order operations")
        print("   • Valid test emails: john@example.com, jane@example.com")
        
        print("\n ORDER TRACKING EXAMPLES:")
        print("   • 'Track my orders for john@example.com'")
        print("   • 'What's the status of order ORD001 for john@example.com?'")
        print("   • 'Check my orders'")
        print("   • 'Show me order ORD002'")
        
        print("\n ORDER CANCELLATION EXAMPLES:")
        print("   • 'Cancel order ORD001 for john@example.com'")
        print("   • 'I want to cancel my order ORD003'")
        print("   • 'Please cancel order ORD002'")
        
        print("\n BUSINESS POLICIES:")
        print("   • Orders can be cancelled within 10 days")
        print("   • Shipped/delivered orders cannot be cancelled")
        print("   • Processing orders can still be cancelled")
        
        print("\n AVAILABLE TEST DATA:")
        print("   john@example.com:")
        print("      • ORD001: Cancelled ($999.99)")
        print("      • ORD002: Shipped ($59.98) - too old to cancel")
        print("      • ORD004: Delivered ($159.99)")
        print("   jane@example.com:")
        print("      • ORD003: Cancelled ($79.99)")
        
        print("\n CONVERSATION TIPS:")
        print("   • Be natural: 'Hi, I need help with my order'")
        print("   • Be specific: Include email and order ID when possible")
        print("   • Ask questions: 'What orders do I have?'")
        print("="*50)
    
    def show_history(self):
        """Show conversation history with better formatting"""
        if not self.conversation_history:
            print("\n📭 No conversation history yet.")
            return
        
        print(f"\n CONVERSATION HISTORY")
        print(f" Session started: {self.session_start.strftime('%H:%M:%S')}")
        print("-" * 50)
        
        for i, msg in enumerate(self.conversation_history[-10:], 1):
            role_emoji = "👤" if msg["role"] == "user" else "🤖"
            role_name = "You" if msg["role"] == "user" else "Bot"
            timestamp = datetime.now().strftime('%H:%M')
            
            # Truncate long messages
            content = msg['content'][:120] + "..." if len(msg['content']) > 120 else msg['content']
            
            print(f"{i:2}. [{timestamp}] {role_emoji} {role_name}: {content}")
        
        if len(self.conversation_history) > 10:
            print(f"... and {len(self.conversation_history) - 10} more messages")
        print("-" * 50)
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.session_start = datetime.now()
        print("\n Conversation reset! Starting fresh session.")
    
    def format_bot_response(self, response):
        """Format bot response for better readability"""
        # Add visual breaks for long responses
        if len(response) > 250:
            # Split into logical parts
            sentences = response.split('. ')
            formatted = ""
            current_line = ""
            
            for i, sentence in enumerate(sentences):
                if len(current_line + sentence) > 80:
                    formatted += current_line.rstrip() + ".\n   "
                    current_line = sentence
                else:
                    current_line += sentence
                    if i < len(sentences) - 1:
                        current_line += ". "
            
            formatted += current_line
            return formatted
        return response
    
    def show_performance_stats(self):
        """Show session performance statistics"""
        total_messages = len(self.conversation_history)
        session_duration = datetime.now() - self.session_start
        
        print(f"\n SESSION STATISTICS:")
        print(f"   • Total messages: {total_messages}")
        print(f"   • Session duration: {session_duration}")
        print(f"   • Model: {getattr(self.bot, 'current_model', 'rule-based')}")
    
    def run(self):
        """Main chat loop with enhanced UX"""
        self.clear_screen()
        self.print_header()
        
        # Welcome message with model info
        model_type = "AI-powered" if hasattr(self.bot, 'llm') and self.bot.llm == "llama_cpp" else "rule-based"
        print(f"\n Hello! I'm your {model_type} customer service assistant.")
        print(" Type your message, or try 'help' for examples and guidance.")
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q', 'bye']:
                    self.show_performance_stats()
                    print("\n🤖 Bot: Thank you for using our customer service! Have a great day! 👋")
                    break
                
                elif user_input.lower() in ['help', 'h', '?']:
                    self.print_help()
                    continue
                
                elif user_input.lower() == 'history':
                    self.show_history()
                    continue
                
                elif user_input.lower() == 'clear':
                    self.clear_screen()
                    self.print_header()
                    continue
                
                elif user_input.lower() in ['reset', 'restart']:
                    self.reset_conversation()
                    continue
                
                elif user_input.lower() in ['stats', 'status']:
                    self.show_performance_stats()
                    continue
                
                if not user_input:
                    print("💭 Please enter a message or type 'help' for assistance.")
                    continue
                
                # Process with chatbot
                print("\n🤖 Bot: ", end="", flush=True)
                
                try:
                    # Show processing indicator
                    print("💭 Processing...", end="", flush=True)
                    
                    response, self.conversation_history = self.bot.chat(user_input, self.conversation_history)
                    
                    # Clear processing indicator and show response
                    print("\r🤖 Bot: ", end="")
                    formatted_response = self.format_bot_response(response)
                    print(formatted_response)
                    
                except Exception as e:
                    print(f"\r🤖 Bot: I encountered an error: {str(e)}")
                    print("         Please try rephrasing your request or type 'help' for guidance.")
                
            except KeyboardInterrupt:
                print("\n\n🤖 Bot: Interrupted! Goodbye!")
                break
            except EOFError:
                print("\n\n🤖 Bot: Session ended. Goodbye!")
                break

def main():
    """Entry point for CLI chatbot"""
    try:
        cli_bot = CLIChatBot()
        cli_bot.run()
    except Exception as e:
        print(f" Failed to start chatbot: {e}")
        print("Troubleshooting:")
        print("   • Make sure you're in the project root directory")
        print("   • Check that all dependencies are installed")
        print("   • Verify the model file exists in ./models/")

if __name__ == "__main__":
    main()