
<img width="1200" height="398" alt="nodedesk-banner" src="https://github.com/user-attachments/assets/ffb337c3-0026-47f1-886b-d4dcb8dab258" />

NodeDesk is an intelligent IT support agent that automatically categorizes, analyzes, and resolves technical queries in a business/office environment. It uses LangChain and Groq to provide automated technical guidance and ticket management.

## 🎯 Overview

NodeDesk follows a structured workflow to handle IT support requests:

1. **Query Analysis**: Determines if the query is related to business/office IT
2. **Technical Guidance**: Provides step-by-step solutions for IT issues
3. **Satisfaction Check**: Evaluates if the provided solution resolved the issue
4. **Ticket Management**: Automatically creates resolved or escalation tickets

## 🏗️ Architecture

### State Management
The system uses a `NodeDeskState` structure to track:
- `query`: The original user query
- `is_technical`: Whether the query is IT-related
- `it_category`: Specific IT category (Hardware, Software, Network, etc.)
- `satisfaction_level`: User satisfaction with the solution
- `answer`: The technical guidance provided
- `ticket_created`: Whether a ticket has been created
- `interaction_count`: Number of interactions to prevent infinite loops

### IT Categories
NodeDesk categorizes queries into business/office IT categories:
1. **Hardware**: Business computers, servers, printers, monitors, office devices
2. **Software**: Business applications, operating systems, productivity software
3. **Network**: Internet, connectivity, business networks, VPN
4. **Security**: Business passwords, access controls, permissions
5. **Email**: Business email systems, Outlook, Exchange
6. **Database**: Business databases, data storage, SQL
7. **Non-Technical**: Gaming consoles, personal devices, non-IT questions

## 🚀 Setup

### Prerequisites
- Python 3.8+
- Groq API key

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd nodedesk
```

2. **Create a virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

## 📦 Dependencies

The project requires the following packages:
- `langchain-groq`: For AI model integration
- `langchain-core`: For core LangChain functionality
- `python-dotenv`: For environment variable management
- `langgraph`: For workflow orchestration (optional)

## 🔧 Usage

### Basic Usage

```python
from main import execute_nodedesk

# Example query
query = "My computer won't turn on"
result = execute_nodedesk(query)

print(f"Category: {result['it_category']}")
print(f"Satisfaction: {result['satisfaction_level']}")
print(f"Answer: {result['answer']}")
```

### Workflow Functions

The system provides several key functions:

#### `check_technical_context(state)`
Determines if a query is related to business/office IT.

#### `respond_general(state)`
Provides general response for non-technical queries, directing users to ask IT-related questions.

#### `provide_technical_guidance(state)`
Offers step-by-step technical guidance based on the IT category.

#### `check_satisfaction(state)`
Evaluates user satisfaction with the provided solution.

#### `create_resolved_ticket(state)`
Creates a ticket marked as resolved by the agent.

#### `create_escalation_ticket(state)`
Creates a ticket for escalation to human support.

## 🔄 Workflow

1. **Initial Assessment**: The system checks if the query is IT-related
2. **Non-Technical Handling**: If not IT-related, provides guidance and creates a resolved ticket
3. **Technical Support**: If IT-related, provides technical guidance
4. **Satisfaction Evaluation**: Checks if the user is satisfied with the solution
5. **Ticket Creation**: 
   - If satisfied: Creates a resolved ticket
   - If not satisfied: Creates an escalation ticket
6. **Loop Prevention**: Limits interactions to prevent infinite loops

## 🛠️ Configuration

### Model Configuration
- **Model**: `llama3-8b-8192` (Groq)
- **Temperature**: Varies by function (0.0 for classification, 0.3-0.7 for responses)
- **Recursion Limit**: 5 interactions maximum

### Business Focus
The system is specifically designed for business/office environments and excludes:
- Video game consoles
- Personal entertainment devices
- Home appliances
- Car issues
- General non-IT questions

## 📊 Example Output

```python
# Input: "My computer won't turn on"
{
    'query': 'My computer won\'t turn on',
    'it_category': '1. Hardware',
    'satisfaction_level': 'Satisfied',
    'answer': 'Here are the steps to troubleshoot your computer...'
}
```

## 🔍 Troubleshooting

### Common Issues

1. **GraphRecursionError**: The system has built-in loop prevention. If you encounter this, check the query complexity.

2. **API Key Issues**: Ensure your Groq API key is properly set in the `.env` file.

3. **Import Errors**: Make sure all dependencies are installed correctly.

### Debug Mode
The system includes logging to help understand the workflow:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

[Add your license information here]

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the workflow documentation
3. Create an issue in the repository

---

**NodeDesk** - Making IT support smarter, one query at a time! 🚀


