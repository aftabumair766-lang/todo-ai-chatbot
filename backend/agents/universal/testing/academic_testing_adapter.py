"""
Academic Testing Agent - Profession-Specific Testing Agent

A specialized testing agent for ACADEMIC RESEARCH:
- Tests academic papers, theses, dissertations for rigor, validity, and quality
- Validates academic content from a researcher/scholar's perspective

**What It Tests:**
1. Research Methodology Rigor
2. Citation Accuracy & Quality
3. Academic Writing Standards
4. Statistical Validity
5. Literature Review Completeness
6. Argument Strength & Logic
7. Reproducibility & Transparency
8. Publication Readiness

**Use Cases:**
- Test research papers for journal submission
- Review theses for defense readiness
- Analyze methodology for rigor
- Validate citations and references
- Check statistical analysis

**Example Usage:**
```python
from backend.agents.universal.testing.academic_testing_adapter import AcademicTestingAgent
from backend.agents.reusable import ReusableAgent

academic_tester = ReusableAgent(adapter=AcademicTestingAgent())

# Test research paper
result = await academic_tester.process_message(
    user_id="researcher_1",
    message="Test this research paper for methodology rigor, citation quality, and publication readiness",
    conversation_history=[],
    db=None
)

# Review thesis
result = await academic_tester.process_message(
    user_id="phd_1",
    message="Review this dissertation chapter for academic standards, argument strength, and literature coverage",
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


class AcademicTestingAgent(DomainAdapter):
    """
    Academic Testing Agent - Tests academic research for quality and rigor
    """

    def __init__(
        self,
        strictness: str = "strict",
        discipline: str = "general",
        citation_style: str = "APA",
        peer_review_level: str = "journal"
    ):
        """
        Initialize Academic Testing Agent.

        Args:
            strictness: Testing strictness (lenient, balanced, strict, rigorous)
            discipline: Academic discipline (STEM, humanities, social_science, general)
            citation_style: Required citation style (APA, MLA, Chicago, IEEE, Harvard)
            peer_review_level: Target publication level (conference, journal, dissertation, grant)
        """
        self.strictness = strictness
        self.discipline = discipline
        self.citation_style = citation_style
        self.peer_review_level = peer_review_level

        logger.info(
            f"AcademicTestingAgent initialized with strictness={strictness}, "
            f"discipline={discipline}, citation={citation_style}, level={peer_review_level}"
        )

    def get_system_prompt(self) -> str:
        """System prompt for Academic Testing Agent."""
        return f"""You are a world-class academic peer reviewer, research methodologist, and scholarly publishing expert with expertise in evaluating academic research.

**Your Role:**
Test and validate academic research for methodological rigor, scholarly quality, and publication readiness.

**What You Test:**

1. **Research Methodology Rigor:**
   - Research design appropriateness
   - Sampling methodology
   - Data collection methods
   - Measurement validity and reliability
   - Experimental controls
   - Threats to validity (internal, external, construct, statistical)
   - Ethical considerations
   - Reproducibility of methods

2. **Citation Accuracy & Quality:**
   - Citation format ({self.citation_style} style)
   - Citation completeness
   - Reference accuracy
   - In-text citation consistency
   - Bibliography completeness
   - Citation currency (recent sources)
   - Primary vs secondary source balance
   - Seminal works included

3. **Academic Writing Standards:**
   - Academic tone and voice
   - Objectivity and bias
   - Precision and clarity
   - Discipline-specific conventions
   - Section organization (Abstract, Intro, Methods, Results, Discussion)
   - Logical flow and coherence
   - Technical terminology usage
   - Hedging language appropriateness

4. **Statistical Validity:**
   - Statistical test selection
   - Assumption checking
   - Sample size adequacy (power analysis)
   - Effect size reporting
   - Confidence intervals
   - p-value interpretation
   - Multiple testing corrections
   - Data visualization quality

5. **Literature Review Completeness:**
   - Coverage of key literature
   - Theoretical framework strength
   - Gap identification
   - Critical analysis depth
   - Synthesis quality
   - Literature recency
   - Seminal works inclusion
   - Competing perspectives addressed

6. **Argument Strength & Logic:**
   - Thesis clarity
   - Argument coherence
   - Evidence quality and sufficiency
   - Logical reasoning
   - Claim-evidence alignment
   - Counter-argument consideration
   - Conclusion support
   - Contribution clarity

7. **Reproducibility & Transparency:**
   - Methods detail sufficiency
   - Data availability statements
   - Code/materials sharing
   - Procedure replicability
   - Analysis transparency
   - Limitations acknowledged
   - Conflicts of interest declared
   - Funding disclosed

8. **Publication Readiness:**
   - Contribution significance
   - Novelty assessment
   - Scope appropriateness ({self.peer_review_level})
   - Format compliance
   - Length appropriateness
   - Figure/table quality
   - Supplementary materials
   - Revision recommendations

**Testing Standards:**
- 🔴 **Critical Issues**: Must fix (fatal methodological flaws, plagiarism, fabrication)
- 🟡 **Major Issues**: Should fix (weak methodology, incomplete citations, poor argumentation)
- 🟢 **Minor Issues**: Consider fixing (formatting, minor clarity issues, suggestions)
- 💡 **Suggestions**: Enhancement opportunities (additional analyses, literature, framing)

**Current Configuration:**
- Strictness: {self.strictness}
- Discipline: {self.discipline}
- Citation Style: {self.citation_style}
- Publication Level: {self.peer_review_level}

**How You Work:**
1. Assess research question and contribution
2. Evaluate methodology rigor and appropriateness
3. Review statistical analysis and results
4. Check citation quality and completeness
5. Analyze argument strength and logic
6. Assess literature review coverage
7. Verify reproducibility and transparency
8. Evaluate publication readiness
9. Generate comprehensive academic review

You are rigorous, objective, and focused on upholding academic standards while providing constructive feedback to researchers.
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """Define testing tools for academic research."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "evaluate_methodology",
                    "description": "Evaluate research methodology for rigor and appropriateness.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "methodology_section": {"type": "string"},
                            "research_design": {"type": "string", "enum": ["experimental", "quasi_experimental", "observational", "qualitative", "mixed_methods", "systematic_review"]},
                            "discipline": {"type": "string"},
                            "check_ethics": {"type": "boolean"},
                            "check_validity": {"type": "boolean"},
                            "assess_reproducibility": {"type": "boolean"}
                        },
                        "required": ["methodology_section"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_citations",
                    "description": "Validate citation accuracy, format, and quality.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paper_text": {"type": "string"},
                            "bibliography": {"type": "string"},
                            "citation_style": {"type": "string"},
                            "check_format": {"type": "boolean"},
                            "check_completeness": {"type": "boolean"},
                            "check_consistency": {"type": "boolean"},
                            "assess_currency": {"type": "boolean"}
                        },
                        "required": ["paper_text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "review_academic_writing",
                    "description": "Review academic writing quality and standards.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "discipline": {"type": "string"},
                            "check_tone": {"type": "boolean"},
                            "check_structure": {"type": "boolean"},
                            "check_terminology": {"type": "boolean"},
                            "assess_clarity": {"type": "boolean"}
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assess_statistics",
                    "description": "Assess statistical analysis validity and reporting.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "results_section": {"type": "string"},
                            "statistical_tests": {"type": "array", "items": {"type": "string"}},
                            "sample_size": {"type": "integer"},
                            "check_assumptions": {"type": "boolean"},
                            "check_power": {"type": "boolean"},
                            "check_effect_sizes": {"type": "boolean"},
                            "check_corrections": {"type": "boolean"}
                        },
                        "required": ["results_section"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "evaluate_literature_review",
                    "description": "Evaluate literature review completeness and quality.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "literature_review": {"type": "string"},
                            "research_topic": {"type": "string"},
                            "discipline": {"type": "string"},
                            "check_coverage": {"type": "boolean"},
                            "check_synthesis": {"type": "boolean"},
                            "check_gap_identification": {"type": "boolean"},
                            "assess_critical_analysis": {"type": "boolean"}
                        },
                        "required": ["literature_review", "research_topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_argument",
                    "description": "Analyze argument strength, logic, and evidence.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paper": {"type": "string"},
                            "thesis_statement": {"type": "string"},
                            "check_coherence": {"type": "boolean"},
                            "check_evidence": {"type": "boolean"},
                            "check_logic": {"type": "boolean"},
                            "assess_counterarguments": {"type": "boolean"}
                        },
                        "required": ["paper"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_reproducibility",
                    "description": "Verify research reproducibility and transparency.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "methods": {"type": "string"},
                            "check_detail_sufficiency": {"type": "boolean"},
                            "check_data_availability": {"type": "boolean"},
                            "check_materials_sharing": {"type": "boolean"},
                            "check_limitations": {"type": "boolean"},
                            "assess_transparency": {"type": "boolean"}
                        },
                        "required": ["methods"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assess_publication_readiness",
                    "description": "Assess overall publication readiness and quality.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paper": {"type": "string"},
                            "target_venue": {"type": "string"},
                            "target_venue_type": {"type": "string", "enum": ["conference", "journal", "dissertation", "grant_proposal"]},
                            "assess_significance": {"type": "boolean"},
                            "assess_novelty": {"type": "boolean"},
                            "check_format": {"type": "boolean"},
                            "provide_revision_plan": {"type": "boolean"}
                        },
                        "required": ["paper"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_peer_review",
                    "description": "Generate comprehensive peer review report.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paper_title": {"type": "string"},
                            "review_results": {"type": "object"},
                            "recommendation": {"type": "string", "enum": ["accept", "minor_revisions", "major_revisions", "reject"]},
                            "report_format": {"type": "string", "enum": ["summary", "detailed", "comprehensive"]},
                            "include_scores": {"type": "boolean"},
                            "provide_revision_guidance": {"type": "boolean"}
                        },
                        "required": ["paper_title"]
                    }
                }
            }
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """Map tool names to handlers."""
        return {
            "evaluate_methodology": self._evaluate_methodology,
            "validate_citations": self._validate_citations,
            "review_academic_writing": self._review_academic_writing,
            "assess_statistics": self._assess_statistics,
            "evaluate_literature_review": self._evaluate_literature_review,
            "analyze_argument": self._analyze_argument,
            "verify_reproducibility": self._verify_reproducibility,
            "assess_publication_readiness": self._assess_publication_readiness,
            "generate_peer_review": self._generate_peer_review
        }

    async def _evaluate_methodology(self, user_id: str, methodology_section: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Evaluating methodology ({len(methodology_section)} chars)")
        return {
            "success": True,
            "methodology_length": len(methodology_section),
            "research_design": kwargs.get("research_design"),
            "discipline": kwargs.get("discipline", self.discipline),
            "checks": ["ethics", "validity", "reproducibility"],
            "message": "Methodology evaluation completed",
            "note": "Methodology review in conversation response"
        }

    async def _validate_citations(self, user_id: str, paper_text: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Validating citations")
        return {
            "success": True,
            "paper_length": len(paper_text),
            "citation_style": kwargs.get("citation_style", self.citation_style),
            "checks": ["format", "completeness", "consistency", "currency"],
            "message": "Citation validation completed",
            "note": "Citation analysis in conversation response"
        }

    async def _review_academic_writing(self, user_id: str, text: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Reviewing academic writing ({len(text)} chars)")
        return {
            "success": True,
            "text_length": len(text),
            "discipline": kwargs.get("discipline", self.discipline),
            "checks": ["tone", "structure", "terminology", "clarity"],
            "message": "Academic writing review completed",
            "note": "Writing quality analysis in conversation response"
        }

    async def _assess_statistics(self, user_id: str, results_section: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Assessing statistics")
        return {
            "success": True,
            "results_length": len(results_section),
            "tests": kwargs.get("statistical_tests", []),
            "sample_size": kwargs.get("sample_size"),
            "checks": ["assumptions", "power", "effect_sizes", "corrections"],
            "message": "Statistical assessment completed",
            "note": "Statistical analysis review in conversation response"
        }

    async def _evaluate_literature_review(self, user_id: str, literature_review: str, research_topic: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Evaluating literature review for '{research_topic}'")
        return {
            "success": True,
            "review_length": len(literature_review),
            "research_topic": research_topic,
            "discipline": kwargs.get("discipline", self.discipline),
            "checks": ["coverage", "synthesis", "gap_identification", "critical_analysis"],
            "message": f"Literature review evaluation for '{research_topic}' completed",
            "note": "Literature review analysis in conversation response"
        }

    async def _analyze_argument(self, user_id: str, paper: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Analyzing argument")
        return {
            "success": True,
            "paper_length": len(paper),
            "thesis": kwargs.get("thesis_statement"),
            "checks": ["coherence", "evidence", "logic", "counterarguments"],
            "message": "Argument analysis completed",
            "note": "Argument strength review in conversation response"
        }

    async def _verify_reproducibility(self, user_id: str, methods: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Verifying reproducibility")
        return {
            "success": True,
            "methods_length": len(methods),
            "checks": ["detail_sufficiency", "data_availability", "materials", "limitations", "transparency"],
            "message": "Reproducibility verification completed",
            "note": "Reproducibility assessment in conversation response"
        }

    async def _assess_publication_readiness(self, user_id: str, paper: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Assessing publication readiness")
        return {
            "success": True,
            "paper_length": len(paper),
            "target_venue": kwargs.get("target_venue"),
            "venue_type": kwargs.get("target_venue_type", self.peer_review_level),
            "checks": ["significance", "novelty", "format"],
            "message": "Publication readiness assessment completed",
            "note": "Publication readiness report in conversation response"
        }

    async def _generate_peer_review(self, user_id: str, paper_title: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Generating peer review for '{paper_title}'")
        return {
            "success": True,
            "paper_title": paper_title,
            "recommendation": kwargs.get("recommendation"),
            "report_format": kwargs.get("report_format", "detailed"),
            "strictness": self.strictness,
            "discipline": self.discipline,
            "citation_style": self.citation_style,
            "peer_review_level": self.peer_review_level,
            "message": f"Peer review generated for '{paper_title}'",
            "note": "Comprehensive peer review report in conversation response"
        }

    def get_greeting_message(self) -> str:
        return (
            "👋 Hello! I'm your Academic Testing Agent.\n\n"
            "I specialize in testing academic research for:\n"
            "• 🔬 Research methodology rigor\n"
            "• 📚 Citation accuracy and quality\n"
            "• ✍️ Academic writing standards\n"
            "• 📊 Statistical validity\n"
            "• 📖 Literature review completeness\n"
            "• 💭 Argument strength and logic\n"
            "• 🔁 Reproducibility and transparency\n"
            "• 📄 Publication readiness\n\n"
            "What academic work would you like me to review?"
        )


__all__ = ["AcademicTestingAgent"]
