# **E-commerce Chatbot: Experiment Report**

## **Summary**

This report presents a comprehensive evaluation of an AI-powered e-commerce customer service chatbot designed to handle order tracking and cancellation requests through automated API interactions. The chatbot, built on Phi-3.5-mini (3.8B parameters) running via llama-cpp, was evaluated across 11 test scenarios covering function calling, parameter extraction, error handling, and conversation flow.

**Key Findings:**

- API call accuracy: 54.5% (target: >85%)
- Parameter extraction accuracy: 69.2% (target: >90%) 
- Average response latency: 16.96 seconds (target: <3s)

The experimental results reveal moderate performance with significant optimization opportunities. The system is not production-ready due to consistency and performance issues, however it demonstrates functional capabilities in natural language generation and logic enforcement.

## **System Architecture**

The chatbot system implements a multi-layered architecture combining large language model inference with JSON-based data operations. As a proof of concept, some design decisions were made:

**Design decisions**
- Mocked API functions: Due capacity constraints, it was decided to mock the API functions
- JSON file storage: As a first iteration it was decided to use JSON-based customer and order databases instead of a proper database with SQL for example
- Small LLM: Due to memory constraints, a small LLM model was used for inference, affecting the quality of the responses

**Core Components:**
- **LLM Engine**: Phi-3.5-mini (3.8B parameter mixture-of-experts model)
- **Inference Backend**: llama-cpp for CPU-optimized inference
- **API Layer**: Dedicated modules for order tracking and cancellation operations
- **Data Storage**: JSON-based customer and order databases
- **Logging System**: Comprehensive conversation and decision tracking

**Processing Flow:**
1. User input processed by LLM for intent classification
2. System generates either direct responses or structured function calls
3. Function calls execute corresponding API operations
4. Results fed back into conversation context for natural language response generation
5. All interactions logged for evaluation and debugging

## **Experiment Setup**

**Hardware Configuration:**
- **Processor**: Intel Mac, 2.6 GHz 6-core i7
- **Memory**: 16GB RAM
- **Inference**: CPU-only (no GPU acceleration)

**Model Configuration:**
- **Temperature**: 0.1 (low for consistent function calling)
- **Max Tokens**: 150 (short focused responses)
- **Inference Mode**: CPU-based via llama-cpp
- **Context Window**: 2048 tokens

**Test Environment:**
- **Database**: Pre-populated JSON files with representative e-commerce data
- **Order Statuses**: Cancelled, shipped, delivered (multiple scenarios)
- **Time Constraints**: Orders spanning different ages for policy testing
- **Execution**: Independent tests with fresh conversation contexts
- **Logging**: Comprehensive metrics capture for post-hoc analysis

## **Experiment Design**

The evaluation framework encompassed 11 test scenarios distributed across five functional categories with specific success criteria:

| **Category** | **Test Count** | **Focus Area** | **Success Criteria** |
|--------------|----------------|----------------|----------------------|
| Function Calling | 3 | API invocation decisions | Correct function selection |
| Parameter Extraction | 2 | Data parsing accuracy | Accurate email/order_id extraction |
| Error Handling | 2 | Missing information management | Appropriate user guidance |
| Business Logic | 1 | Policy enforcement | Correct rule application |
| Conversation Flow | 1 | Multi-turn context | Parameter reuse across turns |
| Edge Cases | 2 | Invalid input handling | Graceful error management |

**Measurement Framework:**
- **Quantitative Metrics**: API call accuracy, parameter accuracy, response time
- **Qualitative Assessment**: Response naturalness, helpfulness, policy adherence
- **Behavioral Analysis**: Decision-making consistency and error handling patterns

## **Experiment Results**

### **Primary Performance Metrics**

| **Metric** | **Result** | **Target** | **Performance Gap** | **Status** |
|------------|------------|------------|---------------------|------------|
| API Call Accuracy | 54.5% | >85% | -30.5% | ❌ Below Target |
| API Arguments Accuracy | 69.2% | >90% | -20.8% | ⚠️ Needs Improvement |
| Average Latency | 16.96s | <3s | +13.96s | ❌ Unacceptable |
| Fast Responses (<5s) | 9.1% | >80% | -70.9% | ❌ Critical Issue |

### **Detailed Performance Analysis**

**API Call Decision Accuracy:**
Only 6 out of 11 tests (54.5%) were successful. This means nearly half of customer requests would not be handled correctly.
Among the failures we find:
  - "Specific Order Status" bypassed API call entirely
  - Error handling tests incorrectly attempted invalid API calls
  - Inconsistent behavior across similar query patterns
Only Basic tracking and cancellation with explicit parameters cases were succesful.

**Parameter Extraction Results:**
18 out of 26 required parameters (69.2%) were included in the API calls.
Among the common failures we find:
  - Placeholder email usage ("user@email.com") instead of extraction
  - Missing order_id when contextually available
  - Context loss between conversation turns
The requests were succeaful when the user mentioned explicitly the email formats and order_id.

**Response Time Distribution:**

Average latency is 16.9s, equivalent to a customer waiting while the system "thinks".

| **Time Range** | **Count** | **Percentage** | **Assessment** |
|----------------|-----------|----------------|----------------|
| <5 seconds | 1 | 9.1% | Acceptable |
| 5-15 seconds | 4 | 36.4% | Slow |
| 15-25 seconds | 4 | 36.4% | Very Slow |
| >25 seconds | 2 | 18.2% | Unacceptable |

### **Qualitative Observations**

**System Strengths:**
- Natural language response generation with appropriate tone
- Correct business rule enforcement (10-day cancellation policy)
- Helpful explanations for policy restrictions and failures
- Contextually appropriate guidance for alternative actions

**Critical Weaknesses:**
- Inconsistent decision-making between similar requests
- Unreliable parameter extraction from natural language
- Excessive processing time impacting user experience
- Lack of robust error handling for edge cases

## **Conclusion**

This evaluation demonstrates that the current chatbot implementation achieves functional capability in core e-commerce operations but requires significant improvements before production deployment. The system architecture proves sound for the intended use case, with particular strength in natural language generation and business logic implementation.
Multiple system optimizations are needed based on identified failure patterns.

## **Future Work**

**Consistency Enhancement:**
- Implement function call validation layers to ensure deterministic behavior
- Strengthen system prompts with additional explicit examples and edge cases
- Develop deterministic fallback logic for ambiguous scenarios
- Add input validation before API execution to prevent invalid calls

**Performance Optimization:**
- Migrate to GPU-based inference for 5-10x speed improvement
- Evaluate smaller, specialized models (e.g., 1B parameter alternatives) or bigger models if more powerful machines are provided
- Optimize inference parameters for faster generation

**Architecture Evolution:**
- Evaluate purpose-built function-calling models (OpenAI GPT-4, Anthropic Claude)
- Investigate hybrid architectures (small routing model + specialized task models)
- Implement proper API functions
- Implement proper database using SQL

**Production Readiness:**
- Establish quantitative performance benchmarks and monitoring
- Develop customer satisfaction measurement and feedback integration
