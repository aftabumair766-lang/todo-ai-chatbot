"""
Reusable AI Agent Framework
============================

A domain-agnostic agent framework that can be configured for any use case:
- Todo Management
- CRM Systems
- E-commerce
- Support Chatbots
- Workflow Automation

Usage:
    from backend.agents.reusable import ReusableAgent, TodoDomainAdapter

    # Create agent with domain adapter
    agent = ReusableAgent(adapter=TodoDomainAdapter())

    # Use agent
    result = await agent.process_message(
        user_id="user123",
        message="Add a task",
        conversation_history=[],
        db=db_session
    )

    print(result["response"])  # "✅ Task added: ..."

Example - Switch to CRM domain:
    from backend.agents.reusable import ReusableAgent, CRMDomainAdapter

    # Same agent, different domain!
    crm_agent = ReusableAgent(adapter=CRMDomainAdapter())

    result = await crm_agent.process_message(
        user_id="sales_rep_1",
        message="Create contact for John Doe at Acme Corp",
        conversation_history=[],
        db=db_session
    )

    print(result["response"])  # "Contact created: John Doe (Acme Corp)"
"""

from backend.agents.reusable.core.reusable_agent import ReusableAgent
from backend.agents.reusable.adapters.base_adapter import DomainAdapter
from backend.agents.reusable.adapters.todo_adapter import TodoDomainAdapter
from backend.agents.reusable.adapters.crm_adapter import CRMDomainAdapter

__all__ = [
    "ReusableAgent",
    "DomainAdapter",
    "TodoDomainAdapter",
    "CRMDomainAdapter"
]
