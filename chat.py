#!/usr/bin/env python3
"""
E-commerce Customer Service Chatbot
Simple launcher for the CLI interface
"""

if __name__ == "__main__":
    try:
        from src.interfaces.cli_chat import main
        main()
    except ImportError as e:
        print("Error: Could not import chatbot modules.")
        print("Make sure you're running from the project root directory.")
        print(f"Error details: {e}")
    except KeyboardInterrupt:
        print("\n Goodbye!")