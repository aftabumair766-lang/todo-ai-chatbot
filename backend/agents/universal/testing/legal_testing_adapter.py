"""
Legal Testing Agent - Profession-Specific Testing Agent

A specialized testing agent for LEGAL DOCUMENTS:
- Tests legal documents for compliance, clarity, completeness, and risk
- Validates legal content from a legal professional's perspective

**What It Tests:**
1. Legal Compliance & Validity
2. Clause Completeness & Coverage
3. Legal Language Precision
4. Risk Assessment
5. Consistency & Cross-References
6. Enforceability
7. Jurisdiction Requirements
8. Standard Compliance

**Use Cases:**
- Test contracts for completeness
- Review constitutions for legal validity
- Analyze agreements for risks
- Validate legal clause consistency
- Check compliance with regulations

**Example Usage:**
```python
from backend.agents.universal.testing.legal_testing_adapter import LegalTestingAgent
from backend.agents.reusable import ReusableAgent

legal_tester = ReusableAgent(adapter=LegalTestingAgent())

# Test contract
result = await legal_tester.process_message(
    user_id="lawyer_1",
    message="Test this employment contract for completeness, legal risks, and enforceability",
    conversation_history=[],
    db=None
)

# Test constitution
result = await legal_tester.process_message(
    user_id="constitutional_1",
    message="Test this constitution draft for legal validity, clause consistency, and completeness",
    conversation_history=[],
    db=None
)
```

Author: AI Agent System
Created: 2024
License: Same as parent project
"""

import logging
from typing import List, Dict, Any, Callable, Optional
from backend.agents.reusable.adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)


class LegalTestingAgent(DomainAdapter):
    """
    Legal Testing Agent - Tests legal documents for compliance and quality
    """

    def __init__(
        self,
        strictness: str = "strict",
        jurisdiction: str = "US",
        document_standards: Optional[List[str]] = None,
        risk_tolerance: str = "low"
    ):
        """
        Initialize Legal Testing Agent.

        Args:
            strictness: Testing strictness (lenient, balanced, strict, regulatory)
            jurisdiction: Legal jurisdiction (US, UK, EU, International, etc.)
            document_standards: Legal standards to check against (ABA, ISO, custom)
            risk_tolerance: Risk tolerance level (very_low, low, medium, high)
        """
        self.strictness = strictness
        self.jurisdiction = jurisdiction
        self.document_standards = document_standards or ["general"]
        self.risk_tolerance = risk_tolerance

        logger.info(
            f"LegalTestingAgent initialized with strictness={strictness}, "
            f"jurisdiction={jurisdiction}, standards={document_standards}, risk={risk_tolerance}"
        )

    def get_system_prompt(self) -> str:
        """System prompt for Legal Testing Agent."""
        return f"""You are a world-class legal expert, contract specialist, and compliance officer with expertise in reviewing and validating legal documents.

**Your Role:**
Test and validate legal documents for compliance, completeness, clarity, and risk management.

**What You Test:**

1. **Legal Compliance & Validity:**
   - Compliance with applicable laws and regulations
   - Jurisdictional requirements ({self.jurisdiction})
   - Statutory compliance
   - Regulatory adherence
   - Constitutional validity
   - Legal precedent alignment
   - Industry-specific regulations

2. **Clause Completeness & Coverage:**
   - Essential clauses present (definitions, parties, terms, obligations, termination, dispute resolution)
   - Missing critical provisions
   - Standard clause requirements
   - Boilerplate completeness (severability, entire agreement, amendments, notices)
   - Special provisions for document type
   - Exhibits and schedules completeness

3. **Legal Language Precision:**
   - Legal terminology accuracy
   - Defined terms consistency
   - Ambiguous language identification
   - Vague or unclear provisions
   - Conflicting terms
   - "Shall" vs "may" vs "will" usage
   - Precision of obligations and rights

4. **Risk Assessment:**
   - Liability exposure
   - Indemnification adequacy
   - Limitation of liability clauses
   - Force majeure provisions
   - Dispute resolution mechanisms
   - Breach remedies
   - Enforcement challenges
   - Compliance risks

5. **Consistency & Cross-References:**
   - Internal consistency
   - Cross-reference accuracy
   - Defined term usage
   - Clause numbering integrity
   - Exhibit references
   - Date consistency
   - Party name consistency

6. **Enforceability:**
   - Legal enforceability assessment
   - Unconscionability check
   - Consideration adequacy
   - Capacity and authority
   - Mutual assent clarity
   - Illegal provisions identification
   - Public policy violations

7. **Jurisdiction Requirements:**
   - Governing law clause
   - Venue and jurisdiction provisions
   - Choice of law appropriateness
   - Forum selection clauses
   - International considerations
   - Conflict of laws analysis

8. **Standard Compliance:**
   - Industry standard compliance
   - Best practice adherence
   - Professional guidelines
   - Template requirements
   - Formatting standards
   - Execution requirements (signatures, dates, witnesses)

**Testing Standards:**
- 🔴 **Critical Issues**: Must fix (invalid provisions, missing essential clauses, high legal risk)
- 🟡 **Major Issues**: Should fix (ambiguous language, incomplete provisions, moderate risk)
- 🟢 **Minor Issues**: Consider fixing (formatting, minor ambiguities, style improvements)
- 💡 **Suggestions**: Best practice recommendations (additional protections, clarifications)

**Current Configuration:**
- Strictness: {self.strictness}
- Jurisdiction: {self.jurisdiction}
- Document Standards: {', '.join(self.document_standards)}
- Risk Tolerance: {self.risk_tolerance}

**How You Work:**
1. Identify document type and purpose
2. Check compliance with jurisdiction requirements
3. Verify essential clauses and completeness
4. Analyze legal language precision
5. Assess legal risks and liabilities
6. Validate consistency and cross-references
7. Evaluate enforceability
8. Generate comprehensive legal test report

**IMPORTANT DISCLAIMERS:**
- This is AI-assisted review, not legal advice
- Human legal professional review is required
- Jurisdiction-specific rules may not be fully covered
- Does not replace licensed attorney review
- For informational purposes only

You are thorough, precise, and focused on identifying legal issues and risks to protect the parties involved.
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """Define testing tools for legal documents."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "check_compliance",
                    "description": "Check legal compliance with laws, regulations, and standards.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document": {"type": "string", "description": "Legal document to check"},
                            "document_type": {"type": "string", "enum": ["contract", "constitution", "agreement", "policy", "terms", "statute", "regulation"]},
                            "jurisdiction": {"type": "string"},
                            "regulations": {"type": "array", "items": {"type": "string"}},
                            "assess_validity": {"type": "boolean"}
                        },
                        "required": ["document", "document_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_completeness",
                    "description": "Verify all essential clauses and provisions are present.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document": {"type": "string"},
                            "document_type": {"type": "string"},
                            "required_clauses": {"type": "array", "items": {"type": "string"}},
                            "check_boilerplate": {"type": "boolean"},
                            "check_exhibits": {"type": "boolean"}
                        },
                        "required": ["document", "document_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_legal_language",
                    "description": "Analyze legal language for precision, clarity, and consistency.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document": {"type": "string"},
                            "check_ambiguity": {"type": "boolean"},
                            "check_defined_terms": {"type": "boolean"},
                            "check_modal_verbs": {"type": "boolean"},
                            "identify_conflicts": {"type": "boolean"}
                        },
                        "required": ["document"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assess_legal_risk",
                    "description": "Assess legal risks, liabilities, and exposure.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document": {"type": "string"},
                            "document_type": {"type": "string"},
                            "party_perspective": {"type": "string", "description": "Which party's perspective to analyze from"},
                            "risk_categories": {"type": "array", "items": {"type": "string", "enum": ["liability", "indemnification", "breach", "compliance", "enforcement", "dispute"]}},
                            "suggest_mitigations": {"type": "boolean"}
                        },
                        "required": ["document"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_consistency",
                    "description": "Validate internal consistency and cross-references.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document": {"type": "string"},
                            "check_cross_references": {"type": "boolean"},
                            "check_defined_terms": {"type": "boolean"},
                            "check_dates": {"type": "boolean"},
                            "check_parties": {"type": "boolean"},
                            "check_numbering": {"type": "boolean"}
                        },
                        "required": ["document"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "evaluate_enforceability",
                    "description": "Evaluate legal enforceability of provisions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document": {"type": "string"},
                            "jurisdiction": {"type": "string"},
                            "check_consideration": {"type": "boolean"},
                            "check_capacity": {"type": "boolean"},
                            "check_legality": {"type": "boolean"},
                            "identify_unenforceable": {"type": "boolean"}
                        },
                        "required": ["document"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "review_jurisdiction",
                    "description": "Review jurisdiction and governing law provisions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document": {"type": "string"},
                            "parties_locations": {"type": "array", "items": {"type": "string"}},
                            "transaction_location": {"type": "string"},
                            "check_governing_law": {"type": "boolean"},
                            "check_venue": {"type": "boolean"},
                            "check_conflicts": {"type": "boolean"}
                        },
                        "required": ["document"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_standards",
                    "description": "Verify compliance with legal document standards and best practices.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document": {"type": "string"},
                            "document_type": {"type": "string"},
                            "standards": {"type": "array", "items": {"type": "string"}},
                            "check_formatting": {"type": "boolean"},
                            "check_execution": {"type": "boolean"}
                        },
                        "required": ["document", "document_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_legal_report",
                    "description": "Generate comprehensive legal document testing report.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document_title": {"type": "string"},
                            "document_type": {"type": "string"},
                            "test_results": {"type": "object"},
                            "report_format": {"type": "string", "enum": ["summary", "detailed", "comprehensive", "executive"]},
                            "include_risk_matrix": {"type": "boolean"},
                            "include_recommendations": {"type": "boolean"}
                        },
                        "required": ["document_title", "document_type"]
                    }
                }
            }
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """Map tool names to handlers."""
        return {
            "check_compliance": self._check_compliance,
            "verify_completeness": self._verify_completeness,
            "analyze_legal_language": self._analyze_legal_language,
            "assess_legal_risk": self._assess_legal_risk,
            "validate_consistency": self._validate_consistency,
            "evaluate_enforceability": self._evaluate_enforceability,
            "review_jurisdiction": self._review_jurisdiction,
            "verify_standards": self._verify_standards,
            "generate_legal_report": self._generate_legal_report
        }

    async def _check_compliance(self, user_id: str, document: str, document_type: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Checking compliance for {document_type}")
        return {
            "success": True,
            "document_type": document_type,
            "document_length": len(document),
            "jurisdiction": kwargs.get("jurisdiction", self.jurisdiction),
            "regulations": kwargs.get("regulations", []),
            "message": f"Compliance check completed for {document_type}",
            "note": "Compliance analysis in conversation response"
        }

    async def _verify_completeness(self, user_id: str, document: str, document_type: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Verifying completeness for {document_type}")
        return {
            "success": True,
            "document_type": document_type,
            "document_length": len(document),
            "required_clauses": kwargs.get("required_clauses", []),
            "message": f"Completeness verification for {document_type} completed",
            "note": "Missing clauses and provisions in conversation response"
        }

    async def _analyze_legal_language(self, user_id: str, document: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Analyzing legal language ({len(document)} chars)")
        return {
            "success": True,
            "document_length": len(document),
            "checks": ["ambiguity", "defined_terms", "modal_verbs", "conflicts"],
            "message": "Legal language analysis completed",
            "note": "Language issues and recommendations in conversation response"
        }

    async def _assess_legal_risk(self, user_id: str, document: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Assessing legal risk")
        return {
            "success": True,
            "document_length": len(document),
            "party_perspective": kwargs.get("party_perspective"),
            "risk_categories": kwargs.get("risk_categories", ["all"]),
            "risk_tolerance": self.risk_tolerance,
            "message": "Legal risk assessment completed",
            "note": "Risk analysis and mitigation recommendations in conversation response"
        }

    async def _validate_consistency(self, user_id: str, document: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Validating consistency")
        return {
            "success": True,
            "document_length": len(document),
            "checks": ["cross_references", "defined_terms", "dates", "parties", "numbering"],
            "message": "Consistency validation completed",
            "note": "Consistency issues in conversation response"
        }

    async def _evaluate_enforceability(self, user_id: str, document: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Evaluating enforceability")
        return {
            "success": True,
            "document_length": len(document),
            "jurisdiction": kwargs.get("jurisdiction", self.jurisdiction),
            "checks": ["consideration", "capacity", "legality"],
            "message": "Enforceability evaluation completed",
            "note": "Enforceability analysis in conversation response"
        }

    async def _review_jurisdiction(self, user_id: str, document: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Reviewing jurisdiction provisions")
        return {
            "success": True,
            "document_length": len(document),
            "parties_locations": kwargs.get("parties_locations", []),
            "message": "Jurisdiction review completed",
            "note": "Jurisdiction analysis in conversation response"
        }

    async def _verify_standards(self, user_id: str, document: str, document_type: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Verifying standards for {document_type}")
        return {
            "success": True,
            "document_type": document_type,
            "document_length": len(document),
            "standards": kwargs.get("standards", self.document_standards),
            "message": f"Standards verification for {document_type} completed",
            "note": "Standards compliance report in conversation response"
        }

    async def _generate_legal_report(self, user_id: str, document_title: str, document_type: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Generating legal report for '{document_title}'")
        return {
            "success": True,
            "document_title": document_title,
            "document_type": document_type,
            "report_format": kwargs.get("report_format", "detailed"),
            "strictness": self.strictness,
            "jurisdiction": self.jurisdiction,
            "message": f"Legal testing report generated for '{document_title}'",
            "note": "Comprehensive legal analysis report in conversation response"
        }

    def get_greeting_message(self) -> str:
        return (
            "👋 Hello! I'm your Legal Testing Agent.\n\n"
            "I specialize in testing legal documents for:\n"
            "• ⚖️ Legal compliance and validity\n"
            "• 📋 Clause completeness and coverage\n"
            "• 📝 Legal language precision\n"
            "• ⚠️ Risk assessment and mitigation\n"
            "• 🔍 Consistency and cross-references\n"
            "• ✅ Enforceability evaluation\n"
            "• 🌍 Jurisdiction requirements\n"
            "• 📊 Standards compliance\n\n"
            "⚠️ Note: AI-assisted review only - human legal review required\n\n"
            "What legal document would you like me to test?"
        )


__all__ = ["LegalTestingAgent"]
