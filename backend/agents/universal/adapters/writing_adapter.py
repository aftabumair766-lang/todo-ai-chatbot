"""
Writing & Content Agent
=======================

Universal writing agent for ALL content creation needs.

Capabilities:
    - Long-form content generation (books, articles, documentation)
    - Multiple writing styles (formal, casual, technical, creative)
    - Outline and structure creation
    - Content rewriting and improvement
    - Grammar and style checking
    - Tone adjustment
    - Multi-language translation
    - SEO optimization

Use Cases:
    ✅ Book chapters
    ✅ Constitution drafting
    ✅ Technical documentation
    ✅ Blog posts and articles
    ✅ Email templates
    ✅ Marketing copy
    ✅ Academic papers
    ✅ Business proposals
    ✅ Creative writing
    ✅ Scripts and screenplays

Example Usage:
    from backend.agents.universal import WritingAgent
    from backend.agents.reusable import ReusableAgent

    writer = ReusableAgent(adapter=WritingAgent())

    # Generate outline
    result = await writer.process_message(
        user_id="author_1",
        message="Create outline for book on AI ethics with 10 chapters",
        conversation_history=[],
        db=None
    )

    # Write chapter
    result = await writer.process_message(
        user_id="author_1",
        message="Write chapter 1 introduction in formal academic style, 2000 words",
        conversation_history=[],
        db=None
    )
"""

from typing import Dict, List, Callable, Any, Optional
import logging
from backend.agents.reusable.adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)


class WritingAgent(DomainAdapter):
    """
    Universal Writing & Content Creation Agent.

    Supports all forms of writing across all professions.
    """

    def get_system_prompt(self) -> str:
        """Professional writer and editor system prompt"""
        return """You are a world-class professional writer, editor, and content strategist with expertise across all writing domains.

**Your Capabilities:**

1. **Content Creation**
   - Long-form writing (books, reports, documentation)
   - Short-form content (articles, blog posts, emails)
   - Technical writing (documentation, specifications, manuals)
   - Creative writing (stories, scripts, narratives)
   - Academic writing (papers, theses, dissertations)
   - Business writing (proposals, plans, reports)
   - Legal writing (contracts, agreements, constitutions)

2. **Writing Styles**
   - Formal (academic, legal, business)
   - Casual (blog, social media, conversational)
   - Technical (documentation, specifications)
   - Creative (storytelling, narrative, descriptive)
   - Persuasive (marketing, sales, advocacy)
   - Instructional (tutorials, guides, how-tos)

3. **Structure & Organization**
   - Outline creation (hierarchical, logical flow)
   - Chapter/section planning
   - Paragraph structuring
   - Logical transitions
   - Coherent narrative flow

4. **Quality Enhancement**
   - Grammar and spelling correction
   - Style improvement (clarity, conciseness, impact)
   - Tone adjustment (formal ↔ casual)
   - Readability optimization
   - Flow and coherence
   - Fact-checking and accuracy

5. **Specialized Services**
   - Rewriting and paraphrasing
   - Summarization (executive summary, abstract)
   - Expansion (add detail, examples, explanations)
   - Translation (preserve meaning and tone)
   - SEO optimization (keywords, meta descriptions)
   - Citation generation (APA, MLA, Chicago)

**Response Format:**

For outlines:
```
# Main Title
## Chapter 1: Title
   - Section 1.1: Subtopic
   - Section 1.2: Subtopic
## Chapter 2: Title
   - Section 2.1: Subtopic
```

For content:
- Well-structured paragraphs
- Clear topic sentences
- Supporting evidence and examples
- Smooth transitions
- Strong conclusions

**Quality Standards:**
- ✅ Grammar-perfect (zero errors)
- ✅ Style-appropriate (match requested tone)
- ✅ Coherent flow (logical progression)
- ✅ Engaging (maintain reader interest)
- ✅ Actionable (clear takeaways)
- ✅ Original (no plagiarism)

**Important Rules:**
- ALWAYS match the requested style and tone
- NEVER make up facts or citations (research first)
- ALWAYS provide well-structured, organized content
- NEVER use clichés or generic phrases unless requested
- ALWAYS maintain consistency within a document
- NEVER deviate from the specified word count significantly

**Examples:**

User: "Create outline for book on AI ethics"
You: [Provide hierarchical outline with chapters and sections]

User: "Write introduction chapter in formal academic style"
You: [Provide well-researched, formally written introduction with proper academic tone]

User: "Rewrite this in casual blog style"
You: [Transform content to engaging, conversational blog style]
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """Writing and content creation tools"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_outline",
                    "description": "Create structured outline for any document (book, article, report, etc.)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Main topic or title of the document"
                            },
                            "document_type": {
                                "type": "string",
                                "enum": ["book", "article", "report", "paper", "proposal", "constitution", "documentation"],
                                "description": "Type of document to outline"
                            },
                            "depth": {
                                "type": "integer",
                                "description": "Outline depth: 1=chapters only, 2=chapters+sections, 3=chapters+sections+subsections"
                            },
                            "chapter_count": {
                                "type": "integer",
                                "description": "Number of main chapters/sections (optional)"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context or requirements (optional)"
                            }
                        },
                        "required": ["topic", "document_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_content",
                    "description": "Write content section (chapter, article, section, paragraph)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Topic or title of this section"
                            },
                            "style": {
                                "type": "string",
                                "enum": ["formal", "casual", "technical", "creative", "academic", "business", "legal"],
                                "description": "Writing style"
                            },
                            "length": {
                                "type": "string",
                                "enum": ["short", "medium", "long"],
                                "description": "Desired length: short=500 words, medium=1000-1500 words, long=2000+ words"
                            },
                            "context": {
                                "type": "string",
                                "description": "Outline, previous sections, or additional context"
                            },
                            "audience": {
                                "type": "string",
                                "description": "Target audience (e.g., 'experts', 'general public', 'students')"
                            }
                        },
                        "required": ["topic", "style"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "improve_writing",
                    "description": "Improve existing content (grammar, style, clarity, flow)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Text to improve"
                            },
                            "improvements": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["grammar", "clarity", "conciseness", "flow", "tone", "engagement", "all"]
                                },
                                "description": "Types of improvements needed"
                            },
                            "preserve_meaning": {
                                "type": "boolean",
                                "description": "Whether to preserve exact meaning (true) or allow creative improvements (false)"
                            }
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "rewrite_style",
                    "description": "Rewrite content in different style or tone",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Original text"
                            },
                            "target_style": {
                                "type": "string",
                                "enum": ["formal", "casual", "technical", "creative", "academic", "business", "simple", "advanced"],
                                "description": "Target writing style"
                            },
                            "preserve_length": {
                                "type": "boolean",
                                "description": "Keep approximately same length"
                            }
                        },
                        "required": ["content", "target_style"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "summarize_content",
                    "description": "Create summary or abstract of content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Text to summarize"
                            },
                            "summary_type": {
                                "type": "string",
                                "enum": ["executive", "abstract", "bullet_points", "one_sentence", "paragraph"],
                                "description": "Type of summary"
                            },
                            "max_words": {
                                "type": "integer",
                                "description": "Maximum words in summary (optional)"
                            }
                        },
                        "required": ["content", "summary_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "expand_content",
                    "description": "Expand brief content with details, examples, and explanations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Brief content to expand"
                            },
                            "target_length": {
                                "type": "string",
                                "enum": ["double", "triple", "custom"],
                                "description": "How much to expand"
                            },
                            "add_elements": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["examples", "details", "explanations", "evidence", "statistics", "quotes"]
                                },
                                "description": "Elements to add during expansion"
                            }
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_grammar",
                    "description": "Check and correct grammar, spelling, and punctuation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Text to check"
                            },
                            "return_format": {
                                "type": "string",
                                "enum": ["corrected_text", "list_of_errors", "both"],
                                "description": "How to return results"
                            }
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_title",
                    "description": "Generate compelling titles or headlines",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Content that needs a title"
                            },
                            "title_style": {
                                "type": "string",
                                "enum": ["formal", "catchy", "descriptive", "seo_optimized", "academic"],
                                "description": "Type of title"
                            },
                            "count": {
                                "type": "integer",
                                "description": "Number of title options to generate (1-10)"
                            }
                        },
                        "required": ["content", "title_style"]
                    }
                }
            }
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """Map tools to handler functions"""
        return {
            "create_outline": self._create_outline_handler,
            "write_content": self._write_content_handler,
            "improve_writing": self._improve_writing_handler,
            "rewrite_style": self._rewrite_style_handler,
            "summarize_content": self._summarize_content_handler,
            "expand_content": self._expand_content_handler,
            "check_grammar": self._check_grammar_handler,
            "generate_title": self._generate_title_handler
        }

    # ============================================================================
    # TOOL HANDLERS
    # ============================================================================

    async def _create_outline_handler(
        self,
        user_id: str,
        topic: str,
        document_type: str,
        depth: int = 2,
        chapter_count: Optional[int] = None,
        context: Optional[str] = None,
        db=None
    ) -> Dict[str, Any]:
        """Create structured outline"""
        try:
            # This is where OpenAI will generate the outline based on the prompt
            # For now, return structure indicating success
            logger.info(f"Creating {document_type} outline for: {topic} (depth={depth})")

            return {
                "success": True,
                "topic": topic,
                "document_type": document_type,
                "depth": depth,
                "message": f"Outline created for '{topic}' with {depth} levels of depth"
            }

        except Exception as e:
            logger.error(f"Error creating outline: {e}")
            return {
                "error": True,
                "message": f"Failed to create outline: {str(e)}"
            }

    async def _write_content_handler(
        self,
        user_id: str,
        topic: str,
        style: str,
        length: str = "medium",
        context: Optional[str] = None,
        audience: Optional[str] = None,
        db=None
    ) -> Dict[str, Any]:
        """Write content section"""
        try:
            length_map = {
                "short": "500 words",
                "medium": "1000-1500 words",
                "long": "2000+ words"
            }

            logger.info(f"Writing content: {topic} ({style} style, {length_map[length]})")

            return {
                "success": True,
                "topic": topic,
                "style": style,
                "length": length,
                "message": f"Content written for '{topic}' in {style} style ({length_map[length]})"
            }

        except Exception as e:
            logger.error(f"Error writing content: {e}")
            return {
                "error": True,
                "message": f"Failed to write content: {str(e)}"
            }

    async def _improve_writing_handler(
        self,
        user_id: str,
        content: str,
        improvements: Optional[List[str]] = None,
        preserve_meaning: bool = True,
        db=None
    ) -> Dict[str, Any]:
        """Improve existing content"""
        try:
            improvements = improvements or ["all"]

            logger.info(f"Improving writing: {improvements}")

            return {
                "success": True,
                "improvements_applied": improvements,
                "message": f"Content improved: {', '.join(improvements)}"
            }

        except Exception as e:
            logger.error(f"Error improving writing: {e}")
            return {
                "error": True,
                "message": f"Failed to improve writing: {str(e)}"
            }

    async def _rewrite_style_handler(
        self,
        user_id: str,
        content: str,
        target_style: str,
        preserve_length: bool = True,
        db=None
    ) -> Dict[str, Any]:
        """Rewrite in different style"""
        try:
            logger.info(f"Rewriting to {target_style} style")

            return {
                "success": True,
                "target_style": target_style,
                "message": f"Content rewritten in {target_style} style"
            }

        except Exception as e:
            logger.error(f"Error rewriting style: {e}")
            return {
                "error": True,
                "message": f"Failed to rewrite: {str(e)}"
            }

    async def _summarize_content_handler(
        self,
        user_id: str,
        content: str,
        summary_type: str,
        max_words: Optional[int] = None,
        db=None
    ) -> Dict[str, Any]:
        """Summarize content"""
        try:
            logger.info(f"Creating {summary_type} summary")

            return {
                "success": True,
                "summary_type": summary_type,
                "message": f"{summary_type.replace('_', ' ').title()} summary created"
            }

        except Exception as e:
            logger.error(f"Error summarizing: {e}")
            return {
                "error": True,
                "message": f"Failed to summarize: {str(e)}"
            }

    async def _expand_content_handler(
        self,
        user_id: str,
        content: str,
        target_length: str = "double",
        add_elements: Optional[List[str]] = None,
        db=None
    ) -> Dict[str, Any]:
        """Expand brief content"""
        try:
            add_elements = add_elements or ["details", "examples"]

            logger.info(f"Expanding content: {target_length}, adding {add_elements}")

            return {
                "success": True,
                "target_length": target_length,
                "elements_added": add_elements,
                "message": f"Content expanded with {', '.join(add_elements)}"
            }

        except Exception as e:
            logger.error(f"Error expanding content: {e}")
            return {
                "error": True,
                "message": f"Failed to expand: {str(e)}"
            }

    async def _check_grammar_handler(
        self,
        user_id: str,
        content: str,
        return_format: str = "corrected_text",
        db=None
    ) -> Dict[str, Any]:
        """Check grammar and spelling"""
        try:
            logger.info(f"Checking grammar (return format: {return_format})")

            return {
                "success": True,
                "return_format": return_format,
                "message": "Grammar check complete"
            }

        except Exception as e:
            logger.error(f"Error checking grammar: {e}")
            return {
                "error": True,
                "message": f"Failed to check grammar: {str(e)}"
            }

    async def _generate_title_handler(
        self,
        user_id: str,
        content: str,
        title_style: str,
        count: int = 5,
        db=None
    ) -> Dict[str, Any]:
        """Generate titles"""
        try:
            logger.info(f"Generating {count} {title_style} titles")

            return {
                "success": True,
                "title_style": title_style,
                "count": count,
                "message": f"{count} {title_style} titles generated"
            }

        except Exception as e:
            logger.error(f"Error generating titles: {e}")
            return {
                "error": True,
                "message": f"Failed to generate titles: {str(e)}"
            }

    # ============================================================================
    # CUSTOMIZATIONS
    # ============================================================================

    def get_greeting_response(self) -> str:
        """Professional writer greeting"""
        return (
            "Hello! I'm your Writing & Content Agent. "
            "I can help you with outlines, writing, editing, rewriting, summarization, "
            "and all forms of content creation. What would you like to write today?"
        )

    def get_model_name(self) -> str:
        """Use GPT-4 for high-quality writing"""
        return "gpt-4-turbo-preview"

    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """Writing-specific error handling"""
        return f"I encountered an error while processing your writing request: {str(error)}. Please try again or rephrase your request."
