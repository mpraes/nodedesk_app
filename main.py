# %%
from typing import Dict, TypedDict, Literal
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END, START
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
from IPython.display import display, Image
from langchain_core.runnables.graph import MermaidDrawMethod

## Logging to understand the problems
import logging
logging.basicConfig(level=logging.INFO)


# Loading the environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY") or ""
# %%
# Defining the structure state of the node desk
class NodeDeskState(TypedDict):
    query: str | None
    is_technical: bool | None
    it_category: str | None
    satisfaction_level: str | None
    answer: str | None
    ticket_created: bool | None
    interaction_count: int | None

# %%

# Nodes functions
# 1 - Check if the query is technical (IT context)
def check_technical_context(state: NodeDeskState) -> NodeDeskState:
    """Check if the query is in technical (IT) context"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that determines if a query is related to IT/technical context in a business/office environment.
        
        Focus on BUSINESS/OFFICE IT equipment and systems, not consumer electronics or gaming devices.
        
        Analyze the query and respond with ONLY one of these categories:
        1. Hardware (business computers, servers, printers, monitors, office devices, etc.)
        2. Software (business applications, operating systems, productivity software, etc.)
        3. Network (internet, connectivity, business networks, VPN, etc.)
        4. Security (business passwords, access controls, permissions, etc.)
        5. Email (business email systems, Outlook, Exchange, etc.)
        6. Database (business databases, data storage, SQL, etc.)
        7. Non-Technical (anything not related to business/office IT, including gaming consoles, personal devices, non-IT questions)
        
        Examples of Non-Technical:
        - Video game consoles, gaming devices
        - Personal entertainment devices
        - Home appliances
        - Car issues
        - General questions not related to business IT
        
        If the query is NOT related to business/office IT (category 7), respond with "Non-Technical".
        Otherwise, respond with the specific IT category number and name."""),
        ("user", "Query: {query}"),
    ])
    chain = prompt | ChatGroq(model="llama3-8b-8192", temperature=0.0)
    response = chain.invoke({"query": state["query"]}).content
    
    response_str = str(response)
    is_technical = "Non-Technical" not in response_str
    it_category = response_str if is_technical else "Non-Technical"
    
    return {
        "query": state["query"],
        "is_technical": is_technical,
        "it_category": it_category,
        "satisfaction_level": state.get("satisfaction_level"),
        "answer": state.get("answer"),
        "ticket_created": state.get("ticket_created", False),
        "interaction_count": state.get("interaction_count", 0) or 0
    }

# 2 - Provide general response for non-technical queries
def respond_general(state: NodeDeskState) -> NodeDeskState:
    """Provide general response for non-technical queries"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that responds to non-technical queries.
        
        Politely inform the user that you are a technical support assistant and can only help with IT-related issues.
        Ask them to please ask a technical question related to hardware, software, network, security, email, or database issues."""),
        ("user", "Query: {query}"),
    ])
    chain = prompt | ChatGroq(model="llama3-8b-8192", temperature=0.7)
    response = chain.invoke({"query": state["query"]}).content
    
    return {
        "query": state["query"],
        "is_technical": state["is_technical"],
        "it_category": state["it_category"],
        "satisfaction_level": state.get("satisfaction_level"),
        "answer": str(response),
        "ticket_created": state.get("ticket_created", False),
        "interaction_count": state.get("interaction_count", 0) or 0
    }

# 3 - Provide technical guidance
def provide_technical_guidance(state: NodeDeskState) -> NodeDeskState:
    """Provide technical guidance for IT-related queries"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful IT support assistant that provides technical guidance.
        
        Based on the IT category, provide step-by-step guidance to help the user resolve their issue.
        Be clear, concise, and helpful. If the issue requires hands-on intervention, mention that.
        
        Categories:
        - Hardware: Physical device issues
        - Software: Application and system issues  
        - Network: Connectivity and server issues
        - Security: Access and permission issues
        - Email: Email account and client issues
        - Database: Data and storage issues"""),
        ("user", "Query: {query}"),
        ("user", "IT Category: {it_category}"),
    ])
    chain = prompt | ChatGroq(model="llama3-8b-8192", temperature=0.3)
    response = chain.invoke({"query": state["query"], "it_category": state["it_category"]}).content
    
    return {
        "query": state["query"],
        "is_technical": state["is_technical"],
        "it_category": state["it_category"],
        "satisfaction_level": state.get("satisfaction_level"),
        "answer": str(response),
        "ticket_created": state.get("ticket_created", False),
        "interaction_count": state.get("interaction_count", 0) or 0
    }

# 4 - Check user satisfaction
def check_satisfaction(state: NodeDeskState) -> NodeDeskState:
    """Check if the user is satisfied with the provided guidance"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that determines user satisfaction.
        
        Based on the user's response, determine their satisfaction level:
        - "Satisfied": User indicates the solution worked or they're happy
        - "Unsatisfied": User indicates the solution didn't work or they need more help
        - "Neutral": User is asking follow-up questions or needs clarification
        
        Respond with ONLY: Satisfied, Unsatisfied, or Neutral"""),
        ("user", "User's response: {query}"),
    ])
    chain = prompt | ChatGroq(model="llama3-8b-8192", temperature=0.0)
    response = chain.invoke({"query": state["query"]}).content
    
    return {
        "query": state["query"],
        "is_technical": state["is_technical"],
        "it_category": state["it_category"],
        "satisfaction_level": str(response),
        "answer": state.get("answer"),
        "ticket_created": state.get("ticket_created", False),
        "interaction_count": state.get("interaction_count", 0) or 0
    }

# 5 - Create resolved ticket
def create_resolved_ticket(state: NodeDeskState) -> NodeDeskState:
    """Create a ticket marked as resolved by the agent"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that creates resolved tickets.
        
        Generate a brief summary of the issue that was resolved by the agent.
        Include the IT category and the solution provided."""),
        ("user", "Query: {query}"),
        ("user", "IT Category: {it_category}"),
        ("user", "Solution provided: {answer}"),
    ])
    chain = prompt | ChatGroq(model="llama3-8b-8192", temperature=0.0)
    response = chain.invoke({
        "query": state["query"], 
        "it_category": state["it_category"],
        "answer": state["answer"]
    }).content
    
    return {
        "query": state["query"],
        "is_technical": state["is_technical"],
        "it_category": state["it_category"],
        "satisfaction_level": state["satisfaction_level"],
        "answer": state["answer"],
        "ticket_created": True,
        "interaction_count": state.get("interaction_count", 0) or 0
    }

# 6 - Create escalation ticket
def create_escalation_ticket(state: NodeDeskState) -> NodeDeskState:
    """Create a ticket for escalation to human support"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that creates escalation tickets.
        
        Generate a brief summary of the issue that needs human intervention.
        Include the IT category and what was attempted."""),
        ("user", "Query: {query}"),
        ("user", "IT Category: {it_category}"),
        ("user", "Attempted solution: {answer}"),
    ])
    chain = prompt | ChatGroq(model="llama3-8b-8192", temperature=0.0)
    response = chain.invoke({
        "query": state["query"], 
        "it_category": state["it_category"],
        "answer": state["answer"]
    }).content
    
    return {
        "query": state["query"],
        "is_technical": state["is_technical"],
        "it_category": state["it_category"],
        "satisfaction_level": state["satisfaction_level"],
        "answer": state["answer"],
        "ticket_created": True,
        "interaction_count": state.get("interaction_count", 0) or 0
    }

# %%
# Routing function
def route_query(state: NodeDeskState) -> str:
    """Route the query to the correct node based on the current state"""
    
    # Force stop if too many interactions
    interaction_count = state.get("interaction_count", 0) or 0
    if interaction_count >= 5:  # Reduced limit to prevent infinite loops
        return "create_escalation_ticket"
    
    # First interaction - check if technical
    if state.get("is_technical") is None:
        return "check_technical_context"
    
    # Non-technical query
    if not state["is_technical"]:
        return "respond_general"
    
    # Technical query - provide guidance
    if state.get("answer") is None:
        return "provide_technical_guidance"
    
    # Check satisfaction after providing guidance
    if state.get("satisfaction_level") is None:
        return "check_satisfaction"
    
    # Route based on satisfaction
    if state["satisfaction_level"] == "Satisfied":
        return "create_resolved_ticket"
    elif state["satisfaction_level"] == "Unsatisfied":
        return "create_escalation_ticket"
    else:  # Neutral - escalate after too many attempts
        return "create_escalation_ticket"


# Main workflow function
def nodedesk_workflow(initial_query: str) -> NodeDeskState:
    """Main workflow for NodeDesk agent"""
    
    # Initialize state
    state: NodeDeskState = {
        "query": initial_query,
        "is_technical": None,
        "it_category": None,
        "satisfaction_level": None,
        "answer": None,
        "ticket_created": False,
        "interaction_count": 0
    }
    
    # Execute workflow
    while not state["ticket_created"]:
        next_node = route_query(state)
        print(f"\n➡️ Routing to: {next_node}")
        print(f"🧠 Current State: {state}")
        print(f"🔍 Current Interaction Count: {state.get('interaction_count', 0)}")
        
        if next_node == "check_technical_context":
            state = check_technical_context(state)
        elif next_node == "respond_general":
            state = respond_general(state)
        elif next_node == "provide_technical_guidance":
            state = provide_technical_guidance(state)
        elif next_node == "check_satisfaction":
            state = check_satisfaction(state)
        elif next_node == "create_resolved_ticket":
            state = create_resolved_ticket(state)
        elif next_node == "create_escalation_ticket":
            state = create_escalation_ticket(state)
        
        current_count = state.get("interaction_count", 0) or 0
        state["interaction_count"] = current_count + 1
        
        print(f"🔁 Interaction Count: {state['interaction_count']}")

        # Prevent infinite loops
        if state["interaction_count"] > 5:
            print("🚨 Max interactions reached! Escalating...")
            state = create_escalation_ticket(state)
            break
    
    return state

# %%

#Creating the workflow graph
workflow = StateGraph(NodeDeskState)

# Adding the nodes to the workflow graph
workflow.add_node("check_technical_context", check_technical_context)
workflow.add_node("respond_general", respond_general)
workflow.add_node("provide_technical_guidance", provide_technical_guidance)
workflow.add_node("check_satisfaction", check_satisfaction)
workflow.add_node("create_resolved_ticket", create_resolved_ticket)
workflow.add_node("create_escalation_ticket", create_escalation_ticket)

# Adding the edges to the workflow graph
workflow.add_edge(START, "check_technical_context")

# From check_technical_context, route based on if query is technical or not
workflow.add_conditional_edges(
    "check_technical_context",
    route_query,
    {
        "respond_general": "respond_general",  # Non-technical queries
        "provide_technical_guidance": "provide_technical_guidance"  # Technical queries
    }
)

# From respond_general (non-technical), create resolved ticket
workflow.add_edge("respond_general", "create_resolved_ticket")

# From technical guidance, check if user is satisfied
workflow.add_edge("provide_technical_guidance", "check_satisfaction")

# From satisfaction check, either resolve or escalate
workflow.add_conditional_edges(
    "check_satisfaction",
    route_query,
    {
        "create_resolved_ticket": "create_resolved_ticket",  # If satisfied
        "create_escalation_ticket": "create_escalation_ticket"  # If not satisfied or neutral
    }
)

# Terminal nodes
workflow.add_edge("create_resolved_ticket", END)
workflow.add_edge("create_escalation_ticket", END)

# Set entry point
workflow.set_entry_point("check_technical_context")

# Add an interrupt to trace entry into each node
app = workflow.compile()

def execute_nodedesk(query: str) -> dict:
    """Execute NodeDesk workflow using the original function approach"""
    try:
        # Use the original workflow function instead of the graph
        result = nodedesk_workflow(query)
        return {
            "query": query,
            "it_category": result.get("it_category"),
            "satisfaction_level": result.get("satisfaction_level"),
            "answer": result.get("answer")
        }
    except Exception as e:
        print("🚨 Exception caught:")
        print(e)
        raise  # Optional: re-raise to propagate the error



# Display the graph
display(
    Image(
        app.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API,
        )
    )
)

# %%
# test the workflow when the query is not technical
from pprint import pprint

query = "I have a problem with my video game console. It just won't turn on."
result = execute_nodedesk(query)
pprint({
    'query': query,
    'it_category': result['it_category'],
    "satisfaction_level": result["satisfaction_level"],
    'answer': result['answer']
}, width=80, sort_dicts=False)
print("\n")
# %%
