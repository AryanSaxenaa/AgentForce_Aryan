"""
Integration tests for the AI setup wizard.
"""
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the setup wizard functions
import setup_ai
from config.ai_config import AIConfigManager


class TestSetupWizard:
    """Test the interactive setup wizard functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Clear environment variables
        self.original_env = {}
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "AI_PROVIDER"]:
            if key in os.environ:
                self.original_env[key] = os.environ[key]
                del os.environ[key]
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        
        # Restore environment variables
        for key, value in self.original_env.items():
            os.environ[key] = value
    
    def test_display_current_status_no_keys(self):
        """Test displaying status when no API keys are configured."""
        config_manager = AIConfigManager()
        setup_info = config_manager.validate_setup()
        
        # Should show no AI capability
        assert not setup_info['has_ai_capability']
        assert setup_info['preferred_provider'] == 'mock'
        assert not setup_info['available_providers']['openai']
        assert not setup_info['available_providers']['anthropic']
    
    def test_display_current_status_with_openai(self):
        """Test displaying status with OpenAI key configured."""
        os.environ['OPENAI_API_KEY'] = 'sk-test-key-123'
        
        config_manager = AIConfigManager()
        setup_info = config_manager.validate_setup()
        
        # Should show OpenAI capability
        assert setup_info['has_ai_capability']
        assert setup_info['preferred_provider'] == 'openai'
        assert setup_info['available_providers']['openai']
        assert not setup_info['available_providers']['anthropic']
    
    def test_display_current_status_with_anthropic(self):
        """Test displaying status with Anthropic key configured."""
        os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-test-key-123'
        
        config_manager = AIConfigManager()
        setup_info = config_manager.validate_setup()
        
        # Should show Anthropic capability
        assert setup_info['has_ai_capability']
        assert setup_info['preferred_provider'] == 'anthropic'
        assert not setup_info['available_providers']['openai']
        assert setup_info['available_providers']['anthropic']
    
    def test_display_current_status_with_both_keys(self):
        """Test displaying status with both API keys configured."""
        os.environ['OPENAI_API_KEY'] = 'sk-test-key-123'
        os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-test-key-123'
        
        config_manager = AIConfigManager()
        setup_info = config_manager.validate_setup()
        
        # Should show both capabilities, prefer OpenAI by default
        assert setup_info['has_ai_capability']
        assert setup_info['preferred_provider'] == 'openai'
        assert setup_info['available_providers']['openai']
        assert setup_info['available_providers']['anthropic']
    
    @patch('setup_ai.validate_openai_key')
    def test_setup_openai_interactive_success(self, mock_validate):
        """Test successful OpenAI setup."""
        mock_validate.return_value = True
        
        with patch('setup_ai.Prompt.ask', return_value='sk-test-key-123'):
            result = setup_ai.setup_openai_interactive()
            
        assert result == 'sk-test-key-123'
        mock_validate.assert_called_once_with('sk-test-key-123')
    
    @patch('setup_ai.validate_openai_key')
    @patch('setup_ai.Confirm.ask')
    def test_setup_openai_interactive_invalid_key(self, mock_confirm, mock_validate):
        """Test OpenAI setup with invalid key."""
        mock_validate.return_value = False
        mock_confirm.return_value = False  # Don't retry
        
        with patch('setup_ai.Prompt.ask', return_value='invalid-key'):
            result = setup_ai.setup_openai_interactive()
            
        assert result is None
        mock_validate.assert_called_once_with('invalid-key')
    
    @patch('setup_ai.validate_anthropic_key')
    def test_setup_anthropic_interactive_success(self, mock_validate):
        """Test successful Anthropic setup."""
        mock_validate.return_value = True
        
        with patch('setup_ai.Prompt.ask', return_value='sk-ant-test-key-123'):
            result = setup_ai.setup_anthropic_interactive()
            
        assert result == 'sk-ant-test-key-123'
        mock_validate.assert_called_once_with('sk-ant-test-key-123')
    
    def test_setup_openai_interactive_skip(self):
        """Test skipping OpenAI setup."""
        with patch('setup_ai.Prompt.ask', return_value='skip'):
            result = setup_ai.setup_openai_interactive()
            
        assert result is None
    
    def test_setup_anthropic_interactive_skip(self):
        """Test skipping Anthropic setup."""
        with patch('setup_ai.Prompt.ask', return_value='skip'):
            result = setup_ai.setup_anthropic_interactive()
            
        assert result is None
    
    def test_configure_advanced_settings(self):
        """Test configuring advanced AI settings."""
        with patch('setup_ai.Prompt.ask', side_effect=['2000', '0.5', '60']):
            settings = setup_ai.configure_advanced_settings()
            
        expected = {
            'AI_MAX_TOKENS': '2000',
            'AI_TEMPERATURE': '0.5',
            'AI_TIMEOUT': '60'
        }
        assert settings == expected
    
    def test_configure_advanced_settings_invalid_values(self):
        """Test configuring advanced settings with invalid values."""
        with patch('setup_ai.Prompt.ask', side_effect=['invalid', '5.0', 'bad']):
            settings = setup_ai.configure_advanced_settings()
            
        # Should not include invalid values
        assert 'AI_MAX_TOKENS' not in settings
        assert 'AI_TEMPERATURE' not in settings  # Out of range
        assert 'AI_TIMEOUT' not in settings
    
    def test_validate_openai_key_api_error(self):
        """Test OpenAI key validation with API error."""
        # Mock openai module to exist but raise an exception
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Invalid API key")
        
        with patch.dict('sys.modules', {'openai': mock_openai}):
            result = setup_ai.validate_openai_key('sk-invalid-key')
            assert result is False
    
    def test_validate_anthropic_key_api_error(self):
        """Test Anthropic key validation with API error."""
        # Mock anthropic module to exist but raise an exception
        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("Invalid API key")
        
        with patch.dict('sys.modules', {'anthropic': mock_anthropic}):
            result = setup_ai.validate_anthropic_key('sk-ant-invalid-key')
            assert result is False
    
    def test_create_env_file_new(self):
        """Test creating a new .env file."""
        env_vars = {
            'OPENAI_API_KEY': 'sk-test-key-123',
            'OPENAI_MODEL': 'gpt-4',
            'AI_PROVIDER': 'openai'
        }
        
        result = setup_ai.create_env_file(env_vars)
        assert result is True
        
        # Check file was created
        env_path = Path('.env')
        assert env_path.exists()
        
        # Check content
        content = env_path.read_text()
        assert 'OPENAI_API_KEY=sk-test-key-123' in content
        assert 'OPENAI_MODEL=gpt-4' in content
        assert 'AI_PROVIDER=openai' in content
        assert '# Test Case Generator Bot' in content
    
    def test_create_env_file_existing(self):
        """Test updating an existing .env file."""
        # Create existing .env file
        env_path = Path('.env')
        env_path.write_text('EXISTING_VAR=value\nOPENAI_API_KEY=old-key\n')
        
        env_vars = {
            'OPENAI_API_KEY': 'sk-new-key-123',
            'AI_PROVIDER': 'openai'
        }
        
        result = setup_ai.create_env_file(env_vars)
        assert result is True
        
        # Check content
        content = env_path.read_text()
        assert 'OPENAI_API_KEY=sk-new-key-123' in content  # Updated
        assert 'AI_PROVIDER=openai' in content  # Added
        assert 'EXISTING_VAR=value' in content  # Preserved
        assert 'old-key' not in content  # Old value replaced
    
    @patch('setup_ai.setup_openai_interactive')
    @patch('setup_ai.setup_anthropic_interactive')
    @patch('setup_ai.Prompt.ask')
    @patch('setup_ai.Confirm.ask')
    def test_run_setup_wizard_openai_only(self, mock_confirm, mock_prompt, mock_anthropic, mock_openai):
        """Test running setup wizard for OpenAI only."""
        mock_prompt.side_effect = ['openai', 'gpt-4']  # Provider choice, model choice
        mock_confirm.return_value = False  # No advanced settings
        mock_openai.return_value = 'sk-test-key-123'
        
        result = setup_ai.run_setup_wizard()
        
        expected = {
            'OPENAI_API_KEY': 'sk-test-key-123',
            'OPENAI_MODEL': 'gpt-4',
            'AI_PROVIDER': 'openai'
        }
        assert result == expected
        mock_openai.assert_called_once()
        mock_anthropic.assert_not_called()
    
    @patch('setup_ai.setup_openai_interactive')
    @patch('setup_ai.setup_anthropic_interactive')
    @patch('setup_ai.Prompt.ask')
    @patch('setup_ai.Confirm.ask')
    def test_run_setup_wizard_both_providers(self, mock_confirm, mock_prompt, mock_anthropic, mock_openai):
        """Test running setup wizard for both providers."""
        mock_prompt.side_effect = [
            'both',  # Provider choice
            'gpt-4',  # OpenAI model
            'claude-3-sonnet-20240229',  # Anthropic model
            'auto'  # Provider preference
        ]
        mock_confirm.return_value = False  # No advanced settings
        mock_openai.return_value = 'sk-test-key-123'
        mock_anthropic.return_value = 'sk-ant-test-key-456'
        
        result = setup_ai.run_setup_wizard()
        
        expected = {
            'OPENAI_API_KEY': 'sk-test-key-123',
            'OPENAI_MODEL': 'gpt-4',
            'ANTHROPIC_API_KEY': 'sk-ant-test-key-456',
            'ANTHROPIC_MODEL': 'claude-3-sonnet-20240229',
            'AI_PROVIDER': 'auto'
        }
        assert result == expected
        mock_openai.assert_called_once()
        mock_anthropic.assert_called_once()
    
    @patch('setup_ai.Prompt.ask')
    def test_run_setup_wizard_skip(self, mock_prompt):
        """Test skipping the setup wizard."""
        mock_prompt.return_value = 'skip'
        
        result = setup_ai.run_setup_wizard()
        assert result is None
    
    def test_verify_setup_success(self):
        """Test successful setup verification."""
        # Create .env file
        env_path = Path('.env')
        env_path.write_text('OPENAI_API_KEY=sk-test-key-123\nAI_PROVIDER=openai\n')
        
        # Mock console to capture output
        with patch('setup_ai.console') as mock_console:
            setup_ai.verify_setup()
            
        # Check that success message was printed
        mock_console.print.assert_any_call("[green]✅ AI setup completed successfully![/green]")
    
    def test_verify_setup_failure(self):
        """Test setup verification when no valid keys are found."""
        # Create empty .env file
        env_path = Path('.env')
        env_path.write_text('# Empty config\n')
        
        # Mock console to capture output
        with patch('setup_ai.console') as mock_console:
            setup_ai.verify_setup()
            
        # Check that failure message was printed
        mock_console.print.assert_any_call("[red]❌ Setup verification failed. Please check your configuration.[/red]")


class TestSetupWizardIntegration:
    """Integration tests for the complete setup process."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Clear environment variables
        self.original_env = {}
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "AI_PROVIDER"]:
            if key in os.environ:
                self.original_env[key] = os.environ[key]
                del os.environ[key]
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        
        # Restore environment variables
        for key, value in self.original_env.items():
            os.environ[key] = value
    
    @patch('setup_ai.run_setup_wizard')
    @patch('setup_ai.create_env_file')
    @patch('setup_ai.verify_setup')
    @patch('setup_ai.Confirm.ask')
    def test_main_complete_setup_flow(self, mock_confirm, mock_verify, mock_create_env, mock_wizard):
        """Test the complete setup flow from main function."""
        # Mock no existing configuration
        mock_confirm.return_value = True  # User wants to configure
        
        # Mock wizard returns configuration
        mock_wizard.return_value = {
            'OPENAI_API_KEY': 'sk-test-key-123',
            'AI_PROVIDER': 'openai'
        }
        
        # Mock successful env file creation
        mock_create_env.return_value = True
        
        # Run main function
        setup_ai.main()
        
        # Verify the flow
        mock_wizard.assert_called_once()
        mock_create_env.assert_called_once_with({
            'OPENAI_API_KEY': 'sk-test-key-123',
            'AI_PROVIDER': 'openai'
        })
        mock_verify.assert_called_once()
    
    @patch('setup_ai.run_setup_wizard')
    @patch('setup_ai.Confirm.ask')
    def test_main_setup_cancelled(self, mock_confirm, mock_wizard):
        """Test main function when setup is cancelled."""
        # Mock no existing configuration
        mock_confirm.return_value = True  # User wants to configure
        
        # Mock wizard returns None (cancelled)
        mock_wizard.return_value = None
        
        # Mock console to capture output
        with patch('setup_ai.console') as mock_console:
            setup_ai.main()
            
        # Verify cancellation message
        mock_console.print.assert_any_call("[yellow]Setup cancelled. You can run this script again later.[/yellow]")
    
    @patch('setup_ai.Confirm.ask')
    def test_main_existing_config_no_reconfigure(self, mock_confirm):
        """Test main function with existing config when user doesn't want to reconfigure."""
        # Set up existing configuration
        os.environ['OPENAI_API_KEY'] = 'sk-existing-key-123'
        
        # User doesn't want to reconfigure
        mock_confirm.return_value = False
        
        # Mock console to capture output
        with patch('setup_ai.console') as mock_console:
            setup_ai.main()
            
        # Verify success message
        mock_console.print.assert_any_call("[green]✓ AI is already configured and ready to use![/green]")