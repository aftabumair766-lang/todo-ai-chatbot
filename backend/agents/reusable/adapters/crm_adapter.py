"""
CRM Domain Adapter (Example)
=============================

Example domain adapter for Customer Relationship Management.

This demonstrates how the reusable agent framework can be configured
for a completely different domain (CRM vs Todo).

Usage:
    from backend.agents.reusable.core.reusable_agent import ReusableAgent
    from backend.agents.reusable.adapters.crm_adapter import CRMDomainAdapter

    agent = ReusableAgent(adapter=CRMDomainAdapter())
    result = await agent.process_message(user_id, message, history, db)

Comparison with TodoDomainAdapter:
    - Different system prompt (professional vs friendly)
    - Different tools (contacts, deals vs tasks)
    - Different formatting (formal vs emoji-heavy)
    - Different greeting response
    - Same underlying agent architecture

This proves the framework is truly domain-agnostic!
"""

from typing import Any, Dict, List, Optional, Callable
import logging
from backend.agents.reusable.adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)


class CRMDomainAdapter(DomainAdapter):
    """
    CRM-specific domain adapter.

    Configures the reusable agent for customer relationship management:
    - Professional tone (vs Todo's friendly emojis)
    - Contact and deal management tools
    - Formal response formatting
    """

    def get_system_prompt(self) -> str:
        """CRM Assistant system prompt - professional tone"""
        return """You are a professional CRM Assistant helping sales teams manage customer relationships.

**Your Capabilities:**
- Create and update customer contacts
- Track deals and opportunities
- Log interactions and notes
- Search and filter contacts by criteria
- Generate sales pipeline reports

**Conversation Style:**
- Professional and business-focused
- Provide clear, actionable information
- Ask clarifying questions for ambiguous requests
- Maintain data accuracy and completeness

**Contact Display Format:**
When listing contacts, use this format:
```
Contacts:
1. John Doe (Acme Corp) - john@acme.com - Deal: $50K (Negotiation)
2. Jane Smith (TechCo) - jane@techco.com - Deal: $25K (Proposal)
```

**Deal Pipeline Stages:**
- Lead: Initial contact
- Qualified: Needs confirmed
- Proposal: Quote sent
- Negotiation: In discussion
- Closed-Won: Deal won
- Closed-Lost: Deal lost

**Important:**
- Always verify contact information before creating duplicates
- Update deal stages promptly for accurate pipeline visibility
- Log all customer interactions for team visibility
- Never share sensitive customer data inappropriately
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """CRM-specific tool definitions (contacts, deals, interactions)"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_contact",
                    "description": "Create a new customer contact in the CRM",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Contact's full name"
                            },
                            "email": {
                                "type": "string",
                                "description": "Contact's email address"
                            },
                            "company": {
                                "type": "string",
                                "description": "Company name"
                            },
                            "phone": {
                                "type": "string",
                                "description": "Phone number (optional)"
                            }
                        },
                        "required": ["name", "email", "company"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_contacts",
                    "description": "List customer contacts with optional filtering",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "company": {
                                "type": "string",
                                "description": "Filter by company name (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_deal",
                    "description": "Create a new sales opportunity/deal",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "contact_id": {
                                "type": "integer",
                                "description": "Associated contact ID"
                            },
                            "title": {
                                "type": "string",
                                "description": "Deal title/description"
                            },
                            "amount": {
                                "type": "number",
                                "description": "Deal value in USD"
                            },
                            "stage": {
                                "type": "string",
                                "enum": ["lead", "qualified", "proposal", "negotiation", "closed-won", "closed-lost"],
                                "description": "Current pipeline stage"
                            }
                        },
                        "required": ["contact_id", "title", "amount", "stage"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_deal_stage",
                    "description": "Update the pipeline stage of a deal",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "deal_id": {
                                "type": "integer",
                                "description": "Deal ID"
                            },
                            "stage": {
                                "type": "string",
                                "enum": ["lead", "qualified", "proposal", "negotiation", "closed-won", "closed-lost"],
                                "description": "New pipeline stage"
                            }
                        },
                        "required": ["deal_id", "stage"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "log_interaction",
                    "description": "Log a customer interaction (call, email, meeting)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "contact_id": {
                                "type": "integer",
                                "description": "Contact ID"
                            },
                            "interaction_type": {
                                "type": "string",
                                "enum": ["call", "email", "meeting", "note"],
                                "description": "Type of interaction"
                            },
                            "notes": {
                                "type": "string",
                                "description": "Interaction notes/summary"
                            }
                        },
                        "required": ["contact_id", "interaction_type", "notes"]
                    }
                }
            }
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """Mapping of CRM tools to placeholder handlers"""
        return {
            "create_contact": self._create_contact_handler,
            "list_contacts": self._list_contacts_handler,
            "create_deal": self._create_deal_handler,
            "update_deal_stage": self._update_deal_stage_handler,
            "log_interaction": self._log_interaction_handler
        }

    # ============================================================================
    # TOOL HANDLERS (Placeholder implementations - would connect to real CRM DB)
    # ============================================================================

    async def _create_contact_handler(
        self,
        user_id: str,
        name: str,
        email: str,
        company: str,
        phone: Optional[str] = None,
        db=None
    ) -> Dict[str, Any]:
        """Create contact (placeholder - would use real CRM MCP tools)"""
        logger.info(f"CRM: Creating contact {name} at {company}")

        # This would call actual MCP tools:
        # from backend.mcp.crm_tools import create_contact as mcp_create_contact
        # result = await mcp_create_contact(...)

        # Placeholder response
        return {
            "success": True,
            "contact_id": 12345,
            "name": name,
            "email": email,
            "company": company,
            "message": f"Contact created: {name} ({company})"
        }

    async def _list_contacts_handler(
        self,
        user_id: str,
        company: Optional[str] = None,
        limit: int = 10,
        db=None
    ) -> Dict[str, Any]:
        """List contacts (placeholder)"""
        logger.info(f"CRM: Listing contacts (company={company}, limit={limit})")

        # Placeholder response
        return {
            "success": True,
            "contacts": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@acme.com",
                    "company": "Acme Corp",
                    "phone": "+1-555-0100"
                },
                {
                    "id": 2,
                    "name": "Jane Smith",
                    "email": "jane@techco.com",
                    "company": "TechCo",
                    "phone": "+1-555-0200"
                }
            ],
            "count": 2
        }

    async def _create_deal_handler(
        self,
        user_id: str,
        contact_id: int,
        title: str,
        amount: float,
        stage: str,
        db=None
    ) -> Dict[str, Any]:
        """Create deal (placeholder)"""
        logger.info(f"CRM: Creating deal '{title}' for contact {contact_id}")

        return {
            "success": True,
            "deal_id": 5678,
            "title": title,
            "amount": amount,
            "stage": stage,
            "message": f"Deal created: {title} (${amount:,.0f})"
        }

    async def _update_deal_stage_handler(
        self,
        user_id: str,
        deal_id: int,
        stage: str,
        db=None
    ) -> Dict[str, Any]:
        """Update deal stage (placeholder)"""
        logger.info(f"CRM: Updating deal {deal_id} to stage '{stage}'")

        return {
            "success": True,
            "deal_id": deal_id,
            "stage": stage,
            "message": f"Deal #{deal_id} moved to {stage}"
        }

    async def _log_interaction_handler(
        self,
        user_id: str,
        contact_id: int,
        interaction_type: str,
        notes: str,
        db=None
    ) -> Dict[str, Any]:
        """Log interaction (placeholder)"""
        logger.info(f"CRM: Logging {interaction_type} with contact {contact_id}")

        return {
            "success": True,
            "interaction_id": 9999,
            "contact_id": contact_id,
            "type": interaction_type,
            "message": f"Logged {interaction_type} interaction"
        }

    # ============================================================================
    # DOMAIN-SPECIFIC CUSTOMIZATIONS
    # ============================================================================

    def is_greeting(self, message: str) -> bool:
        """CRM greetings (more formal than Todo)"""
        formal_greetings = [
            "hello", "good morning", "good afternoon", "good evening", "greetings"
        ]
        message_lower = message.lower().strip()
        return message_lower in formal_greetings

    def get_greeting_response(self) -> Optional[str]:
        """Professional CRM greeting (no emojis)"""
        return (
            "Hello! I'm your CRM Assistant. "
            "I can help you manage contacts, track deals, and log customer interactions. "
            "What would you like to work on today?"
        )

    def format_response(self, response: str, context: Optional[Dict[str, Any]] = None) -> str:
        """CRM-specific formatting (minimal, professional)"""
        # Could add business-specific formatting here
        # For now, just return as-is
        return response

    def get_model_name(self) -> str:
        """Use GPT-4 Turbo for CRM (could use different model per domain)"""
        return "gpt-4-turbo-preview"

    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """Professional error messages (vs Todo's emoji warnings)"""
        return f"I encountered an error while processing your request: {str(error)}. Please try again or contact support."
