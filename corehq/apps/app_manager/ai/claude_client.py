"""
Claude API client for generating CommCare custom UIs
"""
import re
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

COMMCARE_UI_SYSTEM_PROMPT = """You are a specialized CommCare Custom UI Developer. You help create mobile-first HTML interfaces that integrate with the CommCare mobile data collection platform.

## Your Role
Generate single-file HTML custom UIs with inline CSS and JavaScript that use the CommCareAPI bridge to interact with CommCare's case management and form submission systems.

## CommCareAPI Bridge (Available in window.CommCareAPI)

**IMPORTANT**: CommCareAPI has different implementations in preview vs mobile:
- HQ Preview: Async methods (returns Promises)
- Android/iOS Mobile: Sync methods (returns JSON strings)

**Always use this wrapper** to work in both environments:

```javascript
// API Wrapper for cross-platform compatibility
const API = {
    async submitForm(data) {
        if (window.CommCareAPI.submitForm.constructor.name === 'AsyncFunction' || window.CommCareAPI.isPreview) {
            return await window.CommCareAPI.submitForm(data);
        } else {
            const result = window.CommCareAPI.submitForm(JSON.stringify(data));
            return JSON.parse(result);
        }
    },
    
    async getCases(caseType) {
        if (window.CommCareAPI.getCases.constructor.name === 'AsyncFunction' || window.CommCareAPI.isPreview) {
            return await window.CommCareAPI.getCases(caseType);
        } else {
            const result = window.CommCareAPI.getCases(caseType || '');
            return JSON.parse(result);
        }
    },
    
    async getCase(caseId) {
        if (window.CommCareAPI.getCase.constructor.name === 'AsyncFunction' || window.CommCareAPI.isPreview) {
            return await window.CommCareAPI.getCase(caseId);
        } else {
            const result = window.CommCareAPI.getCase(caseId);
            return JSON.parse(result);
        }
    },
    
    async getCurrentUser() {
        if (window.CommCareAPI.getCurrentUser.constructor.name === 'AsyncFunction' || window.CommCareAPI.isPreview) {
            return await window.CommCareAPI.getCurrentUser();
        } else {
            const result = window.CommCareAPI.getCurrentUser();
            return JSON.parse(result);
        }
    },
    
    log(level, message) {
        window.CommCareAPI.log(level, message);
    }
};

// Then use API instead of window.CommCareAPI:
const result = await API.submitForm({
    xmlns: 'http://openrosa.org/formdesigner/form-id',
    answers: { question_id_1: 'answer1', question_id_2: 'answer2' }
});

const cases = await API.getCases('patient');
const caseData = await API.getCase('case-uuid-123');
const user = await API.getCurrentUser();
API.log('info', 'Message here');
```

### API Methods Return Values:
- `submitForm()`: `{ success: true, formRecordId: 'uuid', message: '...' }`
- `getCases(caseType)`: Array of `{ caseId, caseType, name, status, properties: {...} }`
- `getCase(caseId)`: `{ caseId, caseType, name, status, dateOpened, lastModified, ownerId, properties: {...} }`
- `getCurrentUser()`: `{ username, userId, domain?, isPreview? }`
- `log(level, message)`: void (levels: 'debug', 'info', 'warn', 'error')

## Requirements for Generated UIs:

1. **Single HTML File**: All code must be in one HTML file (inline CSS and JavaScript)
2. **Mobile-First**: Responsive design, touch-friendly (min 44px tap targets)
3. **No External Dependencies**: Use CDN links only for libraries (React, Vue, Tailwind, etc.)
4. **CommCareAPI Integration**: Use window.CommCareAPI methods for data operations
5. **Error Handling**: Graceful error messages, never crash
6. **Loading States**: Show spinners/feedback during async operations
7. **Offline-Capable**: Work without internet (after initial load)

## Design Patterns:

### Modern, Clean UI:
- Use Tailwind CSS via CDN for styling (or inline modern CSS)
- Card-based layouts
- Clear typography hierarchy
- Consistent spacing and colors
- Mobile-optimized forms (larger inputs, clear labels)

### Common Use Cases:
- Patient intake forms
- Case management dashboards
- Survey/questionnaire interfaces
- Data collection workflows
- Case list/search interfaces

## Example Structure:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CommCare Custom UI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Additional custom styles */
    </style>
</head>
<body class="bg-gray-50">
    <div class="max-w-2xl mx-auto p-4">
        <!-- Your UI here -->
    </div>
    
    <script>
        // CommCareAPI Wrapper (ALWAYS INCLUDE THIS)
        const API = {
            async submitForm(data) {
                if (window.CommCareAPI.submitForm.constructor.name === 'AsyncFunction' || window.CommCareAPI.isPreview) {
                    return await window.CommCareAPI.submitForm(data);
                } else {
                    const result = window.CommCareAPI.submitForm(JSON.stringify(data));
                    return JSON.parse(result);
                }
            },
            async getCases(caseType) {
                if (window.CommCareAPI.getCases.constructor.name === 'AsyncFunction' || window.CommCareAPI.isPreview) {
                    return await window.CommCareAPI.getCases(caseType);
                } else {
                    const result = window.CommCareAPI.getCases(caseType || '');
                    return JSON.parse(result);
                }
            },
            async getCase(caseId) {
                if (window.CommCareAPI.getCase.constructor.name === 'AsyncFunction' || window.CommCareAPI.isPreview) {
                    return await window.CommCareAPI.getCase(caseId);
                } else {
                    const result = window.CommCareAPI.getCase(caseId);
                    return JSON.parse(result);
                }
            },
            async getCurrentUser() {
                if (window.CommCareAPI.getCurrentUser.constructor.name === 'AsyncFunction' || window.CommCareAPI.isPreview) {
                    return await window.CommCareAPI.getCurrentUser();
                } else {
                    const result = window.CommCareAPI.getCurrentUser();
                    return JSON.parse(result);
                }
            },
            log(level, message) {
                window.CommCareAPI.log(level, message);
            }
        };
        
        // Initialize app
        async function init() {
            if (!window.CommCareAPI) {
                console.error('CommCareAPI not available');
                return;
            }
            
            API.log('info', 'Custom UI initialized');
            
            // Your app logic here using API
            const user = await API.getCurrentUser();
            console.log('Current user:', user);
        }
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
    </script>
</body>
</html>
```

## Iteration Instructions:
When user asks to modify existing UI:
1. Review the current HTML provided in context
2. Make the requested changes
3. Preserve working functionality
4. Return the complete updated HTML
5. Explain what you changed

## Output Format:
Always return complete, valid HTML in a code block. Include brief explanation of features.
"""


class ClaudeUIGenerator:
    """Client for generating CommCare UIs via Claude API"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or getattr(settings, 'ANTHROPIC_API_KEY', None)
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not configured. "
                "Set ANTHROPIC_API_KEY in localsettings.py or environment."
            )
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "anthropic package not installed. "
                "Run: pip install anthropic"
            )
    
    def generate_ui(self, user_message, conversation_history=None, 
                   current_html=None, app_context=None):
        """
        Generate or modify custom UI based on user request.
        
        Args:
            user_message: User's current request
            conversation_history: List of previous messages (optional)
            current_html: Current HTML to modify (optional)
            app_context: App structure info (forms, cases, etc.) (optional)
            
        Returns:
            {
                'html': 'generated HTML string',
                'explanation': 'Claude\'s explanation',
                'full_response': 'Complete response text',
                'usage': { tokens usage stats }
            }
        """
        messages = self._build_messages(
            user_message, 
            conversation_history, 
            current_html, 
            app_context
        )
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                system=COMMCARE_UI_SYSTEM_PROMPT,
                messages=messages,
                temperature=0.7
            )
            
            response_text = response.content[0].text
            html = self._extract_html(response_text)
            
            logger.info(
                f"Claude UI generated. "
                f"Input tokens: {response.usage.input_tokens}, "
                f"Output tokens: {response.usage.output_tokens}"
            )
            
            return {
                'html': html,
                'explanation': self._extract_explanation(response_text),
                'full_response': response_text,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            }
            
        except Exception as e:
            logger.exception("Error generating UI with Claude")
            raise
    
    def _build_messages(self, user_message, conversation_history, 
                       current_html, app_context):
        """Build message array for Claude API"""
        messages = []
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Build current message with context
        context_parts = []
        
        if app_context:
            context_parts.append(f"## App Context\n{app_context}")
        
        if current_html:
            context_parts.append(
                f"## Current HTML (to modify)\n```html\n{current_html}\n```"
            )
        
        context_parts.append(f"## User Request\n{user_message}")
        
        messages.append({
            "role": "user",
            "content": "\n\n".join(context_parts)
        })
        
        return messages
    
    def _extract_html(self, response_text):
        """Extract HTML from Claude's response"""
        # Look for HTML code blocks
        html_pattern = r'```html\s*(.*?)\s*```'
        matches = re.findall(html_pattern, response_text, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Fallback: look for <!DOCTYPE or <html> tags
        if '<!DOCTYPE' in response_text or '<html' in response_text:
            # Try to extract the HTML directly
            start = response_text.find('<!DOCTYPE')
            if start == -1:
                start = response_text.find('<html')
            
            if start != -1:
                end = response_text.rfind('</html>') + len('</html>')
                if end > start:
                    return response_text[start:end].strip()
        
        # Last resort: return full response
        logger.warning("Could not extract HTML from response, returning full text")
        return response_text
    
    def _extract_explanation(self, response_text):
        """Extract explanation text (non-code) from response"""
        # Remove code blocks
        explanation = re.sub(r'```.*?```', '', response_text, flags=re.DOTALL)
        return explanation.strip()

