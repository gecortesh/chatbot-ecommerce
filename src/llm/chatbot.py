import json
import re
import logging
import uuid
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from llama_cpp import Llama
from apis.order_apis import OrderAPIs

class ChatBot:
    def __init__(self, session_id=None):
        self.order_apis = OrderAPIs()
        self.session_id = session_id or str(uuid.uuid4())[:8]
        
        # Setup logging
        self._setup_logging()
        
        # Initialize the model
        self._initialize_model()
        
        # System message optimized for function calling
        self.system_message = """You are a helpful customer service chatbot for an e-commerce company.

AVAILABLE FUNCTIONS:
- orderTracking(email, order_id=None): Track customer orders
- orderCancellation(email, order_id): Cancel a specific order

ORDER CANCELLATION POLICY:
- Eligible: Orders placed within 10 days
- Eligible: Orders with status "processing"
- Not Eligible: Orders older than 10 days
- Not Eligible: Orders with status "shipped", "delivered", or "cancelled"

RULES:
1. If customer provides email → call function: FUNCTION_CALL: functionName(email="user@email.com")
2. If customer lacks email → ask for email
3. When you see "Function [name] executed with result:" interpret the JSON data naturally
4. Be concise and helpful
5. Use ONLY the data from function results - don't make up information

EXAMPLES:

User: "Track my orders for john@example.com"
Assistant: FUNCTION_CALL: orderTracking(email="john@example.com")

System: Function orderTracking executed with result: {"success": True, "data": {"orders": [{"order_id": "ORD001", "status": "cancelled", "total_amount": 999.99}], "customer": {"name": "John Doe"}}}
Assistant: Hi John Doe! I found your order ORD001 with status 'cancelled' and total $999.99.

User: "Cancel order ORD003 for jane@example.com"
Assistant: FUNCTION_CALL: orderCancellation(email="jane@example.com", order_id="ORD003")

System: Function orderCancellation executed with result: {"success": True, "message": "Order ORD003 has been successfully cancelled"}
Assistant: Great! I've successfully cancelled order ORD003 for you.

User: "I want to track my orders"
Assistant: I'd be happy to help you track your orders! Please provide your email address.

Remember: Only use data from function results, be concise, don't add commentary about the process.
IMPORTANT: Never repeat "Function executed with result" or show JSON data to the user"""

    def _setup_logging(self):
        """Setup logging for chat session and errors"""
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Session log file
        session_log_file = f"logs/chat_session_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.session_logger = logging.getLogger(f"session_{self.session_id}")
        self.session_logger.handlers.clear()
        session_handler = logging.FileHandler(session_log_file)
        session_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.session_logger.addHandler(session_handler)
        self.session_logger.setLevel(logging.INFO)
        
        # Error log file
        error_log_file = f"logs/errors_{datetime.now().strftime('%Y%m%d')}.log"
        self.error_logger = logging.getLogger(f"errors_{self.session_id}")
        self.error_logger.handlers.clear()
        error_handler = logging.FileHandler(error_log_file)
        error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.error_logger.addHandler(error_handler)
        self.error_logger.setLevel(logging.ERROR)
        
        self.session_logger.info(f"=== NEW CHAT SESSION STARTED: {self.session_id} ===")

    def _initialize_model(self):
        """Initialize llama-cpp model"""
        try:
            # Model file paths to try (in order of preference)
            model_path = "models/Phi-3.5-mini-instruct-Q4_K_M.gguf"
            
            # Create models directory if it doesn't exist
            os.makedirs("models", exist_ok=True)
            
            model_loaded = False
            if os.path.exists(model_path):
                try:
                    print(f"Loading {model_path} with llama-cpp...")
                    self.session_logger.info(f"Loading model: {model_path}")
                    
                    self.llama_model = Llama(
                        model_path=model_path,
                        n_ctx=2048,          # Context window
                        n_threads=6,         # Use 6 cores
                        n_batch=512,         # Batch size for processing
                        verbose=False,       # Reduce output
                        chat_format="chatml", # Good for instruction following
                        seed=42              # For reproducible results
                    )
                    
                    self.current_model = model_path
                    print(f"llama-cpp model loaded successfully: {os.path.basename(model_path)}")
                    self.session_logger.info(f"Model loaded successfully: {model_path}")
                    self.llm = "llama_cpp"
                    model_loaded = True
                    
                except Exception as model_error:
                    print(f"Failed to load {model_path}: {str(model_error)}")

            
            if not model_loaded:
                print(" No models found in ./models/ directory")
                print("Download a GGUF model:")
                print("   mkdir -p models")
                print("   # Download Phi-3.5 (recommended):")
                print("   wget https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf -O models/phi-3.5-mini-q4.gguf")
                print(" Using enhanced rule-based system instead")
                self.llm = None
                
        except Exception as e:
            self.error_logger.error(f"Failed to initialize llama-cpp: {str(e)}")
            print(f"llama-cpp initialization failed: {e}")
            print("Using rule-based fallback...")
            self.llm = None

    def _call_llm(self, conversation_history: List[Dict]) -> str:
        """Call model with full conversation history including system messages"""
        try:
            if self.llm != "llama_cpp":
                return self._rule_based_fallback(conversation_history)
            
            # Build messages for llama-cpp
            messages = [
                {"role": "system", "content": self.system_message}
            ]
            
            # Add recent conversation history (limit to avoid context overflow)
            recent_history = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
            
            for msg in recent_history:
                if msg['role'] in ['user', 'assistant', 'system']:
                    messages.append({
                        "role": msg['role'], 
                        "content": msg['content']
                    })
            
            self.session_logger.info(f"llama-cpp messages: {json.dumps(messages, indent=2)}")
            
            # Generate response
            response = self.llama_model.create_chat_completion(
                messages=messages,
                max_tokens=150,        # Shorter responses
                temperature=0.1,       # Very low for consistency
                top_p=0.8,             # The top-p value to use for nucleus sampling
                top_k=20,              # The top-k value to use for sampling
                repeat_penalty=1.0,    # The penalty to apply to repeated tokens
                stop=[                 # A list of strings to stop generation when encountered                
                    "Human:", "User:", "System:", 
                    "Assistant Response:", "System response",
                    "Function executed", "hypothetical",
                    "\n\nUser:", "\n\nHuman:", "\n\nSystem:"
                ]
            )
            
            assistant_response = response['choices'][0]['message']['content'].strip()
            
            # Cleanup of meta-commentary
            assistant_response = re.sub(r'System response.*?:', '', assistant_response, flags=re.IGNORECASE)
            assistant_response = re.sub(r'Assistant Response.*?:', '', assistant_response, flags=re.IGNORECASE)
            assistant_response = re.sub(r'\(hypothetical\).*?:', '', assistant_response, flags=re.IGNORECASE)
            assistant_response = re.sub(r'Function executed.*?and here\'s', 'Here\'s', assistant_response, flags=re.IGNORECASE)
            
            # Remove role indicators
            assistant_response = re.sub(r'^(Assistant|Bot|Human|User):\s*', '', assistant_response, flags=re.MULTILINE)
            
            # Clean up formatting
            assistant_response = re.sub(r'\n+', ' ', assistant_response).strip()
            assistant_response = re.sub(r'\s+', ' ', assistant_response).strip()
            
            # If response starts with meta-commentary, use rule-based fallback
            if any(phrase in assistant_response.lower() for phrase in ['system response', 'assistant response', 'hypothetical', 'function executed']):
                self.session_logger.warning("LLM generated meta-commentary, using rule-based fallback")
                return self._rule_based_fallback(conversation_history)
            
            # If response is empty or too short, use fallback
            if not assistant_response or len(assistant_response.strip()) < 5:
                self.session_logger.warning("llama-cpp returned empty/short response, using fallback")
                return self._rule_based_fallback(conversation_history)
            
            self.session_logger.info(f"llama-cpp clean response: {assistant_response}")
            return assistant_response
            
        except Exception as e:
            self.error_logger.error(f"llama-cpp call failed: {str(e)}")
            return self._rule_based_fallback(conversation_history)
    
    def _rule_based_fallback(self, conversation_history: List[Dict]) -> str:
        """Enhanced rule-based fallback with context awareness"""
        if not conversation_history:
            return "Hello! I'm here to help you with your orders. How can I assist you today?"
        
        last_message = conversation_history[-1]['content'].lower()
        
        # Check if there's a recent function result we should interpret
        function_result = None
        for msg in reversed(conversation_history):
            if msg['role'] == 'system' and 'Function' in msg['content'] and 'executed with result:' in msg['content']:
                try:
                    # Extract JSON from system message
                    json_start = msg['content'].find('{')
                    if json_start != -1:
                        json_str = msg['content'][json_start:]
                        function_result = json.loads(json_str)
                        # Also extract function name
                        function_name = msg['content'].split(' ')[1] if len(msg['content'].split(' ')) > 1 else 'unknown'
                        break
                except:
                    pass
        
        # If there's a recent function result, interpret it
        if function_result:
            self.session_logger.info("Using rule-based interpretation of function result")
            return self._generate_response_from_api_result(function_result, function_name, {})
        
        # Regular intent detection
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', last_message)
        order_match = re.search(r'\b(ORD\d+)\b', last_message, re.IGNORECASE)
        
        email = email_match.group() if email_match else None
        order_id = order_match.group() if order_match else None
        
        # Look for context from previous USER messages
        if not email:
            for msg in reversed(conversation_history[-5:]):
                if msg['role'] == 'user':
                    email_in_context = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', msg['content'])
                    if email_in_context:
                        email = email_in_context.group()
                        break
        
        if not order_id:
            for msg in reversed(conversation_history[-5:]):
                if msg['role'] == 'user':
                    order_in_context = re.search(r'\b(ORD\d+)\b', msg['content'], re.IGNORECASE)
                    if order_in_context:
                        order_id = order_in_context.group()
                        break
        
        # Intent detection
        track_words = ['track', 'tracking', 'status', 'check', 'where', 'find', 'orders', 'order']
        cancel_words = ['cancel', 'cancellation', 'stop', 'return', 'refund']
        
        has_track_intent = any(word in last_message for word in track_words)
        has_cancel_intent = any(word in last_message for word in cancel_words)
        
        if has_track_intent:
            if email:
                if order_id:
                    return f'FUNCTION_CALL: orderTracking(email="{email}", order_id="{order_id}")'
                else:
                    return f'FUNCTION_CALL: orderTracking(email="{email}")'
            else:
                return "I'd be happy to help you track your orders! Please provide your email address."
        
        elif has_cancel_intent:
            if email and order_id:
                return f'FUNCTION_CALL: orderCancellation(email="{email}", order_id="{order_id}")'
            else:
                return "I'd be happy to help you cancel your order! Please provide your email address and order ID."
        
        else:
            return "I can help you track orders or cancel them. What would you like to do?"
    
    def _parse_function_call(self, response: str) -> Tuple[Optional[str], Optional[Dict]]:
        """Parse function call from LLM response"""

        pattern = r'FUNCTION_CALL:\s*(\w+)\((.*?)\)'
        match = re.search(pattern, response)
        
        if match:
            function_name = match.group(1)
            params_str = match.group(2)
            
            # Parse parameters
            params = {}
            param_pattern = r'(\w+)="([^"]*)"'
            for param_match in re.finditer(param_pattern, params_str):
                key = param_match.group(1)
                value = param_match.group(2)
                params[key] = value
            
            self.session_logger.info(f"Function call parsed: {function_name} with params {params}")
            return function_name, params
        return None, None

    def _execute_function(self, function_name: str, params: Dict) -> Dict:
        """Execute the requested function"""
        try:
            self.session_logger.info(f"Executing function: {function_name} with params: {params}")
            
            if function_name == "orderTracking":
                email = params.get("email")
                order_id = params.get("order_id")
                result = self.order_apis.orderTracking(email, order_id)
            elif function_name == "orderCancellation":
                email = params.get("email")
                order_id = params.get("order_id")
                result = self.order_apis.orderCancellation(email, order_id)
            else:
                result = {
                    "success": False,
                    "data": None,
                    "message": f"Unknown function: {function_name}"
                }
            
            self.session_logger.info(f"Function result: {json.dumps(result, indent=2)}")
            return result
            
        except Exception as e:
            error_msg = f"Function execution error: {str(e)}"
            self.error_logger.error(error_msg)
            return {
                "success": False,
                "data": None,
                "message": error_msg
            }

    def _generate_response_from_api_result(self, function_result: Dict, function_name: str, params: Dict) -> str:
        """Generate a natural response from API result (enhanced with examples from system prompt)"""
        try:
            if function_name == "orderTracking":
                if function_result.get("success"):
                    data = function_result.get("data", {})
                    if "orders" in data:
                        # Multiple orders
                        orders = data["orders"]
                        customer = data.get("customer", {})
                        customer_name = customer.get('name', 'there')
                        
                        if len(orders) == 1:
                            order = orders[0]
                            return f"Hi {customer_name}! I found your order {order['order_id']} with status '{order['status']}' and total amount ${order['total_amount']}. Is there anything specific you'd like to know about this order?"
                        else:
                            response = f"Hi {customer_name}! I found {len(orders)} orders for your account:\n"
                            for order in orders[:3]:  # Show max 3 orders
                                response += f"• Order {order['order_id']}: {order['status']} - ${order['total_amount']}\n"
                            if len(orders) > 3:
                                response += f"... and {len(orders) - 3} more orders\n"
                            response += "\nIs there anything specific you'd like to know about these orders?"
                            return response
                    else:
                        # Single order details
                        order_id = data.get("order_id")
                        status = data.get("status")
                        total = data.get("total_amount")
                        customer_name = data.get("customer_name", "")
                        order_date = data.get("order_date")
                        items = data.get("items", [])
                        payment_method = data.get("payment_method", "")
                        
                        response = f"Hi {customer_name}! Here are the details for order {order_id}:\n"
                        response += f"• Status: {status.title()}\n"
                        response += f"• Order Date: {order_date}\n"
                        
                        if items:
                            response += f"• Items: "
                            item_details = []
                            for item in items:
                                item_details.append(f"{item.get('quantity', 1)}x {item.get('product', 'Item')} (${item.get('price', 0)})")
                            response += ", ".join(item_details) + "\n"
                        
                        if payment_method:
                            response += f"• Payment Method: {payment_method.replace('_', ' ').title()}\n"
                        
                        response += f"• Total: ${total}\n"
                        
                        # Add contextual message based on status
                        if status == "cancelled":
                            response += "\nThis order was cancelled, so you should see a refund processed to your original payment method."
                        elif status == "shipped":
                            response += "\nYour order is on its way! You should receive it soon."
                        elif status == "delivered":
                            response += "\nYour order has been delivered. If you have any issues, please let me know!"
                        
                        return response
                else:
                    message = function_result.get("message", "I could not find any orders for that email address.")
                    if "No customer found" in message:
                        return f"I couldn't find any customer account associated with {params.get('email', 'that email')}. Please double-check your email address and make sure it's the same one you used when placing your orders.\n\nIf you continue to have trouble, you might have:\n• Typed the email incorrectly\n• Used a different email address for your orders\n• Created your account with a different email\n\nWould you like to try again with a different email address?"
                    return f"I'm sorry, {message} Please double-check your email address."
            
            elif function_name == "orderCancellation":
                if function_result.get("success"):
                    order_id = params.get("order_id")
                    data = function_result.get("data", {})
                    previous_status = data.get("previous_status", "processing")
                    total_amount = data.get("order", {}).get("total_amount", "the order amount")
                    
                    return f"Great news! I've successfully cancelled order {order_id} for you. The order status has been changed from '{previous_status}' to 'cancelled', and you'll receive a refund of ${total_amount} to your original payment method within 3-5 business days."
                else:
                    message = function_result.get("message", "I wasn't able to cancel that order.")
                    data = function_result.get("data", {})
                    
                    if "days ago" in message:
                        # Too old to cancel
                        days_old = data.get("days_old", "unknown")
                        return f"I'm sorry, but I can't cancel order {params.get('order_id')}. Here's why:\n• The order was placed {days_old} days ago, which exceeds our 10-day cancellation limit\n• Once this time limit is passed, orders cannot be cancelled\n\nHowever, you can still return the items once you receive them. Would you like information about our return policy?"
                    
                    elif "status:" in message:
                        # Wrong status
                        order_status = data.get("order", {}).get("status", "unknown")
                        response = f"I'm unable to cancel order {params.get('order_id')} because it has already been {order_status}. Once an order reaches '{order_status}' status, it cannot be cancelled.\n\n"
                        
                        if order_status in ["delivered", "shipped"]:
                            response += "If you're not satisfied with your purchase, you can initiate a return instead. Would you like me to help you with the return process?"
                        
                        return response
                    
                    return f"I'm sorry, I wasn't able to cancel that order. {message}"
            
            else:
                return "I encountered an issue processing your request. Please try again or contact our support team for assistance."
                
        except Exception as e:
            self.error_logger.error(f"Error in fallback response generation: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again or contact our support team."

    def _call_llm_for_final_response(self, conversation_history: List[Dict], function_result: Dict, function_name: str, params: Dict) -> str:
        """Call llama-cpp LLM to generate final natural response based on function result"""
        try:
            if self.llm != "llama_cpp":
                return self._generate_response_from_api_result(function_result, function_name, params)
            
            # Add function result to conversation history
            function_result_content = f"Function {function_name} was executed and returned: {json.dumps(function_result)}"
            conversation_history.append({"role": "system", "content": function_result_content})
            
            # Use the same _call_llm method with the updated conversation history
            self.session_logger.info("Calling llama-cpp for final response with function result in conversation history")
            response = self._call_llm(conversation_history)
            
            self.session_logger.info(f"Final Response llama-cpp Output: {response}")
            return response
            
        except Exception as e:
            self.error_logger.error(f"Final response llama-cpp call failed: {str(e)}")
            return self._generate_response_from_api_result(function_result, function_name, params)

    def chat(self, user_input: str, conversation_history: Optional[List[Dict]] = None) -> Tuple[str, List[Dict]]:
        """
        Main chat method - function results are added to conversation history
        """
        if conversation_history is None:
            conversation_history = []
        
        # Step 1: Log user input
        self.session_logger.info("="*50)
        self.session_logger.info(f"STEP 1 - USER INPUT: {user_input}")
        
        # Add user input to history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Step 2: Get initial LLM response
        self.session_logger.info("STEP 2 - SENDING TO LLAMA-CPP LLM")
        llm_response = self._call_llm(conversation_history)
        self.session_logger.info(f"STEP 2 - LLAMA-CPP RESPONSE: {llm_response}")
        
        # Step 3: Check if LLM wants to call a function
        function_name, params = self._parse_function_call(llm_response)
        
        if function_name:
            self.session_logger.info(f"STEP 3 - LLAMA-CPP DECIDED TO CALL API: {function_name} with params {params}")
            
            # Step 4: Execute function (hidden from user)
            self.session_logger.info("STEP 4 - EXECUTING API CALL (HIDDEN FROM USER)")
            function_result = self._execute_function(function_name, params)
            self.session_logger.info(f"STEP 4 - API RESULT: {json.dumps(function_result, indent=2)}")
            
            # Step 5: Add function result to conversation history
            self.session_logger.info("STEP 5 - ADDING FUNCTION RESULT TO CONVERSATION HISTORY")
            function_result_message = f"Function {function_name} executed with result: {json.dumps(function_result)}"
            conversation_history.append({"role": "system", "content": function_result_message})
            
            # Step 6: Call LLM again with updated conversation history (including function result)
            self.session_logger.info("STEP 6 - CALLING LLM AGAIN WITH FUNCTION RESULT IN HISTORY")
            final_response = self._call_llm(conversation_history)
            
            # Clean up any remaining function calls from final response
            final_response = re.sub(r'FUNCTION_CALL:.*?\)', '', final_response).strip()
            
            if not final_response or len(final_response.strip()) < 10:
                self.session_logger.warning("STEP 6 - LLM returned empty final response, using fallback")
                final_response = self._generate_response_from_api_result(function_result, function_name, params)
            
            # Add the final assistant response to conversation history
            conversation_history.append({"role": "assistant", "content": final_response})
            
            self.session_logger.info(f"STEP 6 - FINAL RESPONSE TO USER: {final_response}")
            self.session_logger.info("="*50)
            return final_response, conversation_history
        else:
            # No function call needed - direct response
            self.session_logger.info("STEP 3 - NO API CALL NEEDED, DIRECT RESPONSE")
            clean_response = re.sub(r'FUNCTION_CALL:.*?\)', '', llm_response).strip()
            
            if not clean_response or len(clean_response.strip()) < 3:
                self.session_logger.warning("llama-cpp returned empty direct response, using fallback")
                clean_response = self._rule_based_fallback(conversation_history)
            
            conversation_history.append({"role": "assistant", "content": clean_response})
            
            self.session_logger.info(f"STEP 4 - DIRECT RESPONSE TO USER: {clean_response}")
            self.session_logger.info("="*50)
            return clean_response, conversation_history
