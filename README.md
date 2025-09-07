# E-commerce Customer Service Chatbot

## Project Overview

An AI-powered customer service chatbot for e-commerce platforms that handles order tracking and cancellation requests through automated API interactions while enforcing business policies.

### Key Features
- **AI-powered Responses**: Natural language understanding and generation
- **Policy-Aware Responses**: Enforces 10-day cancellation policy automatically
-  **API Integration**: Connects to OrderTracking and OrderCancellation endpoints
-  **Multi-step Conversations**: Context-aware dialogue management
-  **Authentication Flow**: Email-based customer verification
-  **Multiple Interfaces**: CLI and Web API
-  **Function Calling**: Hidden API calls with natural language responses

## System Architecture

![Alt text](images/chatbot.png?raw=true "System overview")

### Core Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **LLM Engine** | Phi-3.5-mini + llama-cpp | Intent classification & response generation |
| **API Layer** | Python modules | Order tracking & cancellation logic |
| **Data Storage** | JSON files | Customer & order data (POC) |
| **Web API** | FastAPI | REST endpoints for web integration |
| **Frontend** | Streamlit | Interactive web interface |
| **CLI** | Python | Command-line interaction |

## Installation & Setup

### Prerequisites
- Python 3.9+
- 8GB+ RAM recommended
- Storage 2GB for model files

### Installation Steps

1. **Clone the repository**
```
git clone https://github.com/gecortesh/chatbot-ecommerce
cd chatbot-ecommerce
```
2. **Install dependencies**
```
pip install -r requirements.txt
```
3. **Download Model**
```
mkdir -p models

cd models

pip install -U "huggingface_hub[cli]"

huggingface-cli download bartowski/Phi-3.5-mini-instruct-GGUF --include "Phi-3.5-mini-instruct-Q4_K_M.gguf" --local-dir .
```
4. **Verify setup**
```
python -c "from src.llm.chatbot import ChatBot; print('Setup complete!')"
```

## Usage

### CLI Interface
```
python chat.py
```
#### Example Conversation:
```
👤 You: I want to track my order
🤖 Bot: I'd be happy to help you track your order! Could you please provide your email address?
👤 You: john@example.com
🤖 Bot: Hi John Doe, I found 3 orders:
- Order ORD001: $999.99 (cancelled) - 2025-08-30
- Order ORD002: $59.98 (shipped) - 2025-08-20
- Order ORD004: $159.99 (delivered) - 2025-08-27

Which order would you like to track specifically?
```
### Web Interface
```
# Start both API and frontend
python web_launcher.py
```

#### Access Points:
- Frontend: http://localhost:8501

## Business Policies

### Order Cancellation Policy

- Eligible: Orders placed within 10 days
- Eligible: Orders with status "processing"
- Not Eligible: Orders older than 10 days
- Not Eligible: Orders with status "shipped", "delivered", or "cancelled"
- Authentication Requirements

Users must provide email address for order operations
Email is validated against customer database
Orders are filtered by customer ownership

## Logging

Logs are automatically created in the `logs/` directory:
- Session Logs: Individual conversation tracking
- Error Logs: System error monitoring
- Evaluation Results: Performance metrics (when running tests)

## Evaluation

Run comprehensive performance evaluation:
```
python create_evaluation_experiment.py
```
Calculate metrics from results:
```
python calculate_evaluation_metrics.py -r logs/evaluation_results_*.json
```
An initial evaluation report can be found in `experiments/experiments_report.md`.
