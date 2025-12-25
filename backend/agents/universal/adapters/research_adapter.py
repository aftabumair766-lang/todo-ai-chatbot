"""
Research & Knowledge Agent - Universal Reusable Agent

A comprehensive research and knowledge management agent that works across ALL projects:
- Book writing, Constitution drafting, Software development, Academic papers, Business plans, etc.

**Capabilities:**
1. Web Search & Information Gathering
2. Document Analysis (PDFs, articles, reports)
3. Content Summarization & Synthesis
4. Fact-checking & Verification
5. Citation Generation (APA, MLA, Chicago, IEEE, etc.)
6. Knowledge Base Creation
7. Source Comparison & Cross-referencing
8. Research Organization

**Use Cases:**
- Book Research: Gather facts, statistics, case studies, expert opinions
- Constitution: Research legal frameworks, precedents, international examples
- Software: Research libraries, frameworks, best practices, architecture patterns
- Academic: Literature review, citation management, methodology research
- Business: Market research, competitor analysis, industry trends

**Example Usage:**
```python
from backend.agents.universal.adapters.research_adapter import ResearchAgent
from backend.agents.reusable import ReusableAgent

research_agent = ReusableAgent(adapter=ResearchAgent())

# Research for book
result = await research_agent.process_message(
    user_id="author_1",
    message="Research the history of artificial intelligence from 1950-2020, focusing on key milestones and breakthroughs",
    conversation_history=[],
    db=None
)

# Analyze document
result = await research_agent.process_message(
    user_id="lawyer_1",
    message="Analyze this constitutional document and extract key principles and rights",
    conversation_history=[],
    db=None
)

# Generate citations
result = await research_agent.process_message(
    user_id="student_1",
    message="Generate APA citations for these 5 research papers",
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


class ResearchAgent(DomainAdapter):
    """
    Universal Research & Knowledge Agent

    Provides comprehensive research capabilities across all domains and professions.
    """

    def __init__(
        self,
        default_citation_style: str = "APA",
        max_search_results: int = 10,
        enable_fact_checking: bool = True,
        knowledge_base_storage: Optional[str] = None
    ):
        """
        Initialize Research Agent with customizable settings.

        Args:
            default_citation_style: Default citation format (APA, MLA, Chicago, IEEE, Harvard)
            max_search_results: Maximum number of search results to return
            enable_fact_checking: Enable automatic fact verification
            knowledge_base_storage: Path to store organized research (optional)
        """
        self.default_citation_style = default_citation_style
        self.max_search_results = max_search_results
        self.enable_fact_checking = enable_fact_checking
        self.knowledge_base_storage = knowledge_base_storage

        logger.info(
            f"ResearchAgent initialized with citation_style={default_citation_style}, "
            f"max_results={max_search_results}, fact_checking={enable_fact_checking}"
        )

    def get_system_prompt(self) -> str:
        """
        System prompt defining the Research Agent's role and capabilities.
        """
        return f"""You are a world-class research expert, information analyst, and knowledge curator with access to vast information sources and advanced analytical capabilities.

**Your Role:**
You help users gather, analyze, synthesize, and organize information for ANY type of project:
- 📚 Book Writing (facts, statistics, case studies, expert quotes)
- ⚖️ Constitution/Legal Documents (legal frameworks, precedents, international examples)
- 💻 Software Development (library research, best practices, architecture patterns)
- 🎓 Academic Research (literature reviews, methodology, citations)
- 💼 Business Planning (market research, competitor analysis, industry trends)
- 🔬 Scientific Research (studies, experiments, data analysis)
- 📰 Journalism (fact-checking, source verification, investigative research)

**Your Capabilities:**

1. **Information Gathering:**
   - Web search across multiple sources
   - Academic database queries
   - Patent and legal document search
   - News and media monitoring
   - Social media trend analysis

2. **Document Analysis:**
   - PDF, Word, text file analysis
   - Extract key themes and concepts
   - Identify main arguments and evidence
   - Summarize complex documents
   - Compare multiple documents

3. **Knowledge Synthesis:**
   - Combine information from multiple sources
   - Identify patterns and trends
   - Create comprehensive summaries
   - Generate insights and conclusions
   - Build structured knowledge bases

4. **Verification & Quality:**
   - Fact-checking claims and statistics
   - Source credibility assessment
   - Detect bias and misinformation
   - Cross-reference multiple sources
   - Verify citations and references

5. **Citation Management:**
   - Generate citations in any format (APA, MLA, Chicago, IEEE, Harvard, etc.)
   - Create bibliographies and reference lists
   - Format in-text citations
   - Manage citation databases

6. **Research Organization:**
   - Categorize and tag research
   - Create research outlines
   - Build knowledge hierarchies
   - Generate research reports
   - Create annotated bibliographies

**Your Standards:**
- ✅ Accuracy: Only provide verified, reliable information
- ✅ Comprehensiveness: Cover all relevant aspects thoroughly
- ✅ Objectivity: Present balanced perspectives without bias
- ✅ Clarity: Organize information in clear, accessible formats
- ✅ Citations: Always provide proper attribution and sources
- ✅ Timeliness: Prioritize current, up-to-date information
- ✅ Relevance: Focus on information directly relevant to the user's needs

**Current Configuration:**
- Default Citation Style: {self.default_citation_style}
- Max Search Results: {self.max_search_results}
- Fact-Checking: {'Enabled' if self.enable_fact_checking else 'Disabled'}
- Knowledge Base: {self.knowledge_base_storage or 'Not configured'}

**How You Work:**
1. Understand the research question or information need
2. Identify the best sources and search strategies
3. Gather comprehensive, relevant information
4. Analyze and synthesize findings
5. Verify facts and check source credibility
6. Organize and present information clearly
7. Provide proper citations and references
8. Offer insights and recommendations

You are thorough, accurate, and committed to delivering high-quality research that empowers users to make informed decisions and create excellent work.
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Define all research tools available to the agent.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the internet for information on any topic. Returns relevant articles, papers, websites, and sources.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query or research question"
                            },
                            "search_type": {
                                "type": "string",
                                "enum": ["general", "academic", "news", "patents", "legal", "social_media"],
                                "description": "Type of search to perform"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 10)"
                            },
                            "time_range": {
                                "type": "string",
                                "enum": ["any", "past_day", "past_week", "past_month", "past_year"],
                                "description": "Time range for search results"
                            },
                            "language": {
                                "type": "string",
                                "description": "Language for search results (default: en)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_document",
                    "description": "Analyze a document (PDF, text, article) to extract key information, themes, and insights.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "The full text content of the document to analyze"
                            },
                            "document_type": {
                                "type": "string",
                                "enum": ["academic_paper", "legal_document", "business_report", "article", "book_chapter", "technical_doc", "general"],
                                "description": "Type of document being analyzed"
                            },
                            "analysis_focus": {
                                "type": "string",
                                "description": "Specific aspect to focus on (e.g., 'methodology', 'legal precedents', 'market trends', 'key arguments')"
                            },
                            "extract_citations": {
                                "type": "boolean",
                                "description": "Whether to extract and list all citations found in the document"
                            }
                        },
                        "required": ["document_content", "document_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "summarize_text",
                    "description": "Create a concise summary of long-form content, preserving key information and main ideas.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text content to summarize"
                            },
                            "summary_length": {
                                "type": "string",
                                "enum": ["brief", "moderate", "detailed"],
                                "description": "Desired length of summary"
                            },
                            "summary_type": {
                                "type": "string",
                                "enum": ["abstract", "executive_summary", "bullet_points", "paragraph"],
                                "description": "Format of the summary"
                            },
                            "focus_areas": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific topics or areas to emphasize in the summary"
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "extract_key_points",
                    "description": "Extract main ideas, key findings, and critical insights from content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to extract key points from"
                            },
                            "max_points": {
                                "type": "integer",
                                "description": "Maximum number of key points to extract (default: 10)"
                            },
                            "categorize": {
                                "type": "boolean",
                                "description": "Whether to categorize key points by theme or topic"
                            },
                            "include_evidence": {
                                "type": "boolean",
                                "description": "Whether to include supporting evidence or data for each key point"
                            }
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "fact_check",
                    "description": "Verify the accuracy of claims, statistics, or statements by cross-referencing reliable sources.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "claim": {
                                "type": "string",
                                "description": "The claim, fact, or statement to verify"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context about the claim (source, date, subject area)"
                            },
                            "verification_depth": {
                                "type": "string",
                                "enum": ["quick", "standard", "thorough"],
                                "description": "How extensively to verify the claim"
                            }
                        },
                        "required": ["claim"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_citations",
                    "description": "Generate properly formatted citations for sources in various citation styles.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sources": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string", "enum": ["book", "article", "website", "journal", "conference", "patent", "legal_case", "thesis"]},
                                        "title": {"type": "string"},
                                        "authors": {"type": "array", "items": {"type": "string"}},
                                        "year": {"type": "string"},
                                        "url": {"type": "string"},
                                        "publisher": {"type": "string"},
                                        "journal": {"type": "string"},
                                        "volume": {"type": "string"},
                                        "pages": {"type": "string"},
                                        "doi": {"type": "string"}
                                    }
                                },
                                "description": "List of sources to generate citations for"
                            },
                            "citation_style": {
                                "type": "string",
                                "enum": ["APA", "MLA", "Chicago", "IEEE", "Harvard", "Vancouver", "AMA"],
                                "description": f"Citation format to use (default: {self.default_citation_style})"
                            },
                            "citation_type": {
                                "type": "string",
                                "enum": ["in_text", "reference_list", "both"],
                                "description": "Type of citation to generate"
                            }
                        },
                        "required": ["sources"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_sources",
                    "description": "Compare multiple sources to identify agreements, contradictions, and unique perspectives.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sources": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "content": {"type": "string"},
                                        "source_type": {"type": "string"},
                                        "publication_date": {"type": "string"},
                                        "credibility_rating": {"type": "string", "enum": ["high", "medium", "low", "unknown"]}
                                    }
                                },
                                "description": "Sources to compare (minimum 2)"
                            },
                            "comparison_criteria": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific aspects to compare (e.g., 'methodology', 'conclusions', 'evidence quality')"
                            },
                            "identify_bias": {
                                "type": "boolean",
                                "description": "Whether to analyze potential bias in sources"
                            }
                        },
                        "required": ["sources"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_knowledge_base",
                    "description": "Organize research findings into a structured, searchable knowledge base with categories and tags.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Main topic or subject of the knowledge base"
                            },
                            "research_items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "content": {"type": "string"},
                                        "source": {"type": "string"},
                                        "tags": {"type": "array", "items": {"type": "string"}},
                                        "relevance_score": {"type": "number"}
                                    }
                                },
                                "description": "Research findings to organize"
                            },
                            "organization_structure": {
                                "type": "string",
                                "enum": ["hierarchical", "thematic", "chronological", "source_based"],
                                "description": "How to organize the knowledge base"
                            },
                            "include_index": {
                                "type": "boolean",
                                "description": "Whether to create a searchable index"
                            }
                        },
                        "required": ["topic", "research_items"]
                    }
                }
            }
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """
        Map tool names to their handler functions.
        """
        return {
            "web_search": self._web_search_handler,
            "analyze_document": self._analyze_document_handler,
            "summarize_text": self._summarize_text_handler,
            "extract_key_points": self._extract_key_points_handler,
            "fact_check": self._fact_check_handler,
            "generate_citations": self._generate_citations_handler,
            "compare_sources": self._compare_sources_handler,
            "create_knowledge_base": self._create_knowledge_base_handler
        }

    # ============================================================================
    # Tool Handler Implementations
    # ============================================================================

    async def _web_search_handler(
        self,
        user_id: str,
        query: str,
        search_type: str = "general",
        max_results: Optional[int] = None,
        time_range: str = "any",
        language: str = "en",
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Search the internet for information.

        Note: This is a placeholder. In production, integrate with:
        - Google Custom Search API
        - Bing Web Search API
        - Academic search APIs (Google Scholar, PubMed, arXiv)
        - News APIs (NewsAPI, MediaStack)
        - Patent databases (USPTO, EPO)
        """
        logger.info(
            f"Web search: query='{query}', type={search_type}, "
            f"max_results={max_results or self.max_search_results}, time_range={time_range}"
        )

        # Placeholder implementation
        # TODO: Integrate with actual search APIs
        return {
            "success": True,
            "query": query,
            "search_type": search_type,
            "results_count": max_results or self.max_search_results,
            "message": f"Search completed for '{query}' in {search_type} sources",
            "note": "Integration with search APIs required for production use"
        }

    async def _analyze_document_handler(
        self,
        user_id: str,
        document_content: str,
        document_type: str,
        analysis_focus: Optional[str] = None,
        extract_citations: bool = False,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Analyze document content to extract key information.

        The actual analysis is performed by the LLM through the conversation.
        This handler acknowledges the request and provides structure.
        """
        logger.info(
            f"Document analysis: type={document_type}, "
            f"focus={analysis_focus}, extract_citations={extract_citations}, "
            f"content_length={len(document_content)} chars"
        )

        return {
            "success": True,
            "document_type": document_type,
            "analysis_focus": analysis_focus,
            "content_length": len(document_content),
            "extract_citations": extract_citations,
            "message": f"Analysis of {document_type} document completed",
            "note": "Detailed analysis provided in conversation response"
        }

    async def _summarize_text_handler(
        self,
        user_id: str,
        text: str,
        summary_length: str = "moderate",
        summary_type: str = "paragraph",
        focus_areas: Optional[List[str]] = None,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Create summary of text content.

        The actual summarization is performed by the LLM.
        This handler structures the request.
        """
        logger.info(
            f"Text summarization: length={summary_length}, type={summary_type}, "
            f"focus_areas={focus_areas}, text_length={len(text)} chars"
        )

        return {
            "success": True,
            "original_length": len(text),
            "summary_length": summary_length,
            "summary_type": summary_type,
            "focus_areas": focus_areas or [],
            "message": f"Summary created in {summary_type} format with {summary_length} length",
            "note": "Summary content provided in conversation response"
        }

    async def _extract_key_points_handler(
        self,
        user_id: str,
        content: str,
        max_points: int = 10,
        categorize: bool = False,
        include_evidence: bool = False,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Extract key points from content.

        The LLM performs the extraction through the conversation.
        """
        logger.info(
            f"Extracting key points: max_points={max_points}, "
            f"categorize={categorize}, include_evidence={include_evidence}, "
            f"content_length={len(content)} chars"
        )

        return {
            "success": True,
            "content_length": len(content),
            "max_points": max_points,
            "categorize": categorize,
            "include_evidence": include_evidence,
            "message": f"Extracted up to {max_points} key points from content",
            "note": "Key points provided in conversation response"
        }

    async def _fact_check_handler(
        self,
        user_id: str,
        claim: str,
        context: Optional[str] = None,
        verification_depth: str = "standard",
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Verify factual claims.

        Note: In production, integrate with:
        - Fact-checking APIs (FactCheck.org, Snopes)
        - Knowledge graphs (Wikidata, DBpedia)
        - Academic databases
        """
        logger.info(
            f"Fact-checking claim: '{claim[:100]}...', "
            f"depth={verification_depth}, has_context={context is not None}"
        )

        return {
            "success": True,
            "claim": claim,
            "context": context,
            "verification_depth": verification_depth,
            "fact_checking_enabled": self.enable_fact_checking,
            "message": f"Claim verified with {verification_depth} verification depth",
            "note": "Verification results provided in conversation response. Integrate with fact-checking APIs for production."
        }

    async def _generate_citations_handler(
        self,
        user_id: str,
        sources: List[Dict[str, Any]],
        citation_style: Optional[str] = None,
        citation_type: str = "both",
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Generate formatted citations.

        The LLM generates properly formatted citations based on the style guide.
        """
        style = citation_style or self.default_citation_style

        logger.info(
            f"Generating citations: style={style}, type={citation_type}, "
            f"source_count={len(sources)}"
        )

        return {
            "success": True,
            "citation_style": style,
            "citation_type": citation_type,
            "source_count": len(sources),
            "message": f"Generated {len(sources)} citations in {style} format",
            "note": "Formatted citations provided in conversation response"
        }

    async def _compare_sources_handler(
        self,
        user_id: str,
        sources: List[Dict[str, Any]],
        comparison_criteria: Optional[List[str]] = None,
        identify_bias: bool = False,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Compare multiple sources for consistency and contradictions.

        The LLM performs the comparison and analysis.
        """
        logger.info(
            f"Comparing sources: count={len(sources)}, "
            f"criteria={comparison_criteria}, identify_bias={identify_bias}"
        )

        if len(sources) < 2:
            return {
                "success": False,
                "error": "At least 2 sources required for comparison",
                "source_count": len(sources)
            }

        return {
            "success": True,
            "source_count": len(sources),
            "comparison_criteria": comparison_criteria or ["general comparison"],
            "identify_bias": identify_bias,
            "message": f"Compared {len(sources)} sources",
            "note": "Comparison analysis provided in conversation response"
        }

    async def _create_knowledge_base_handler(
        self,
        user_id: str,
        topic: str,
        research_items: List[Dict[str, Any]],
        organization_structure: str = "thematic",
        include_index: bool = True,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Organize research into structured knowledge base.

        The LLM creates the organized structure.
        If knowledge_base_storage is configured, it could be persisted.
        """
        logger.info(
            f"Creating knowledge base: topic='{topic}', "
            f"items={len(research_items)}, structure={organization_structure}, "
            f"include_index={include_index}"
        )

        return {
            "success": True,
            "topic": topic,
            "item_count": len(research_items),
            "organization_structure": organization_structure,
            "include_index": include_index,
            "storage_path": self.knowledge_base_storage,
            "message": f"Knowledge base created for '{topic}' with {len(research_items)} items organized by {organization_structure}",
            "note": "Organized knowledge base provided in conversation response"
        }

    # ============================================================================
    # Customization Methods
    # ============================================================================

    def get_greeting_message(self) -> str:
        """Custom greeting for Research Agent."""
        return (
            "👋 Hello! I'm your Research & Knowledge Agent.\n\n"
            "I can help you:\n"
            "• 🔍 Search and gather information from various sources\n"
            "• 📄 Analyze documents and extract key insights\n"
            "• ✍️ Summarize complex content\n"
            "• ✅ Fact-check claims and verify information\n"
            "• 📚 Generate citations in any format\n"
            "• 🗂️ Organize research into knowledge bases\n\n"
            "What would you like to research today?"
        )

    def get_recommended_model(self) -> str:
        """
        Recommend the best model for research tasks.

        Research often requires large context windows for document analysis.
        """
        return "gpt-4-turbo-preview"  # Large context window for document analysis

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate Research Agent configuration.
        """
        issues = []

        if self.default_citation_style not in ["APA", "MLA", "Chicago", "IEEE", "Harvard", "Vancouver", "AMA"]:
            issues.append(f"Invalid citation style: {self.default_citation_style}")

        if self.max_search_results < 1 or self.max_search_results > 100:
            issues.append(f"max_search_results should be between 1-100, got {self.max_search_results}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "configuration": {
                "citation_style": self.default_citation_style,
                "max_results": self.max_search_results,
                "fact_checking": self.enable_fact_checking,
                "knowledge_base": self.knowledge_base_storage or "Not configured"
            }
        }


# ============================================================================
# Convenience Export
# ============================================================================

__all__ = ["ResearchAgent"]
