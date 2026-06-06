from typing import TypedDict, Literal
from langchain_core.messages import HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
import os
from dotenv import load_dotenv

load_dotenv()

class State(TypedDict):
    """Shared memory/state passed between all nodes in the graph"""
    user_query: str
    category: Literal["billing", "technical", "unknown"]
    final_response: str

def triage_input(state: State):
    """Analyzes the input and categorizes it using an LLM."""
    print("-- NODE: Triaging Input --")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_retries=6
    )

    prompt = (
        f"Classify the following customer queri into exactly one of these categories: "
        f"'billing' or 'technical'. Respond with ONLY the category name.\n\n"
        f"Query: {state['user_query']}"
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    category = response.content.strip().lower()

    if category not in ["billing", "technical"]:
        category = "unknown"

    return {"category": category}


def handle_billing(state: State):
    """Specific node handling billing complaints."""
    print("-- NODE: Handling Billing Issue ---")

    response_text = "Billing System Note: Forwarding your invoice discrepancy to our accounting department."

    return {"final_response": response_text}

def handle_technical(state: State):
    """Specific node handling software or bug issues."""
    print("-- NODE: Handling Technical Issue --")

    response_text = "Technical Support Note: Opening an internal engineering ticket for our system logs."

    return {"final_response": response_text}


def route_by_category(state: State) -> Literal["billing_node", "tech_node", END]:
    """Inspect state and dictates which edge node to invoke next."""
    if state["category"] == "billing":
        return "billing_node"
    elif state["category"] == "technical":
        return "tech_node"
    else:
        return END

# Build node graph with edges
builder = StateGraph(state_schema=State)

builder.add_node("triage_node", triage_input)
builder.add_node("billing_node", handle_billing)
builder.add_node("tech_node", handle_technical)

builder.add_edge(START, "triage_node")

builder.add_conditional_edges(
    "triage_node",
    route_by_category,
    {
        "billing_node": "billing_node",
        "tech_node": "tech_node",
        END: END
    }
)

builder.add_edge("billing_node", END)
builder.add_edge("tech_node", END)

workflow = builder.compile()

# Execute workflow
if __name__ == "__main__":
    input_state_1 = {"user_query": "The mobile application crashes every time I tap upload."}
    print("--- RUNNING TECH WORKFLOW ---")
    output_1 = workflow.invoke(input_state_1)
    print(f"Final Category: {output_1['category']}")
    print(f"Final Output:   {output_1['final_response']}\n")

    # Test Case 2: Triggering the Billing branch
    input_state_2 = {"user_query": "Why was I charged $49 dollars twice this month?"}
    print("--- RUNNING BILLING WORKFLOW ---")
    output_2 = workflow.invoke(input_state_2)
    print(f"Final Category: {output_2['category']}")
    print(f"Final Output:   {output_2['final_response']}\n")
