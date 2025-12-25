"""
Content Testing Agent - Profession-Specific Testing Agent

A specialized testing agent for CONTENT CREATION projects:
- Tests written content for quality, readability, engagement, and effectiveness
- Validates content from a writer/publisher's perspective

**What It Tests:**
1. Readability & Clarity
2. Grammar & Style
3. SEO Optimization
4. Engagement & Impact
5. Audience Appropriateness
6. Originality & Plagiarism
7. Structure & Flow
8. Brand Voice & Tone

**Use Cases:**
- Test book chapters for readability
- Review blog posts for SEO
- Analyze marketing copy for engagement
- Validate content consistency
- Check content completeness

**Example Usage:**
```python
from backend.agents.universal.testing.content_testing_adapter import ContentTestingAgent
from backend.agents.reusable import ReusableAgent

content_tester = ReusableAgent(adapter=ContentTestingAgent())

# Test blog post
result = await content_tester.process_message(
    user_id="writer_1",
    message="Test this blog post for SEO, readability, and engagement metrics",
    conversation_history=[],
    db=None
)

# Test book chapter
result = await content_tester.process_message(
    user_id="author_1",
    message="Test this chapter for readability, flow, and consistency with previous chapters",
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


class ContentTestingAgent(DomainAdapter):
    """
    Content Testing Agent - Tests written content for quality and effectiveness
    """

    def __init__(
        self,
        strictness: str = "balanced",
        target_audience: str = "general",
        min_readability_score: int = 60,
        enable_seo_check: bool = True
    ):
        """
        Initialize Content Testing Agent.

        Args:
            strictness: Testing strictness (lenient, balanced, strict, editorial)
            target_audience: Target audience (children, students, general, professional, expert)
            min_readability_score: Minimum Flesch reading ease score (0-100)
            enable_seo_check: Enable SEO optimization checking
        """
        self.strictness = strictness
        self.target_audience = target_audience
        self.min_readability_score = min_readability_score
        self.enable_seo_check = enable_seo_check

        logger.info(
            f"ContentTestingAgent initialized with strictness={strictness}, "
            f"audience={target_audience}, min_readability={min_readability_score}, seo={enable_seo_check}"
        )

    def get_system_prompt(self) -> str:
        """System prompt for Content Testing Agent."""
        return f"""You are a world-class content editor, SEO expert, and readability specialist with expertise in evaluating written content across all formats.

**Your Role:**
Test and validate written content for quality, effectiveness, and audience appropriateness.

**What You Test:**

1. **Readability & Clarity:**
   - Flesch Reading Ease score (minimum: {self.min_readability_score})
   - Sentence length and complexity
   - Paragraph structure
   - Word choice and vocabulary level
   - Active vs passive voice
   - Clarity of main ideas
   - Logical flow and transitions

2. **Grammar & Style:**
   - Grammar, spelling, punctuation
   - Style consistency
   - Tone appropriateness
   - Voice consistency (1st, 2nd, 3rd person)
   - Tense consistency
   - Word repetition
   - Clichés and overused phrases

3. **SEO Optimization:**
   - Keyword usage and density
   - Meta description quality
   - Title tag optimization
   - Heading structure (H1, H2, H3)
   - Internal/external linking
   - Image alt text
   - URL structure
   - Content length for topic

4. **Engagement & Impact:**
   - Hook effectiveness (first paragraph)
   - Call-to-action clarity
   - Emotional resonance
   - Storytelling elements
   - Examples and evidence
   - Visual element suggestions
   - Shareability potential

5. **Audience Appropriateness:**
   - Reading level match (target: {self.target_audience})
   - Technical depth alignment
   - Cultural sensitivity
   - Tone formality match
   - Content complexity fit
   - Prior knowledge assumptions

6. **Originality & Uniqueness:**
   - Plagiarism risk assessment
   - Content uniqueness
   - Fresh perspective
   - Original insights
   - Value proposition
   - Competitive differentiation

7. **Structure & Organization:**
   - Logical structure
   - Heading hierarchy
   - Section transitions
   - Introduction effectiveness
   - Conclusion strength
   - Paragraph cohesion
   - Information architecture

8. **Brand Voice & Consistency:**
   - Brand voice alignment
   - Messaging consistency
   - Style guide adherence
   - Terminology consistency
   - Cross-content consistency

**Testing Standards:**
- ✅ **Critical Issues**: Must fix (factual errors, plagiarism, unclear messaging)
- 🟡 **Major Issues**: Should fix (poor readability, weak SEO, engagement problems)
- 🟢 **Minor Issues**: Consider fixing (minor grammar, style tweaks)
- 💡 **Suggestions**: Enhancement opportunities (engagement, storytelling, visuals)

**Current Configuration:**
- Strictness: {self.strictness}
- Target Audience: {self.target_audience}
- Min Readability: {self.min_readability_score}/100
- SEO Checking: {'Enabled' if self.enable_seo_check else 'Disabled'}

**How You Work:**
1. Analyze content structure and organization
2. Evaluate readability and clarity
3. Check grammar, style, and tone
4. Assess SEO optimization (if enabled)
5. Measure engagement potential
6. Verify audience appropriateness
7. Check originality and uniqueness
8. Generate comprehensive content test report

You are thorough, constructive, and focused on helping content creators produce high-quality, engaging content that resonates with their audience.
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """Define testing tools for content projects."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "test_readability",
                    "description": "Test content readability and clarity metrics.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Content to test"},
                            "target_audience": {"type": "string", "enum": ["children", "students", "general", "professional", "expert"]},
                            "metrics": {"type": "array", "items": {"type": "string", "enum": ["flesch_ease", "gunning_fog", "smog", "coleman_liau"]}},
                            "suggest_improvements": {"type": "boolean"}
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_grammar_style",
                    "description": "Check grammar, spelling, style, and tone.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "style_guide": {"type": "string", "enum": ["AP", "Chicago", "MLA", "Oxford", "custom"]},
                            "check_tone": {"type": "boolean"},
                            "check_voice": {"type": "boolean"},
                            "provide_corrections": {"type": "boolean"}
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_seo",
                    "description": "Analyze content for SEO optimization.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "target_keyword": {"type": "string"},
                            "meta_description": {"type": "string"},
                            "title": {"type": "string"},
                            "check_aspects": {"type": "array", "items": {"type": "string", "enum": ["keywords", "headings", "links", "images", "length", "all"]}},
                            "suggest_optimizations": {"type": "boolean"}
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "measure_engagement",
                    "description": "Measure content engagement potential and emotional impact.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "content_type": {"type": "string", "enum": ["blog", "article", "social", "email", "book_chapter", "marketing"]},
                            "analyze_aspects": {"type": "array", "items": {"type": "string", "enum": ["hook", "cta", "emotion", "storytelling", "visuals", "shareability"]}},
                            "suggest_enhancements": {"type": "boolean"}
                        },
                        "required": ["content", "content_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_audience_fit",
                    "description": "Verify content appropriateness for target audience.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "target_audience": {"type": "string"},
                            "audience_characteristics": {"type": "object", "properties": {
                                "education_level": {"type": "string"},
                                "technical_knowledge": {"type": "string"},
                                "interests": {"type": "array", "items": {"type": "string"}},
                                "age_range": {"type": "string"}
                            }},
                            "suggest_adjustments": {"type": "boolean"}
                        },
                        "required": ["content", "target_audience"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_originality",
                    "description": "Check content originality and plagiarism risk.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "check_depth": {"type": "string", "enum": ["basic", "standard", "thorough"]},
                            "assess_uniqueness": {"type": "boolean"},
                            "identify_common_phrases": {"type": "boolean"}
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "evaluate_structure",
                    "description": "Evaluate content structure and organization.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "content_type": {"type": "string", "enum": ["blog", "article", "book_chapter", "report", "email", "social"]},
                            "check_elements": {"type": "array", "items": {"type": "string", "enum": ["introduction", "body", "conclusion", "transitions", "headings", "paragraphs"]}},
                            "suggest_reorganization": {"type": "boolean"}
                        },
                        "required": ["content", "content_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_brand_voice",
                    "description": "Validate content against brand voice and style guidelines.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "brand_voice": {"type": "object", "properties": {
                                "tone": {"type": "string"},
                                "personality": {"type": "array", "items": {"type": "string"}},
                                "vocabulary": {"type": "array", "items": {"type": "string"}},
                                "forbidden_words": {"type": "array", "items": {"type": "string"}}
                            }},
                            "reference_content": {"type": "string"},
                            "check_consistency": {"type": "boolean"}
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_content_report",
                    "description": "Generate comprehensive content testing report.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content_title": {"type": "string"},
                            "test_results": {"type": "object"},
                            "report_format": {"type": "string", "enum": ["summary", "detailed", "comprehensive"]},
                            "include_scores": {"type": "boolean"},
                            "include_recommendations": {"type": "boolean"}
                        },
                        "required": ["content_title"]
                    }
                }
            }
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """Map tool names to handlers."""
        return {
            "test_readability": self._test_readability,
            "check_grammar_style": self._check_grammar_style,
            "analyze_seo": self._analyze_seo,
            "measure_engagement": self._measure_engagement,
            "verify_audience_fit": self._verify_audience_fit,
            "check_originality": self._check_originality,
            "evaluate_structure": self._evaluate_structure,
            "validate_brand_voice": self._validate_brand_voice,
            "generate_content_report": self._generate_content_report
        }

    async def _test_readability(self, user_id: str, content: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Testing readability ({len(content)} chars)")
        return {
            "success": True,
            "content_length": len(content),
            "target_audience": kwargs.get("target_audience", self.target_audience),
            "min_score": self.min_readability_score,
            "metrics": kwargs.get("metrics", ["flesch_ease"]),
            "message": "Readability test completed",
            "note": "Readability scores and recommendations in conversation response"
        }

    async def _check_grammar_style(self, user_id: str, content: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Checking grammar and style ({len(content)} chars)")
        return {
            "success": True,
            "content_length": len(content),
            "style_guide": kwargs.get("style_guide", "custom"),
            "checks": ["grammar", "spelling", "style", "tone", "voice"],
            "message": "Grammar and style check completed",
            "note": "Grammar issues and corrections in conversation response"
        }

    async def _analyze_seo(self, user_id: str, content: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Analyzing SEO for content")
        return {
            "success": True,
            "content_length": len(content),
            "seo_enabled": self.enable_seo_check,
            "target_keyword": kwargs.get("target_keyword"),
            "aspects": kwargs.get("check_aspects", ["all"]),
            "message": "SEO analysis completed",
            "note": "SEO optimization report in conversation response"
        }

    async def _measure_engagement(self, user_id: str, content: str, content_type: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Measuring engagement for {content_type}")
        return {
            "success": True,
            "content_type": content_type,
            "content_length": len(content),
            "aspects": kwargs.get("analyze_aspects", ["hook", "cta", "emotion"]),
            "message": f"Engagement analysis completed for {content_type}",
            "note": "Engagement metrics and recommendations in conversation response"
        }

    async def _verify_audience_fit(self, user_id: str, content: str, target_audience: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Verifying audience fit for {target_audience}")
        return {
            "success": True,
            "target_audience": target_audience,
            "content_length": len(content),
            "characteristics": kwargs.get("audience_characteristics", {}),
            "message": f"Audience fit verified for {target_audience}",
            "note": "Audience appropriateness report in conversation response"
        }

    async def _check_originality(self, user_id: str, content: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Checking originality ({len(content)} chars)")
        return {
            "success": True,
            "content_length": len(content),
            "check_depth": kwargs.get("check_depth", "standard"),
            "message": "Originality check completed",
            "note": "Originality assessment and plagiarism risk in conversation response"
        }

    async def _evaluate_structure(self, user_id: str, content: str, content_type: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Evaluating structure for {content_type}")
        return {
            "success": True,
            "content_type": content_type,
            "content_length": len(content),
            "elements": kwargs.get("check_elements", ["all"]),
            "message": f"Structure evaluation completed for {content_type}",
            "note": "Structure analysis in conversation response"
        }

    async def _validate_brand_voice(self, user_id: str, content: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Validating brand voice")
        return {
            "success": True,
            "content_length": len(content),
            "brand_voice": kwargs.get("brand_voice", {}),
            "has_reference": "reference_content" in kwargs,
            "message": "Brand voice validation completed",
            "note": "Brand voice consistency report in conversation response"
        }

    async def _generate_content_report(self, user_id: str, content_title: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Generating content report for '{content_title}'")
        return {
            "success": True,
            "content_title": content_title,
            "report_format": kwargs.get("report_format", "detailed"),
            "strictness": self.strictness,
            "target_audience": self.target_audience,
            "message": f"Content testing report generated for '{content_title}'",
            "note": "Comprehensive content quality report in conversation response"
        }

    def get_greeting_message(self) -> str:
        return (
            "👋 Hello! I'm your Content Testing Agent.\n\n"
            "I specialize in testing written content for:\n"
            "• 📖 Readability and clarity\n"
            "• ✍️ Grammar, style, and tone\n"
            "• 🔍 SEO optimization\n"
            "• 💡 Engagement and impact\n"
            "• 👥 Audience appropriateness\n"
            "• ✨ Originality and uniqueness\n"
            "• 📋 Structure and organization\n"
            "• 🎯 Brand voice consistency\n\n"
            "What content would you like me to test?"
        )


__all__ = ["ContentTestingAgent"]
