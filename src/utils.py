import re
import json
import textwrap
from markdownify import markdownify as md
import markdown
from markdown.extensions import codehilite, fenced_code, tables

class ResponseCleaner:
    """Base class for cleaning raw responses"""
    
    @staticmethod
    def clean_raw_response(raw_response):
        """Clean the raw response from any model"""
        content = str(raw_response)
        
        # Handle JSON-wrapped responses
        if content.strip().startswith('"') and content.strip().endswith('"'):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                content = content.strip('"')
        
        # Replace escaped characters
        replacements = {
            '\\n': '\n',
            '\\"': '"',
            '\\t': '\t',
            '\\r': '\r',
            '\\/': '/',
            '\\\\': '\\'
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        return content.strip()

# =============================================================================
# FORMATTER 1: HTML Formatter
# =============================================================================

def format_to_html(raw_response):
    """
    Convert raw response to clean HTML format
    
    Args:
        raw_response: Raw response string from model
    
    Returns:
        str: Clean HTML formatted response
    """
    
    # Clean the response first
    cleaned = ResponseCleaner.clean_raw_response(raw_response)
    
    # Configure markdown processor
    md_processor = markdown.Markdown(
        extensions=['codehilite', 'fenced_code', 'tables', 'nl2br'],
        extension_configs={
            'codehilite': {'css_class': 'highlight', 'use_pygments': True}
        }
    )
    
    # Split into sections
    sections = cleaned.split('\n\n')
    html_parts = ['<div class="formatted-response">']
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        if section.startswith('Reference(s):'):
            # Format references specially
            refs = section.replace('Reference(s):', '').strip()
            html_parts.append(f'''
            <div class="references-section">
                <h4>📚 References</h4>
                <div class="references-content">{md_processor.convert(refs)}</div>
            </div>
            ''')
        else:
            # Regular content
            html_content = md_processor.convert(section)
            html_parts.append(f'<div class="content-section">{html_content}</div>')
    
    html_parts.append('</div>')
    
    # Add basic CSS for better presentation
    css = '''
    <style>
    .formatted-response { 
        font-family: Arial, sans-serif; 
        line-height: 1.6; 
        max-width: 800px; 
        margin: 0 auto; 
        padding: 20px;
    }
    .content-section { 
        margin-bottom: 20px; 
        padding: 15px;
        background-color: #f9f9f9;
        border-left: 4px solid #007acc;
    }
    .references-section { 
        margin-top: 30px; 
        padding: 15px;
        background-color: #e8f5e8;
        border: 1px solid #4caf50;
        border-radius: 5px;
    }
    .references-section h4 { 
        margin-top: 0; 
        color: #2e7d32;
    }
    </style>
    '''
    
    return css + '\n'.join(html_parts)

# =============================================================================
# FORMATTER 2: Markdown Formatter  
# =============================================================================

def format_to_markdown(raw_response):
    """
    Convert raw response to clean Markdown format
    
    Args:
        raw_response: Raw response string from model
    
    Returns:
        str: Clean Markdown formatted response
    """
    
    # Clean the response first
    cleaned = ResponseCleaner.clean_raw_response(raw_response)
    
    # Split into sections
    sections = cleaned.split('\n\n')
    md_parts = []
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        if section.startswith('Reference(s):'):
            # Format references
            refs = section.replace('Reference(s):', '').strip()
            md_parts.append(f'## 📚 References\n\n{refs}\n')
        else:
            # Regular content - ensure proper paragraph spacing
            md_parts.append(f'{section}\n')
    
    return '\n'.join(md_parts)

# =============================================================================
# FORMATTER 3: Rich Console Formatter
# =============================================================================

def format_to_rich_console(raw_response, print_output=True):
    """
    Format response for Rich console output
    
    Args:
        raw_response: Raw response string from model
        print_output: Whether to print to console (default: True)
    
    Returns:
        str: The cleaned response text
    """
    
    try:
        from rich.console import Console
        from rich.markdown import Markdown
        from rich.panel import Panel
        from rich.columns import Columns
        
        console = Console()
        
        # Clean the response first
        cleaned = ResponseCleaner.clean_raw_response(raw_response)
        
        if print_output:
            # Split into main content and references
            sections = cleaned.split('\n\n')
            main_content = []
            references = []
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                
                if section.startswith('Reference(s):'):
                    references.append(section.replace('Reference(s):', '').strip())
                else:
                    main_content.append(section)
            
            # Display main content
            if main_content:
                main_text = '\n\n'.join(main_content)
                md = Markdown(main_text)
                
                panel = Panel(
                    md,
                    title="📄 Response",
                    border_style="blue",
                    padding=(1, 2)
                )
                console.print(panel)
                console.print()
            
            # Display references if present
            if references:
                ref_text = '\n'.join([f"• {ref}" for ref in references])
                ref_panel = Panel(
                    ref_text,
                    title="📚 References", 
                    border_style="green",
                    padding=(1, 2)
                )
                console.print(ref_panel)
        
        return cleaned
        
    except ImportError:
        print("Rich library not installed. Install with: pip install rich")
        return ResponseCleaner.clean_raw_response(raw_response)

# =============================================================================
# FORMATTER 4: Plain Text Formatter
# =============================================================================

def format_to_plain_text(raw_response, width=80):
    """
    Convert raw response to clean plain text format
    
    Args:
        raw_response: Raw response string from model
        width: Line width for text wrapping (default: 80)
    
    Returns:
        str: Clean plain text formatted response
    """
    
    # Clean the response first
    cleaned = ResponseCleaner.clean_raw_response(raw_response)
    
    # Split into sections
    sections = cleaned.split('\n\n')
    formatted_sections = []
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        if section.startswith('Reference(s):'):
            # Format references section
            refs = section.replace('Reference(s):', '').strip()
            formatted_sections.append("=" * width)
            formatted_sections.append("REFERENCES".center(width))
            formatted_sections.append("=" * width)
            
            # Format each reference
            ref_lines = refs.split('\n')
            for ref in ref_lines:
                ref = ref.strip()
                if ref:
                    if not ref.startswith('•'):
                        ref = f"• {ref}"
                    wrapped = textwrap.fill(ref, width=width, 
                                          initial_indent="", 
                                          subsequent_indent="  ")
                    formatted_sections.append(wrapped)
        else:
            # Regular content - wrap to specified width
            wrapped = textwrap.fill(section, width=width)
            formatted_sections.append(wrapped)
    
    return '\n\n'.join(formatted_sections)

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def clean_only(raw_response):
    """Just clean the response without any formatting"""
    return ResponseCleaner.clean_raw_response(raw_response)

def format_response(raw_response, format_type='plain', **kwargs):
    """
    Universal formatter function
    
    Args:
        raw_response: Raw response from model
        format_type: 'html', 'markdown', 'rich', or 'plain'
        **kwargs: Additional arguments for specific formatters
    
    Returns:
        str: Formatted response
    """
    
    formatters = {
        'html': format_to_html,
        'markdown': format_to_markdown, 
        'rich': format_to_rich_console,
        'plain': format_to_plain_text,
        'clean': clean_only
    }
    
    if format_type not in formatters:
        raise ValueError(f"Format type must be one of: {list(formatters.keys())}")
    
    if format_type == 'plain':
        return formatters[format_type](raw_response, kwargs.get('width', 80))
    elif format_type == 'rich':
        return formatters[format_type](raw_response, kwargs.get('print_output', True))
    else:
        return formatters[format_type](raw_response)