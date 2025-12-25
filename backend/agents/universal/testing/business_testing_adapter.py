"""
Business Testing Agent - Profession-Specific Testing Agent

A specialized testing agent for BUSINESS DOCUMENTS:
- Tests business plans, strategies, financial projections for viability and quality
- Validates business content from a business professional's perspective

**What It Tests:**
1. Business Strategy Viability
2. Financial Projections Realism
3. Market Analysis Depth
4. Competitive Positioning
5. Operational Feasibility
6. Risk Assessment & Mitigation
7. Revenue Model Soundness
8. Growth Plan Credibility

**Use Cases:**
- Test business plans for investor readiness
- Review financial projections for realism
- Analyze market strategy for soundness
- Validate business assumptions
- Check operational plans

**Example Usage:**
```python
from backend.agents.universal.testing.business_testing_adapter import BusinessTestingAgent
from backend.agents.reusable import ReusableAgent

business_tester = ReusableAgent(adapter=BusinessTestingAgent())

# Test business plan
result = await business_tester.process_message(
    user_id="entrepreneur_1",
    message="Test this business plan for financial realism, market analysis, and investor readiness",
    conversation_history=[],
    db=None
)

# Review marketing strategy
result = await business_tester.process_message(
    user_id="marketer_1",
    message="Review this go-to-market strategy for competitive positioning and execution feasibility",
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


class BusinessTestingAgent(DomainAdapter):
    """
    Business Testing Agent - Tests business plans and strategies for viability
    """

    def __init__(
        self,
        strictness: str = "balanced",
        business_stage: str = "startup",
        focus_areas: Optional[List[str]] = None,
        financial_rigor: str = "moderate"
    ):
        """
        Initialize Business Testing Agent.

        Args:
            strictness: Testing strictness (lenient, balanced, strict, investor_grade)
            business_stage: Business stage (idea, startup, growth, enterprise)
            focus_areas: Areas to focus on (strategy, financial, market, operations, risk)
            financial_rigor: Financial analysis rigor (basic, moderate, rigorous, forensic)
        """
        self.strictness = strictness
        self.business_stage = business_stage
        self.focus_areas = focus_areas or ["strategy", "financial", "market", "operations", "risk"]
        self.financial_rigor = financial_rigor

        logger.info(
            f"BusinessTestingAgent initialized with strictness={strictness}, "
            f"stage={business_stage}, focus={focus_areas}, financial_rigor={financial_rigor}"
        )

    def get_system_prompt(self) -> str:
        """System prompt for Business Testing Agent."""
        return f"""You are a world-class business strategist, financial analyst, and management consultant with expertise in evaluating business plans and strategies.

**Your Role:**
Test and validate business plans, strategies, and financial projections for viability, soundness, and execution potential.

**What You Test:**

1. **Business Strategy Viability:**
   - Value proposition clarity
   - Business model soundness
   - Strategic positioning
   - Competitive advantages (moat)
   - Strategic goals alignment
   - Differentiation strategy
   - Market timing
   - Scalability potential

2. **Financial Projections Realism:**
   - Revenue assumptions (rigor: {self.financial_rigor})
   - Cost structure accuracy
   - Profitability timeline
   - Cash flow projections
   - Unit economics
   - Burn rate & runway
   - Financial metrics (CAC, LTV, margins, etc.)
   - Break-even analysis

3. **Market Analysis Depth:**
   - Market size estimation (TAM, SAM, SOM)
   - Market trends analysis
   - Customer segmentation
   - Target market definition
   - Market research quality
   - Customer pain points validation
   - Market entry barriers
   - Market growth potential

4. **Competitive Positioning:**
   - Competitive landscape analysis
   - Competitive advantages
   - Barriers to entry
   - SWOT analysis quality
   - Competitive strategy
   - Market share assumptions
   - Differentiation factors
   - Competitive response planning

5. **Operational Feasibility:**
   - Operations plan realism
   - Resource requirements
   - Team capabilities
   - Technology infrastructure
   - Supply chain planning
   - Scalability roadmap
   - Key partnerships
   - Execution timeline

6. **Risk Assessment & Mitigation:**
   - Risk identification completeness
   - Risk severity assessment
   - Mitigation strategies
   - Contingency planning
   - Regulatory risks
   - Market risks
   - Operational risks
   - Financial risks

7. **Revenue Model Soundness:**
   - Revenue streams clarity
   - Pricing strategy
   - Customer acquisition strategy
   - Sales process definition
   - Revenue growth assumptions
   - Monetization strategy
   - Customer retention plans
   - Upsell/cross-sell opportunities

8. **Growth Plan Credibility:**
   - Growth strategy clarity
   - Scaling plan realism
   - Milestone definition
   - Resource scaling plans
   - Market expansion strategy
   - Partnership strategy
   - Exit strategy (if applicable)
   - Long-term vision

**Testing Standards:**
- 🔴 **Critical Issues**: Must fix (unrealistic projections, flawed assumptions, missing critical elements)
- 🟡 **Major Issues**: Should fix (weak analysis, incomplete planning, moderate risks)
- 🟢 **Minor Issues**: Consider fixing (presentation, minor assumptions, clarifications)
- 💡 **Suggestions**: Enhancement opportunities (additional analysis, strategic refinements)

**Current Configuration:**
- Strictness: {self.strictness}
- Business Stage: {self.business_stage}
- Focus Areas: {', '.join(self.focus_areas)}
- Financial Rigor: {self.financial_rigor}

**How You Work:**
1. Assess business model and value proposition
2. Evaluate market opportunity and analysis
3. Review financial projections and assumptions
4. Analyze competitive positioning
5. Assess operational feasibility
6. Evaluate growth strategy
7. Review risk assessment and mitigation
8. Generate comprehensive business validation report

You are thorough, realistic, and focused on helping entrepreneurs and business leaders create viable, executable business strategies.
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """Define testing tools for business documents."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "evaluate_strategy",
                    "description": "Evaluate business strategy viability and soundness.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "business_plan": {"type": "string"},
                            "business_model": {"type": "string", "enum": ["B2B", "B2C", "B2B2C", "marketplace", "SaaS", "subscription", "freemium", "enterprise"]},
                            "industry": {"type": "string"},
                            "check_value_prop": {"type": "boolean"},
                            "check_differentiation": {"type": "boolean"},
                            "assess_moat": {"type": "boolean"}
                        },
                        "required": ["business_plan"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_financials",
                    "description": "Validate financial projections and assumptions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "financial_projections": {"type": "string"},
                            "projection_period": {"type": "string"},
                            "check_revenue": {"type": "boolean"},
                            "check_costs": {"type": "boolean"},
                            "check_cash_flow": {"type": "boolean"},
                            "check_unit_economics": {"type": "boolean"},
                            "assess_assumptions": {"type": "boolean"}
                        },
                        "required": ["financial_projections"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_market",
                    "description": "Analyze market opportunity and market analysis quality.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "market_analysis": {"type": "string"},
                            "target_market": {"type": "string"},
                            "check_market_size": {"type": "boolean"},
                            "check_segmentation": {"type": "boolean"},
                            "check_trends": {"type": "boolean"},
                            "validate_research": {"type": "boolean"}
                        },
                        "required": ["market_analysis"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assess_competition",
                    "description": "Assess competitive positioning and analysis.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "competitive_analysis": {"type": "string"},
                            "key_competitors": {"type": "array", "items": {"type": "string"}},
                            "check_landscape": {"type": "boolean"},
                            "check_advantages": {"type": "boolean"},
                            "assess_swot": {"type": "boolean"},
                            "validate_differentiation": {"type": "boolean"}
                        },
                        "required": ["competitive_analysis"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "review_operations",
                    "description": "Review operational plan and feasibility.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "operations_plan": {"type": "string"},
                            "business_stage": {"type": "string"},
                            "check_resources": {"type": "boolean"},
                            "check_team": {"type": "boolean"},
                            "check_scalability": {"type": "boolean"},
                            "assess_timeline": {"type": "boolean"}
                        },
                        "required": ["operations_plan"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "evaluate_risks",
                    "description": "Evaluate risk assessment and mitigation strategies.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "business_plan": {"type": "string"},
                            "risk_section": {"type": "string"},
                            "risk_types": {"type": "array", "items": {"type": "string", "enum": ["market", "financial", "operational", "regulatory", "competitive", "technology"]}},
                            "assess_completeness": {"type": "boolean"},
                            "check_mitigation": {"type": "boolean"},
                            "assess_contingency": {"type": "boolean"}
                        },
                        "required": ["business_plan"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_revenue_model",
                    "description": "Validate revenue model and monetization strategy.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "revenue_model": {"type": "string"},
                            "pricing_strategy": {"type": "string"},
                            "check_streams": {"type": "boolean"},
                            "check_pricing": {"type": "boolean"},
                            "check_acquisition": {"type": "boolean"},
                            "assess_retention": {"type": "boolean"}
                        },
                        "required": ["revenue_model"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assess_growth_plan",
                    "description": "Assess growth strategy and scaling plan.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "growth_plan": {"type": "string"},
                            "target_growth_rate": {"type": "string"},
                            "check_strategy": {"type": "boolean"},
                            "check_milestones": {"type": "boolean"},
                            "check_scaling": {"type": "boolean"},
                            "assess_realism": {"type": "boolean"}
                        },
                        "required": ["growth_plan"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_business_report",
                    "description": "Generate comprehensive business validation report.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "business_name": {"type": "string"},
                            "test_results": {"type": "object"},
                            "investor_ready": {"type": "boolean"},
                            "report_format": {"type": "string", "enum": ["summary", "detailed", "comprehensive", "investor_grade"]},
                            "include_scores": {"type": "boolean"},
                            "provide_recommendations": {"type": "boolean"}
                        },
                        "required": ["business_name"]
                    }
                }
            }
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """Map tool names to handlers."""
        return {
            "evaluate_strategy": self._evaluate_strategy,
            "validate_financials": self._validate_financials,
            "analyze_market": self._analyze_market,
            "assess_competition": self._assess_competition,
            "review_operations": self._review_operations,
            "evaluate_risks": self._evaluate_risks,
            "validate_revenue_model": self._validate_revenue_model,
            "assess_growth_plan": self._assess_growth_plan,
            "generate_business_report": self._generate_business_report
        }

    async def _evaluate_strategy(self, user_id: str, business_plan: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Evaluating business strategy ({len(business_plan)} chars)")
        return {
            "success": True,
            "plan_length": len(business_plan),
            "business_model": kwargs.get("business_model"),
            "industry": kwargs.get("industry"),
            "checks": ["value_prop", "differentiation", "moat"],
            "message": "Business strategy evaluation completed",
            "note": "Strategy viability analysis in conversation response"
        }

    async def _validate_financials(self, user_id: str, financial_projections: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Validating financial projections")
        return {
            "success": True,
            "projections_length": len(financial_projections),
            "projection_period": kwargs.get("projection_period"),
            "financial_rigor": self.financial_rigor,
            "checks": ["revenue", "costs", "cash_flow", "unit_economics", "assumptions"],
            "message": "Financial validation completed",
            "note": "Financial projection analysis in conversation response"
        }

    async def _analyze_market(self, user_id: str, market_analysis: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Analyzing market opportunity")
        return {
            "success": True,
            "analysis_length": len(market_analysis),
            "target_market": kwargs.get("target_market"),
            "checks": ["market_size", "segmentation", "trends", "research"],
            "message": "Market analysis completed",
            "note": "Market opportunity assessment in conversation response"
        }

    async def _assess_competition(self, user_id: str, competitive_analysis: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Assessing competitive positioning")
        return {
            "success": True,
            "analysis_length": len(competitive_analysis),
            "competitors": kwargs.get("key_competitors", []),
            "checks": ["landscape", "advantages", "swot", "differentiation"],
            "message": "Competitive assessment completed",
            "note": "Competitive positioning analysis in conversation response"
        }

    async def _review_operations(self, user_id: str, operations_plan: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Reviewing operational plan")
        return {
            "success": True,
            "plan_length": len(operations_plan),
            "business_stage": kwargs.get("business_stage", self.business_stage),
            "checks": ["resources", "team", "scalability", "timeline"],
            "message": "Operations review completed",
            "note": "Operational feasibility analysis in conversation response"
        }

    async def _evaluate_risks(self, user_id: str, business_plan: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Evaluating business risks")
        return {
            "success": True,
            "plan_length": len(business_plan),
            "risk_types": kwargs.get("risk_types", ["all"]),
            "checks": ["completeness", "mitigation", "contingency"],
            "message": "Risk evaluation completed",
            "note": "Risk assessment and mitigation analysis in conversation response"
        }

    async def _validate_revenue_model(self, user_id: str, revenue_model: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Validating revenue model")
        return {
            "success": True,
            "model_length": len(revenue_model),
            "pricing_strategy": kwargs.get("pricing_strategy"),
            "checks": ["streams", "pricing", "acquisition", "retention"],
            "message": "Revenue model validation completed",
            "note": "Revenue model analysis in conversation response"
        }

    async def _assess_growth_plan(self, user_id: str, growth_plan: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Assessing growth plan")
        return {
            "success": True,
            "plan_length": len(growth_plan),
            "target_growth": kwargs.get("target_growth_rate"),
            "checks": ["strategy", "milestones", "scaling", "realism"],
            "message": "Growth plan assessment completed",
            "note": "Growth strategy analysis in conversation response"
        }

    async def _generate_business_report(self, user_id: str, business_name: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Generating business report for '{business_name}'")
        return {
            "success": True,
            "business_name": business_name,
            "investor_ready": kwargs.get("investor_ready", False),
            "report_format": kwargs.get("report_format", "detailed"),
            "strictness": self.strictness,
            "business_stage": self.business_stage,
            "focus_areas": self.focus_areas,
            "message": f"Business validation report generated for '{business_name}'",
            "note": "Comprehensive business analysis report in conversation response"
        }

    def get_greeting_message(self) -> str:
        return (
            "👋 Hello! I'm your Business Testing Agent.\n\n"
            "I specialize in testing business plans for:\n"
            "• 💡 Business strategy viability\n"
            "• 💰 Financial projection realism\n"
            "• 📊 Market analysis depth\n"
            "• 🎯 Competitive positioning\n"
            "• ⚙️ Operational feasibility\n"
            "• ⚠️ Risk assessment & mitigation\n"
            "• 💵 Revenue model soundness\n"
            "• 📈 Growth plan credibility\n\n"
            "What business plan would you like me to test?"
        )


__all__ = ["BusinessTestingAgent"]
