"""
Quality Assurance Agent - Universal Reusable Agent

A comprehensive quality assurance and review agent that works across ALL projects:
- Book writing, Constitution drafting, Software documentation, Academic papers, Business documents, etc.

**Capabilities:**
1. Content Review & Editing
2. Grammar & Spelling Checking
3. Consistency Validation
4. Structure & Organization Review
5. Readability Assessment
6. Completeness Checking
7. Cross-Reference Validation
8. Quality Reporting

**Use Cases:**
- Book Writing: Proofread chapters, check consistency, assess readability, verify structure
- Constitution: Review legal language, check clause consistency, validate references
- Software Documentation: Check technical accuracy, verify code examples, assess clarity
- Academic Papers: Review methodology, check citations, assess academic rigor
- Business Documents: Review professionalism, check data accuracy, assess persuasiveness

**Example Usage:**
```python
from backend.agents.universal.adapters.qa_adapter import QAAgent
from backend.agents.reusable import ReusableAgent

qa_agent = ReusableAgent(adapter=QAAgent())

# Review book chapter
result = await qa_agent.process_message(
    user_id="author_1",
    message="Review this chapter for grammar, clarity, and consistency with previous chapters",
    conversation_history=[],
    db=None
)

# Check document completeness
result = await qa_agent.process_message(
    user_id="legal_1",
    message="Check if this constitution draft includes all required sections and clauses",
    conversation_history=[],
    db=None
)

# Assess readability
result = await qa_agent.process_message(
    user_id="writer_1",
    message="Assess the readability of this technical documentation for non-technical users",
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


class QAAgent(DomainAdapter):
    """
    Universal Quality Assurance Agent

    Provides comprehensive quality review and validation capabilities across all domains.
    """

    def __init__(
        self,
        strictness_level: str = "balanced",
        focus_areas: Optional[List[str]] = None,
        target_readability: str = "general_audience",
        auto_fix_suggestions: bool = True
    ):
        """
        Initialize QA Agent with customizable settings.

        Args:
            strictness_level: Review strictness (lenient, balanced, strict, very_strict)
            focus_areas: Specific areas to focus on (grammar, style, consistency, accuracy, structure)
            target_readability: Target audience level (academic, professional, general_audience, simplified)
            auto_fix_suggestions: Whether to provide specific fix suggestions
        """
        self.strictness_level = strictness_level
        self.focus_areas = focus_areas or ["grammar", "style", "consistency", "accuracy", "structure"]
        self.target_readability = target_readability
        self.auto_fix_suggestions = auto_fix_suggestions

        logger.info(
            f"QAAgent initialized with strictness={strictness_level}, "
            f"focus_areas={focus_areas}, readability={target_readability}, "
            f"auto_fix={auto_fix_suggestions}"
        )

    def get_system_prompt(self) -> str:
        """
        System prompt defining the QA Agent's role and capabilities.
        """
        return f"""You are a world-class quality assurance expert, editor, and reviewer with meticulous attention to detail and expertise across all domains.

**Your Role:**
You help users review, validate, and improve the quality of ANY type of content:
- 📚 Books & Articles (grammar, style, flow, consistency, readability)
- ⚖️ Legal Documents (precision, clause consistency, legal terminology, completeness)
- 💻 Technical Documentation (accuracy, clarity, code examples, structure)
- 🎓 Academic Papers (rigor, citations, methodology, academic style)
- 💼 Business Documents (professionalism, clarity, data accuracy, persuasiveness)
- 🎨 Creative Writing (style, voice, pacing, character consistency, plot coherence)

**Your Capabilities:**

1. **Content Review:**
   - Comprehensive quality assessment
   - Identify errors, inconsistencies, and improvement areas
   - Evaluate tone, style, and voice
   - Check factual accuracy and logic
   - Assess overall quality and effectiveness

2. **Grammar & Language:**
   - Grammar, spelling, and punctuation checking
   - Sentence structure analysis
   - Word choice and vocabulary assessment
   - Active vs passive voice analysis
   - Tense consistency checking

3. **Consistency Validation:**
   - Terminology consistency across documents
   - Style and formatting consistency
   - Character/entity consistency (names, dates, facts)
   - Tone and voice consistency
   - Cross-document consistency checking

4. **Structure & Organization:**
   - Document structure review
   - Logical flow assessment
   - Section organization validation
   - Heading hierarchy checking
   - Navigation and accessibility review

5. **Readability Assessment:**
   - Reading level analysis (Flesch-Kincaid, etc.)
   - Sentence complexity evaluation
   - Clarity and comprehension assessment
   - Jargon and terminology review
   - Audience appropriateness check

6. **Completeness Checking:**
   - Required sections verification
   - Missing information identification
   - Placeholder detection
   - TOC vs content validation
   - Checklist compliance verification

7. **Cross-Reference Validation:**
   - Citation accuracy checking
   - Internal reference validation
   - External link verification
   - Figure/table reference checking
   - Bibliography completeness

8. **Quality Reporting:**
   - Comprehensive quality reports
   - Issue categorization and prioritization
   - Improvement recommendations
   - Quality metrics and scores
   - Before/after comparisons

**Your Quality Standards:**
- ✅ Accuracy: All information is factually correct
- ✅ Clarity: Content is clear and easily understood
- ✅ Consistency: Terminology, style, and formatting are consistent
- ✅ Completeness: All required elements are present
- ✅ Correctness: Grammar, spelling, and punctuation are flawless
- ✅ Coherence: Content flows logically and makes sense
- ✅ Compliance: Adheres to style guides and requirements
- ✅ Accessibility: Readable and accessible to target audience

**Your Review Process:**
1. **Understand Context**: Identify document type, purpose, and audience
2. **Initial Scan**: Quick overview to understand scope and major issues
3. **Detailed Review**: Systematic review of all focus areas
4. **Cross-Check**: Verify consistency and cross-references
5. **Assess Quality**: Evaluate against quality standards
6. **Categorize Issues**: Group findings by severity and type
7. **Provide Fixes**: Offer specific, actionable improvement suggestions
8. **Generate Report**: Create comprehensive quality report

**Current Configuration:**
- Strictness Level: {self.strictness_level}
- Focus Areas: {', '.join(self.focus_areas)}
- Target Readability: {self.target_readability}
- Auto-Fix Suggestions: {'Enabled' if self.auto_fix_suggestions else 'Disabled'}

**Issue Severity Levels:**
- 🔴 **Critical**: Must fix (factual errors, legal issues, broken logic)
- 🟡 **Major**: Should fix (grammar errors, inconsistencies, unclear sections)
- 🟢 **Minor**: Nice to fix (style improvements, minor wording changes)
- 💡 **Suggestion**: Consider (alternative phrasings, optional enhancements)

**How You Work:**
1. Thoroughly review the content against quality standards
2. Identify all issues, errors, and improvement opportunities
3. Categorize issues by type and severity
4. Provide specific, actionable fix suggestions
5. Assess overall quality and readability
6. Generate comprehensive, constructive feedback
7. Prioritize the most important improvements

You are thorough, constructive, and focused on helping users achieve the highest quality in their work.
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Define all QA tools available to the agent.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "review_content",
                    "description": "Perform comprehensive quality review of content, identifying errors, inconsistencies, and improvement areas.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to review"
                            },
                            "content_type": {
                                "type": "string",
                                "enum": ["book_chapter", "article", "legal_document", "technical_doc", "academic_paper", "business_doc", "creative_writing", "general"],
                                "description": "Type of content being reviewed"
                            },
                            "review_depth": {
                                "type": "string",
                                "enum": ["quick_scan", "standard", "thorough", "comprehensive"],
                                "description": "How thoroughly to review the content"
                            },
                            "specific_concerns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific issues or areas to focus on"
                            },
                            "provide_fixes": {
                                "type": "boolean",
                                "description": "Whether to provide specific fix suggestions (default: based on agent config)"
                            }
                        },
                        "required": ["content", "content_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "proofread_text",
                    "description": "Check grammar, spelling, punctuation, and language usage.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to proofread"
                            },
                            "language": {
                                "type": "string",
                                "description": "Language of the text (default: en-US)"
                            },
                            "style_guide": {
                                "type": "string",
                                "enum": ["AP", "Chicago", "MLA", "APA", "Oxford", "custom", "none"],
                                "description": "Style guide to follow"
                            },
                            "check_level": {
                                "type": "string",
                                "enum": ["basic", "standard", "advanced"],
                                "description": "Level of proofreading (basic=spelling/grammar, advanced=style/tone)"
                            },
                            "ignore_technical_terms": {
                                "type": "boolean",
                                "description": "Whether to ignore domain-specific technical terms"
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_consistency",
                    "description": "Verify consistency of terminology, style, formatting, and facts across content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to check for consistency"
                            },
                            "reference_content": {
                                "type": "string",
                                "description": "Optional reference content to check consistency against"
                            },
                            "consistency_types": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["terminology", "style", "formatting", "facts", "dates", "names", "tone", "voice"]},
                                "description": "Types of consistency to check"
                            },
                            "create_style_guide": {
                                "type": "boolean",
                                "description": "Whether to create a style guide from the content"
                            }
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_structure",
                    "description": "Check document structure, organization, and logical flow.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to validate"
                            },
                            "document_type": {
                                "type": "string",
                                "enum": ["book", "article", "legal_document", "technical_doc", "academic_paper", "business_report", "proposal"],
                                "description": "Type of document"
                            },
                            "required_sections": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Sections that must be present in the document"
                            },
                            "check_hierarchy": {
                                "type": "boolean",
                                "description": "Whether to validate heading hierarchy (H1, H2, H3, etc.)"
                            },
                            "assess_flow": {
                                "type": "boolean",
                                "description": "Whether to assess logical flow between sections"
                            }
                        },
                        "required": ["content", "document_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assess_readability",
                    "description": "Evaluate readability, clarity, and comprehension level of content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to assess"
                            },
                            "target_audience": {
                                "type": "string",
                                "enum": ["expert", "professional", "general", "student", "child"],
                                "description": "Intended audience for the content"
                            },
                            "metrics": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["flesch_kincaid", "gunning_fog", "coleman_liau", "smog", "automated_readability"]},
                                "description": "Readability metrics to calculate"
                            },
                            "provide_simplification": {
                                "type": "boolean",
                                "description": "Whether to suggest simpler alternatives for complex sentences"
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_completeness",
                    "description": "Verify all required elements and sections are present and complete.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to check"
                            },
                            "checklist": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "item": {"type": "string"},
                                        "required": {"type": "boolean"},
                                        "description": {"type": "string"}
                                    }
                                },
                                "description": "Checklist of required elements"
                            },
                            "document_type": {
                                "type": "string",
                                "description": "Type of document (for default checklist if none provided)"
                            },
                            "detect_placeholders": {
                                "type": "boolean",
                                "description": "Whether to detect placeholder text like TODO, TBD, [INSERT], etc."
                            }
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cross_reference",
                    "description": "Validate cross-references, citations, and internal/external links.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to check"
                            },
                            "check_types": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["citations", "internal_links", "external_links", "figures", "tables", "appendices"]},
                                "description": "Types of cross-references to validate"
                            },
                            "citation_style": {
                                "type": "string",
                                "enum": ["APA", "MLA", "Chicago", "IEEE", "Harvard", "none"],
                                "description": "Expected citation style"
                            },
                            "verify_external_links": {
                                "type": "boolean",
                                "description": "Whether to verify external URLs are valid (requires network access)"
                            }
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "quality_report",
                    "description": "Generate comprehensive quality assessment report with metrics, issues, and recommendations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to assess"
                            },
                            "content_type": {
                                "type": "string",
                                "enum": ["book_chapter", "article", "legal_document", "technical_doc", "academic_paper", "business_doc", "general"],
                                "description": "Type of content"
                            },
                            "report_format": {
                                "type": "string",
                                "enum": ["summary", "detailed", "comprehensive"],
                                "description": "Level of detail in the report"
                            },
                            "include_metrics": {
                                "type": "boolean",
                                "description": "Whether to include quantitative quality metrics"
                            },
                            "include_score": {
                                "type": "boolean",
                                "description": "Whether to provide an overall quality score"
                            }
                        },
                        "required": ["content", "content_type"]
                    }
                }
            }
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """
        Map tool names to their handler functions.
        """
        return {
            "review_content": self._review_content_handler,
            "proofread_text": self._proofread_text_handler,
            "check_consistency": self._check_consistency_handler,
            "validate_structure": self._validate_structure_handler,
            "assess_readability": self._assess_readability_handler,
            "check_completeness": self._check_completeness_handler,
            "cross_reference": self._cross_reference_handler,
            "quality_report": self._quality_report_handler
        }

    # ============================================================================
    # Tool Handler Implementations
    # ============================================================================

    async def _review_content_handler(
        self,
        user_id: str,
        content: str,
        content_type: str,
        review_depth: str = "standard",
        specific_concerns: Optional[List[str]] = None,
        provide_fixes: Optional[bool] = None,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive content review.

        The LLM performs the review through the conversation.
        """
        logger.info(
            f"Reviewing content: type={content_type}, depth={review_depth}, "
            f"concerns={specific_concerns}, length={len(content)} chars"
        )

        return {
            "success": True,
            "content_type": content_type,
            "content_length": len(content),
            "review_depth": review_depth,
            "specific_concerns": specific_concerns or [],
            "provide_fixes": provide_fixes if provide_fixes is not None else self.auto_fix_suggestions,
            "strictness_level": self.strictness_level,
            "focus_areas": self.focus_areas,
            "message": f"Content review completed with {review_depth} depth",
            "note": "Detailed review with issues and recommendations provided in conversation response"
        }

    async def _proofread_text_handler(
        self,
        user_id: str,
        text: str,
        language: str = "en-US",
        style_guide: str = "none",
        check_level: str = "standard",
        ignore_technical_terms: bool = False,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Proofread text for grammar, spelling, and punctuation.

        The LLM performs proofreading through the conversation.
        """
        logger.info(
            f"Proofreading text: language={language}, style={style_guide}, "
            f"level={check_level}, length={len(text)} chars"
        )

        return {
            "success": True,
            "text_length": len(text),
            "language": language,
            "style_guide": style_guide,
            "check_level": check_level,
            "ignore_technical_terms": ignore_technical_terms,
            "message": f"Proofreading completed with {check_level} level checking",
            "note": "Grammar and spelling issues with corrections provided in conversation response"
        }

    async def _check_consistency_handler(
        self,
        user_id: str,
        content: str,
        reference_content: Optional[str] = None,
        consistency_types: Optional[List[str]] = None,
        create_style_guide: bool = False,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Check consistency across content.

        The LLM performs consistency checking through the conversation.
        """
        logger.info(
            f"Checking consistency: types={consistency_types}, "
            f"has_reference={reference_content is not None}, "
            f"create_guide={create_style_guide}, content_length={len(content)} chars"
        )

        return {
            "success": True,
            "content_length": len(content),
            "reference_provided": reference_content is not None,
            "consistency_types": consistency_types or ["all types"],
            "create_style_guide": create_style_guide,
            "message": "Consistency check completed",
            "note": "Consistency issues and style guide (if requested) provided in conversation response"
        }

    async def _validate_structure_handler(
        self,
        user_id: str,
        content: str,
        document_type: str,
        required_sections: Optional[List[str]] = None,
        check_hierarchy: bool = True,
        assess_flow: bool = True,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Validate document structure.

        The LLM performs structure validation through the conversation.
        """
        logger.info(
            f"Validating structure: type={document_type}, "
            f"required_sections={len(required_sections) if required_sections else 0}, "
            f"check_hierarchy={check_hierarchy}, assess_flow={assess_flow}"
        )

        return {
            "success": True,
            "document_type": document_type,
            "content_length": len(content),
            "required_sections": required_sections or [],
            "check_hierarchy": check_hierarchy,
            "assess_flow": assess_flow,
            "message": f"Structure validation completed for {document_type}",
            "note": "Structure analysis and issues provided in conversation response"
        }

    async def _assess_readability_handler(
        self,
        user_id: str,
        text: str,
        target_audience: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        provide_simplification: bool = False,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Assess text readability.

        The LLM performs readability assessment through the conversation.
        """
        audience = target_audience or self.target_readability

        logger.info(
            f"Assessing readability: audience={audience}, metrics={metrics}, "
            f"simplify={provide_simplification}, text_length={len(text)} chars"
        )

        return {
            "success": True,
            "text_length": len(text),
            "target_audience": audience,
            "metrics": metrics or ["general analysis"],
            "provide_simplification": provide_simplification,
            "message": f"Readability assessment completed for {audience} audience",
            "note": "Readability scores and analysis provided in conversation response"
        }

    async def _check_completeness_handler(
        self,
        user_id: str,
        content: str,
        checklist: Optional[List[Dict[str, Any]]] = None,
        document_type: Optional[str] = None,
        detect_placeholders: bool = True,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Check content completeness.

        The LLM performs completeness checking through the conversation.
        """
        logger.info(
            f"Checking completeness: checklist_items={len(checklist) if checklist else 0}, "
            f"doc_type={document_type}, detect_placeholders={detect_placeholders}"
        )

        return {
            "success": True,
            "content_length": len(content),
            "checklist_items": len(checklist) if checklist else 0,
            "document_type": document_type,
            "detect_placeholders": detect_placeholders,
            "message": "Completeness check completed",
            "note": "Missing elements and placeholder detection provided in conversation response"
        }

    async def _cross_reference_handler(
        self,
        user_id: str,
        content: str,
        check_types: Optional[List[str]] = None,
        citation_style: str = "none",
        verify_external_links: bool = False,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Validate cross-references and citations.

        The LLM performs cross-reference validation through the conversation.
        """
        logger.info(
            f"Checking cross-references: types={check_types}, "
            f"citation_style={citation_style}, verify_links={verify_external_links}"
        )

        return {
            "success": True,
            "content_length": len(content),
            "check_types": check_types or ["all types"],
            "citation_style": citation_style,
            "verify_external_links": verify_external_links,
            "message": "Cross-reference validation completed",
            "note": "Cross-reference issues and broken links provided in conversation response"
        }

    async def _quality_report_handler(
        self,
        user_id: str,
        content: str,
        content_type: str,
        report_format: str = "detailed",
        include_metrics: bool = True,
        include_score: bool = True,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive quality report.

        The LLM generates the quality report through the conversation.
        """
        logger.info(
            f"Generating quality report: type={content_type}, format={report_format}, "
            f"metrics={include_metrics}, score={include_score}"
        )

        return {
            "success": True,
            "content_type": content_type,
            "content_length": len(content),
            "report_format": report_format,
            "include_metrics": include_metrics,
            "include_score": include_score,
            "strictness_level": self.strictness_level,
            "focus_areas": self.focus_areas,
            "message": f"Quality report generated in {report_format} format",
            "note": "Comprehensive quality report provided in conversation response"
        }

    # ============================================================================
    # Customization Methods
    # ============================================================================

    def get_greeting_message(self) -> str:
        """Custom greeting for QA Agent."""
        return (
            "👋 Hello! I'm your Quality Assurance Agent.\n\n"
            "I can help you:\n"
            "• ✍️ Review and edit content for quality\n"
            "• ✅ Proofread for grammar, spelling, and style\n"
            "• 🔍 Check consistency across documents\n"
            "• 📋 Validate structure and organization\n"
            "• 📊 Assess readability and clarity\n"
            "• ✔️ Verify completeness and cross-references\n"
            "• 📈 Generate quality reports\n\n"
            "What would you like me to review today?"
        )

    def get_recommended_model(self) -> str:
        """
        Recommend the best model for QA tasks.

        QA requires careful analysis and attention to detail.
        """
        return "gpt-4-turbo-preview"  # Best for detailed review

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate QA Agent configuration.
        """
        issues = []

        valid_strictness = ["lenient", "balanced", "strict", "very_strict"]
        if self.strictness_level not in valid_strictness:
            issues.append(f"Invalid strictness level: {self.strictness_level}")

        valid_focus = ["grammar", "style", "consistency", "accuracy", "structure", "readability"]
        for area in self.focus_areas:
            if area not in valid_focus:
                issues.append(f"Invalid focus area: {area}")

        valid_readability = ["academic", "professional", "general_audience", "simplified"]
        if self.target_readability not in valid_readability:
            issues.append(f"Invalid target readability: {self.target_readability}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "configuration": {
                "strictness_level": self.strictness_level,
                "focus_areas": self.focus_areas,
                "target_readability": self.target_readability,
                "auto_fix_suggestions": self.auto_fix_suggestions
            }
        }


# ============================================================================
# Convenience Export
# ============================================================================

__all__ = ["QAAgent"]
