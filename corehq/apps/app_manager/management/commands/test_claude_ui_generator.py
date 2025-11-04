"""
Django management command to test the Claude UI Generator
Usage: python manage.py test_claude_ui_generator
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from corehq.apps.app_manager.ai.claude_client import ClaudeUIGenerator


class Command(BaseCommand):
    help = 'Test the Claude UI Generator for CommCare Custom UIs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n=== Testing Claude UI Generator ===\n'))
        
        # Check if API key is configured
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
        if not api_key:
            self.stdout.write(self.style.ERROR('ERROR: ANTHROPIC_API_KEY not set in settings'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'✓ API key configured (length: {len(api_key)})'))
        
        # Check if feature flag is enabled
        enabled = getattr(settings, 'ENABLE_CUSTOM_UI_AI', False)
        self.stdout.write(self.style.SUCCESS(f'✓ ENABLE_CUSTOM_UI_AI: {enabled}'))
        
        # Initialize the generator
        try:
            generator = ClaudeUIGenerator()
            self.stdout.write(self.style.SUCCESS('✓ ClaudeUIGenerator initialized'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERROR initializing generator: {e}'))
            return
        
        # Test a simple generation
        self.stdout.write(self.style.WARNING('\n--- Testing UI Generation ---'))
        self.stdout.write('Sending request to Claude Sonnet 4.5...')
        
        test_message = "Create a simple hello world page with a heading that says 'Hello CommCare!'"
        
        try:
            result = generator.generate_ui(
                user_message=test_message,
                conversation_history=[],
                current_html=None,
                app_context={
                    'app_name': 'Test App',
                    'modules': [],
                    'case_types': []
                }
            )
            
            self.stdout.write(self.style.SUCCESS('\n✓ Generation successful!'))
            self.stdout.write(f'\nResponse length: {len(result["full_response"])} characters')
            self.stdout.write(f'HTML length: {len(result["html"])} characters')
            
            self.stdout.write(self.style.WARNING('\n--- Generated HTML (first 500 chars) ---'))
            self.stdout.write(result['html'][:500])
            
            self.stdout.write(self.style.WARNING('\n--- Full Response (first 300 chars) ---'))
            self.stdout.write(result['full_response'][:300])
            
            self.stdout.write(self.style.SUCCESS('\n\n=== Test Complete ==='))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nERROR during generation: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())

