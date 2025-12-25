"""
Template & Document Agent - Universal Reusable Agent

A comprehensive template and document formatting agent that works across ALL projects:
- Book writing, Constitution drafting, Software documentation, Academic papers, Business documents, etc.

**Capabilities:**
1. Template Application & Management
2. Document Formatting & Styling
3. Multi-Format Conversion (PDF, DOCX, Markdown, HTML, LaTeX)
4. Document Merging & Splitting
5. Template Creation & Extraction
6. Boilerplate Generation
7. Style Application
8. Document Export & Publishing

**Use Cases:**
- Book Writing: Apply book templates, format chapters, export to PDF/EPUB
- Constitution: Apply legal document templates, format articles and clauses
- Software Documentation: Generate API docs, format code examples, export to HTML
- Academic Papers: Apply journal templates, format citations, export to LaTeX
- Business Documents: Apply corporate templates, format reports, export to DOCX/PDF

**Example Usage:**
```python
from backend.agents.universal.adapters.template_adapter import TemplateAgent
from backend.agents.reusable import ReusableAgent

template_agent = ReusableAgent(adapter=TemplateAgent())

# Apply template to content
result = await template_agent.process_message(
    user_id="author_1",
    message="Apply the book chapter template to this content with professional formatting",
    conversation_history=[],
    db=None
)

# Convert format
result = await template_agent.process_message(
    user_id="legal_1",
    message="Convert this constitution from Markdown to PDF with legal document formatting",
    conversation_history=[],
    db=None
)

# Generate boilerplate
result = await template_agent.process_message(
    user_id="dev_1",
    message="Generate boilerplate for API documentation including introduction, authentication, and endpoints sections",
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


class TemplateAgent(DomainAdapter):
    """
    Universal Template & Document Agent

    Provides comprehensive template and document formatting capabilities across all domains.
    """

    def __init__(
        self,
        default_output_format: str = "markdown",
        template_library_path: Optional[str] = None,
        enable_custom_styles: bool = True,
        preserve_formatting: bool = True
    ):
        """
        Initialize Template Agent with customizable settings.

        Args:
            default_output_format: Default format for exports (markdown, html, pdf, docx, latex, epub)
            template_library_path: Path to custom template library (optional)
            enable_custom_styles: Allow custom styling and formatting
            preserve_formatting: Preserve original formatting when converting
        """
        self.default_output_format = default_output_format
        self.template_library_path = template_library_path
        self.enable_custom_styles = enable_custom_styles
        self.preserve_formatting = preserve_formatting

        logger.info(
            f"TemplateAgent initialized with output_format={default_output_format}, "
            f"template_library={template_library_path}, custom_styles={enable_custom_styles}, "
            f"preserve_formatting={preserve_formatting}"
        )

    def get_system_prompt(self) -> str:
        """
        System prompt defining the Template Agent's role and capabilities.
        """
        return f"""You are a world-class document formatting expert, template designer, and publishing specialist with expertise in all document formats and styles.

**Your Role:**
You help users format, style, and export ANY type of document:
- 📚 Books (chapters, covers, table of contents, indexes)
- ⚖️ Legal Documents (contracts, constitutions, legal briefs)
- 💻 Technical Documentation (API docs, user guides, README files)
- 🎓 Academic Papers (journal articles, theses, dissertations)
- 💼 Business Documents (reports, proposals, presentations)
- 📄 General Documents (letters, resumes, forms)

**Your Capabilities:**

1. **Template Application:**
   - Apply predefined templates to content
   - Customize templates for specific needs
   - Manage template libraries
   - Create template variations
   - Support for all document types

2. **Document Formatting:**
   - Professional typography and layout
   - Heading hierarchy and structure
   - Paragraph spacing and alignment
   - List formatting (bullets, numbers, nested)
   - Table formatting and styling
   - Code block formatting
   - Quote and callout boxes

3. **Multi-Format Conversion:**
   - Markdown ↔ HTML ↔ PDF ↔ DOCX ↔ LaTeX
   - EPUB, MOBI (for books)
   - XML, JSON (for data documents)
   - RTF, ODT (compatibility formats)
   - Preserve formatting during conversion
   - Handle special characters and encoding

4. **Document Merging:**
   - Combine multiple documents
   - Maintain consistent formatting
   - Merge table of contents
   - Consolidate references
   - Handle duplicate sections

5. **Template Creation:**
   - Extract templates from existing documents
   - Design new templates
   - Create reusable components
   - Define template variables
   - Build template inheritance

6. **Boilerplate Generation:**
   - Standard document sections (abstracts, introductions, conclusions)
   - Legal boilerplate (disclaimers, terms, clauses)
   - Technical boilerplate (setup, installation, configuration)
   - Academic boilerplate (acknowledgments, methodology, references)
   - Business boilerplate (executive summaries, appendices)

7. **Style Application:**
   - Apply typography styles (fonts, sizes, weights)
   - Apply color schemes
   - Apply spacing and margins
   - Apply header/footer styles
   - Apply brand guidelines

8. **Document Export:**
   - Export to PDF (print-ready, web-optimized)
   - Export to DOCX (Microsoft Word)
   - Export to HTML (web pages, blogs)
   - Export to LaTeX (academic publishing)
   - Export to EPUB/MOBI (e-books)
   - Export to Markdown (documentation)

**Your Formatting Standards:**
- ✅ Consistency: Uniform formatting throughout
- ✅ Professionalism: Clean, polished appearance
- ✅ Readability: Easy to read and navigate
- ✅ Accessibility: Compatible with screen readers
- ✅ Standards-Compliant: Follow format specifications
- ✅ Brand Alignment: Match style guidelines
- ✅ Cross-Platform: Work across devices and software

**Supported Document Types:**
- 📖 Books: Fiction, non-fiction, textbooks, workbooks
- 📑 Legal: Contracts, constitutions, briefs, patents
- 💻 Technical: API docs, user guides, README, wikis
- 🎓 Academic: Papers, theses, dissertations, journals
- 💼 Business: Reports, proposals, presentations, white papers
- 📋 Forms: Applications, surveys, questionnaires
- 📧 Letters: Business letters, cover letters, memos
- 📄 Resumes: CVs, portfolios, bios

**Current Configuration:**
- Default Output Format: {self.default_output_format}
- Template Library: {self.template_library_path or 'Built-in templates'}
- Custom Styles: {'Enabled' if self.enable_custom_styles else 'Disabled'}
- Preserve Formatting: {'Yes' if self.preserve_formatting else 'No'}

**How You Work:**
1. Understand the document type and purpose
2. Select or create appropriate template
3. Apply formatting and styling
4. Handle special elements (images, tables, code)
5. Ensure consistency and quality
6. Convert to requested format
7. Optimize for output medium (print, web, e-reader)
8. Validate output and provide preview

You are meticulous, detail-oriented, and committed to producing beautifully formatted, professional documents.
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Define all template and formatting tools available to the agent.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "apply_template",
                    "description": "Apply a template to content with formatting and structure.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to apply the template to"
                            },
                            "template_type": {
                                "type": "string",
                                "enum": ["book_chapter", "legal_document", "technical_doc", "academic_paper", "business_report", "article", "letter", "resume", "custom"],
                                "description": "Type of template to apply"
                            },
                            "template_name": {
                                "type": "string",
                                "description": "Specific template name (optional, for custom templates)"
                            },
                            "customizations": {
                                "type": "object",
                                "properties": {
                                    "font": {"type": "string"},
                                    "font_size": {"type": "integer"},
                                    "margins": {"type": "string"},
                                    "line_spacing": {"type": "number"},
                                    "header_footer": {"type": "boolean"}
                                },
                                "description": "Custom formatting options"
                            }
                        },
                        "required": ["content", "template_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "format_document",
                    "description": "Format document with professional styling, typography, and layout.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to format"
                            },
                            "document_type": {
                                "type": "string",
                                "enum": ["book", "legal", "technical", "academic", "business", "general"],
                                "description": "Type of document"
                            },
                            "style": {
                                "type": "string",
                                "enum": ["formal", "casual", "academic", "technical", "creative", "corporate"],
                                "description": "Formatting style"
                            },
                            "elements": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["headings", "paragraphs", "lists", "tables", "code_blocks", "quotes", "images"]},
                                "description": "Document elements to format"
                            },
                            "output_format": {
                                "type": "string",
                                "enum": ["markdown", "html", "latex", "docx"],
                                "description": "Output format for formatted content"
                            }
                        },
                        "required": ["content", "document_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "convert_format",
                    "description": "Convert document from one format to another while preserving content and formatting.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to convert"
                            },
                            "source_format": {
                                "type": "string",
                                "enum": ["markdown", "html", "latex", "docx", "pdf", "txt", "rtf"],
                                "description": "Current format of the content"
                            },
                            "target_format": {
                                "type": "string",
                                "enum": ["markdown", "html", "latex", "pdf", "docx", "epub", "mobi", "txt", "rtf"],
                                "description": "Desired output format"
                            },
                            "conversion_options": {
                                "type": "object",
                                "properties": {
                                    "preserve_formatting": {"type": "boolean"},
                                    "optimize_for": {"type": "string", "enum": ["print", "web", "ebook"]},
                                    "include_toc": {"type": "boolean"},
                                    "page_size": {"type": "string"}
                                },
                                "description": "Conversion settings"
                            }
                        },
                        "required": ["content", "source_format", "target_format"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_template",
                    "description": "Create a reusable template from specifications or existing content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "template_name": {
                                "type": "string",
                                "description": "Name for the new template"
                            },
                            "template_type": {
                                "type": "string",
                                "enum": ["book", "legal", "technical", "academic", "business", "general"],
                                "description": "Type of template"
                            },
                            "sections": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "required": {"type": "boolean"},
                                        "default_content": {"type": "string"},
                                        "formatting": {"type": "object"}
                                    }
                                },
                                "description": "Template sections and structure"
                            },
                            "variables": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Variable placeholders in the template"
                            },
                            "styling": {
                                "type": "object",
                                "description": "Default styling for the template"
                            }
                        },
                        "required": ["template_name", "template_type", "sections"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "merge_documents",
                    "description": "Merge multiple documents into a single document with consistent formatting.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "documents": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "content": {"type": "string"},
                                        "order": {"type": "integer"}
                                    }
                                },
                                "description": "Documents to merge (minimum 2)"
                            },
                            "merge_options": {
                                "type": "object",
                                "properties": {
                                    "add_separator": {"type": "boolean"},
                                    "generate_toc": {"type": "boolean"},
                                    "consolidate_references": {"type": "boolean"},
                                    "remove_duplicates": {"type": "boolean"}
                                },
                                "description": "Merge settings"
                            },
                            "output_format": {
                                "type": "string",
                                "enum": ["markdown", "html", "pdf", "docx"],
                                "description": "Format for merged document"
                            }
                        },
                        "required": ["documents"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "extract_template",
                    "description": "Extract a reusable template from an existing document.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document": {
                                "type": "string",
                                "description": "The document to extract template from"
                            },
                            "template_name": {
                                "type": "string",
                                "description": "Name for the extracted template"
                            },
                            "extract_elements": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["structure", "styling", "sections", "variables", "formatting"]},
                                "description": "Elements to extract into template"
                            },
                            "generalize": {
                                "type": "boolean",
                                "description": "Whether to generalize content into placeholders"
                            }
                        },
                        "required": ["document", "template_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_boilerplate",
                    "description": "Generate standard boilerplate sections for documents.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "document_type": {
                                "type": "string",
                                "enum": ["book", "legal", "technical", "academic", "business"],
                                "description": "Type of document"
                            },
                            "boilerplate_sections": {
                                "type": "array",
                                "items": {"type": "string", "enum": [
                                    "abstract", "introduction", "conclusion", "acknowledgments",
                                    "disclaimer", "terms_and_conditions", "privacy_policy",
                                    "copyright", "license", "methodology", "references",
                                    "appendix", "glossary", "executive_summary",
                                    "table_of_contents", "index"
                                ]},
                                "description": "Sections to generate"
                            },
                            "context": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "author": {"type": "string"},
                                    "organization": {"type": "string"},
                                    "date": {"type": "string"},
                                    "custom_info": {"type": "object"}
                                },
                                "description": "Context information for boilerplate"
                            },
                            "style": {
                                "type": "string",
                                "enum": ["formal", "casual", "technical", "legal", "academic"],
                                "description": "Writing style for boilerplate"
                            }
                        },
                        "required": ["document_type", "boilerplate_sections"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "export_document",
                    "description": "Export document to specified format with optimization for output medium.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to export"
                            },
                            "export_format": {
                                "type": "string",
                                "enum": ["pdf", "docx", "html", "markdown", "latex", "epub", "mobi", "txt"],
                                "description": "Export format"
                            },
                            "optimize_for": {
                                "type": "string",
                                "enum": ["print", "web", "ebook", "mobile", "archive"],
                                "description": "Optimization target"
                            },
                            "export_options": {
                                "type": "object",
                                "properties": {
                                    "include_toc": {"type": "boolean"},
                                    "include_cover": {"type": "boolean"},
                                    "page_numbers": {"type": "boolean"},
                                    "headers_footers": {"type": "boolean"},
                                    "compression": {"type": "string", "enum": ["none", "low", "medium", "high"]}
                                },
                                "description": "Export settings"
                            },
                            "metadata": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "author": {"type": "string"},
                                    "subject": {"type": "string"},
                                    "keywords": {"type": "array", "items": {"type": "string"}}
                                },
                                "description": "Document metadata"
                            }
                        },
                        "required": ["content", "export_format"]
                    }
                }
            }
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """
        Map tool names to their handler functions.
        """
        return {
            "apply_template": self._apply_template_handler,
            "format_document": self._format_document_handler,
            "convert_format": self._convert_format_handler,
            "create_template": self._create_template_handler,
            "merge_documents": self._merge_documents_handler,
            "extract_template": self._extract_template_handler,
            "generate_boilerplate": self._generate_boilerplate_handler,
            "export_document": self._export_document_handler
        }

    # ============================================================================
    # Tool Handler Implementations
    # ============================================================================

    async def _apply_template_handler(
        self,
        user_id: str,
        content: str,
        template_type: str,
        template_name: Optional[str] = None,
        customizations: Optional[Dict[str, Any]] = None,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Apply template to content.

        The LLM applies the template through the conversation.
        """
        logger.info(
            f"Applying template: type={template_type}, name={template_name}, "
            f"customizations={bool(customizations)}, content_length={len(content)} chars"
        )

        return {
            "success": True,
            "template_type": template_type,
            "template_name": template_name or f"Default {template_type}",
            "content_length": len(content),
            "customizations": customizations or {},
            "message": f"Template '{template_type}' applied to content",
            "note": "Formatted content with template provided in conversation response"
        }

    async def _format_document_handler(
        self,
        user_id: str,
        content: str,
        document_type: str,
        style: str = "formal",
        elements: Optional[List[str]] = None,
        output_format: Optional[str] = None,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Format document with professional styling.

        The LLM performs formatting through the conversation.
        """
        output_fmt = output_format or self.default_output_format

        logger.info(
            f"Formatting document: type={document_type}, style={style}, "
            f"elements={elements}, output={output_fmt}"
        )

        return {
            "success": True,
            "document_type": document_type,
            "style": style,
            "elements": elements or ["all elements"],
            "output_format": output_fmt,
            "content_length": len(content),
            "custom_styles_enabled": self.enable_custom_styles,
            "message": f"Document formatted in {style} style for {document_type}",
            "note": "Formatted document provided in conversation response"
        }

    async def _convert_format_handler(
        self,
        user_id: str,
        content: str,
        source_format: str,
        target_format: str,
        conversion_options: Optional[Dict[str, Any]] = None,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Convert document between formats.

        The LLM performs conversion through the conversation.
        Note: In production, integrate with conversion libraries like pandoc.
        """
        logger.info(
            f"Converting format: {source_format} → {target_format}, "
            f"options={conversion_options}, content_length={len(content)} chars"
        )

        return {
            "success": True,
            "source_format": source_format,
            "target_format": target_format,
            "conversion_options": conversion_options or {},
            "content_length": len(content),
            "preserve_formatting": self.preserve_formatting,
            "message": f"Content converted from {source_format} to {target_format}",
            "note": "Converted content provided in conversation response. For production, integrate with pandoc or similar tools."
        }

    async def _create_template_handler(
        self,
        user_id: str,
        template_name: str,
        template_type: str,
        sections: List[Dict[str, Any]],
        variables: Optional[List[str]] = None,
        styling: Optional[Dict[str, Any]] = None,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Create new reusable template.

        The LLM creates the template through the conversation.
        """
        logger.info(
            f"Creating template: name='{template_name}', type={template_type}, "
            f"sections={len(sections)}, variables={len(variables) if variables else 0}"
        )

        return {
            "success": True,
            "template_name": template_name,
            "template_type": template_type,
            "section_count": len(sections),
            "variables": variables or [],
            "styling": styling or {},
            "library_path": self.template_library_path,
            "message": f"Template '{template_name}' created with {len(sections)} sections",
            "note": "Template definition provided in conversation response"
        }

    async def _merge_documents_handler(
        self,
        user_id: str,
        documents: List[Dict[str, Any]],
        merge_options: Optional[Dict[str, Any]] = None,
        output_format: Optional[str] = None,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Merge multiple documents.

        The LLM performs the merge through the conversation.
        """
        logger.info(
            f"Merging documents: count={len(documents)}, "
            f"options={merge_options}, output={output_format}"
        )

        if len(documents) < 2:
            return {
                "success": False,
                "error": "At least 2 documents required for merging",
                "document_count": len(documents)
            }

        return {
            "success": True,
            "document_count": len(documents),
            "merge_options": merge_options or {},
            "output_format": output_format or self.default_output_format,
            "message": f"Merged {len(documents)} documents",
            "note": "Merged document provided in conversation response"
        }

    async def _extract_template_handler(
        self,
        user_id: str,
        document: str,
        template_name: str,
        extract_elements: Optional[List[str]] = None,
        generalize: bool = True,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Extract template from existing document.

        The LLM extracts the template through the conversation.
        """
        logger.info(
            f"Extracting template: name='{template_name}', "
            f"elements={extract_elements}, generalize={generalize}"
        )

        return {
            "success": True,
            "template_name": template_name,
            "extract_elements": extract_elements or ["all elements"],
            "generalize": generalize,
            "document_length": len(document),
            "message": f"Template '{template_name}' extracted from document",
            "note": "Extracted template provided in conversation response"
        }

    async def _generate_boilerplate_handler(
        self,
        user_id: str,
        document_type: str,
        boilerplate_sections: List[str],
        context: Optional[Dict[str, Any]] = None,
        style: str = "formal",
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Generate standard boilerplate sections.

        The LLM generates boilerplate through the conversation.
        """
        logger.info(
            f"Generating boilerplate: type={document_type}, "
            f"sections={boilerplate_sections}, style={style}, context={bool(context)}"
        )

        return {
            "success": True,
            "document_type": document_type,
            "sections": boilerplate_sections,
            "style": style,
            "context": context or {},
            "message": f"Generated {len(boilerplate_sections)} boilerplate sections for {document_type}",
            "note": "Boilerplate content provided in conversation response"
        }

    async def _export_document_handler(
        self,
        user_id: str,
        content: str,
        export_format: str,
        optimize_for: str = "web",
        export_options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Export document to specified format.

        The LLM prepares export through the conversation.
        Note: In production, integrate with export libraries (ReportLab for PDF, python-docx, etc.)
        """
        logger.info(
            f"Exporting document: format={export_format}, optimize={optimize_for}, "
            f"options={export_options}, metadata={bool(metadata)}"
        )

        return {
            "success": True,
            "export_format": export_format,
            "optimize_for": optimize_for,
            "export_options": export_options or {},
            "metadata": metadata or {},
            "content_length": len(content),
            "message": f"Document exported to {export_format} format (optimized for {optimize_for})",
            "note": "Export-ready content provided in conversation response. For production, integrate with format-specific libraries."
        }

    # ============================================================================
    # Customization Methods
    # ============================================================================

    def get_greeting_message(self) -> str:
        """Custom greeting for Template Agent."""
        return (
            "👋 Hello! I'm your Template & Document Agent.\n\n"
            "I can help you:\n"
            "• 📝 Apply templates to your content\n"
            "• ✨ Format documents professionally\n"
            "• 🔄 Convert between formats (PDF, DOCX, Markdown, HTML, etc.)\n"
            "• 🎨 Create reusable templates\n"
            "• 📚 Merge multiple documents\n"
            "• 📋 Generate boilerplate sections\n"
            "• 📤 Export to various formats\n\n"
            "What document would you like to format or export today?"
        )

    def get_recommended_model(self) -> str:
        """
        Recommend the best model for template tasks.

        Template work requires attention to structure and formatting.
        """
        return "gpt-4-turbo-preview"  # Good balance for formatting tasks

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate Template Agent configuration.
        """
        issues = []

        valid_formats = ["markdown", "html", "pdf", "docx", "latex", "epub", "txt"]
        if self.default_output_format not in valid_formats:
            issues.append(f"Invalid output format: {self.default_output_format}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "configuration": {
                "default_output_format": self.default_output_format,
                "template_library": self.template_library_path or "Built-in",
                "custom_styles": self.enable_custom_styles,
                "preserve_formatting": self.preserve_formatting
            }
        }


# ============================================================================
# Convenience Export
# ============================================================================

__all__ = ["TemplateAgent"]
