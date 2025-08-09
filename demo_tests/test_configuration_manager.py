"""
Unit tests for ConfigurationManager - Testing configuration loading and validation scenarios
"""
import os
import tempfile
import yaml
import pytest
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open

from src.config.configuration_manager import ConfigurationManager, TestGeneratorConfig
from src.interfaces.base_interfaces import Language


class TestConfigurationManager:
    """Test suite for ConfigurationManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.yaml")
        
        # Sample configuration data
        self.sample_config = {
            'ai': {
                'provider': 'openai',
                'openai_model': 'gpt-4',
                'anthropic_model': 'claude-3-sonnet-20240229',
                'max_tokens': 1500,
                'temperature': 0.5,
                'timeout': 45
            },
            'test_generation': {
                'coverage_threshold': 85.0,
                'max_test_cases_per_function': 7,
                'include_edge_cases': False,
                'include_integration_tests': False,
                'default_test_framework': {
                    'python': 'unittest',
                    'javascript': 'mocha'
                }
            },
            'output': {
                'output_format': 'json',
                'test_file_prefix': 'spec_',
                'test_directory': 'specs'
            },
            'integration': {
                'github_integration': True,
                'auto_pr_comments': False,
                'coverage_check_enabled': False
            },
            'languages': {
                'python': {
                    'test_framework': 'unittest',
                    'custom_setting': 'test_value'
                }
            }
        }
    
    def teardown_method(self):
        """Clean up after each test method."""
        # Clean up temporary directory and all its contents
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_default_configuration(self):
        """Test that ConfigurationManager initializes with default values."""
        config_manager = ConfigurationManager(config_path=None)
        
        assert config_manager.config.ai_provider == "auto"
        assert config_manager.config.openai_model == "gpt-4"
        assert config_manager.config.anthropic_model == "claude-3-sonnet-20240229"
        assert config_manager.config.ai_max_tokens == 1000
        assert config_manager.config.ai_temperature == 0.3
        assert config_manager.config.ai_timeout == 30
        assert config_manager.config.coverage_threshold == 80.0
        assert config_manager.config.max_test_cases_per_function == 5
        assert config_manager.config.include_edge_cases is True
        assert config_manager.config.include_integration_tests is True
        assert config_manager.config.output_format == "files"
        assert config_manager.config.test_file_prefix == "test_"
        assert config_manager.config.test_directory == "tests"
        assert config_manager.config.github_integration is False
        assert config_manager.config.auto_pr_comments is True
        assert config_manager.config.coverage_check_enabled is True
    
    def test_load_config_from_yaml_file(self):
        """Test loading configuration from YAML file."""
        # Write sample config to file
        with open(self.config_path, 'w') as f:
            yaml.dump(self.sample_config, f)
        
        config_manager = ConfigurationManager(config_path=self.config_path)
        
        # Verify AI configuration
        assert config_manager.config.ai_provider == "openai"
        assert config_manager.config.openai_model == "gpt-4"
        assert config_manager.config.ai_max_tokens == 1500
        assert config_manager.config.ai_temperature == 0.5
        assert config_manager.config.ai_timeout == 45
        
        # Verify test generation configuration
        assert config_manager.config.coverage_threshold == 85.0
        assert config_manager.config.max_test_cases_per_function == 7
        assert config_manager.config.include_edge_cases is False
        assert config_manager.config.include_integration_tests is False
        assert config_manager.config.default_test_framework['python'] == 'unittest'
        assert config_manager.config.default_test_framework['javascript'] == 'mocha'
        
        # Verify output configuration
        assert config_manager.config.output_format == "json"
        assert config_manager.config.test_file_prefix == "spec_"
        assert config_manager.config.test_directory == "specs"
        
        # Verify integration configuration
        assert config_manager.config.github_integration is True
        assert config_manager.config.auto_pr_comments is False
        assert config_manager.config.coverage_check_enabled is False
    
    def test_load_config_nonexistent_file(self):
        """Test loading configuration when file doesn't exist."""
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.yaml")
        config_manager = ConfigurationManager(config_path=nonexistent_path)
        
        # Should use default values
        assert config_manager.config.ai_provider == "auto"
        assert config_manager.config.coverage_threshold == 80.0
    
    def test_load_config_invalid_yaml(self):
        """Test loading configuration with invalid YAML."""
        # Write invalid YAML to file
        with open(self.config_path, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        config_manager = ConfigurationManager(config_path=self.config_path)
        
        # Should use default values when YAML is invalid
        assert config_manager.config.ai_provider == "auto"
        assert config_manager.config.coverage_threshold == 80.0
    
    @patch.dict(os.environ, {
        'AI_PROVIDER': 'anthropic',
        'OPENAI_MODEL': 'gpt-3.5-turbo',
        'ANTHROPIC_MODEL': 'claude-3-haiku-20240307',
        'AI_MAX_TOKENS': '2000',
        'AI_TEMPERATURE': '0.7',
        'AI_TIMEOUT': '60',
        'COVERAGE_THRESHOLD': '90.0',
        'MAX_TEST_CASES_PER_FUNCTION': '10',
        'INCLUDE_EDGE_CASES': 'false',
        'INCLUDE_INTEGRATION_TESTS': 'true',
        'GITHUB_INTEGRATION': 'true',
        'AUTO_PR_COMMENTS': 'false',
        'COVERAGE_CHECK_ENABLED': 'false',
        'OUTPUT_FORMAT': 'stdout',
        'TEST_FILE_PREFIX': 'unit_',
        'TEST_DIRECTORY': 'unit_tests'
    })
    def test_load_config_from_environment_variables(self):
        """Test loading configuration from environment variables."""
        config_manager = ConfigurationManager(config_path=None)
        
        # Verify environment variables override defaults
        assert config_manager.config.ai_provider == "anthropic"
        assert config_manager.config.openai_model == "gpt-3.5-turbo"
        assert config_manager.config.anthropic_model == "claude-3-haiku-20240307"
        assert config_manager.config.ai_max_tokens == 2000
        assert config_manager.config.ai_temperature == 0.7
        assert config_manager.config.ai_timeout == 60
        assert config_manager.config.coverage_threshold == 90.0
        assert config_manager.config.max_test_cases_per_function == 10
        assert config_manager.config.include_edge_cases is False
        assert config_manager.config.include_integration_tests is True
        assert config_manager.config.github_integration is True
        assert config_manager.config.auto_pr_comments is False
        assert config_manager.config.coverage_check_enabled is False
        assert config_manager.config.output_format == "stdout"
        assert config_manager.config.test_file_prefix == "unit_"
        assert config_manager.config.test_directory == "unit_tests"
    
    @patch.dict(os.environ, {
        'AI_MAX_TOKENS': 'invalid_number',
        'AI_TEMPERATURE': 'not_a_float',
        'COVERAGE_THRESHOLD': 'invalid_threshold'
    })
    def test_load_config_invalid_environment_variables(self):
        """Test handling of invalid environment variable values."""
        config_manager = ConfigurationManager(config_path=None)
        
        # Should keep default values when environment variables are invalid
        assert config_manager.config.ai_max_tokens == 1000  # default
        assert config_manager.config.ai_temperature == 0.3  # default
        assert config_manager.config.coverage_threshold == 80.0  # default
    
    def test_environment_variables_override_yaml(self):
        """Test that environment variables override YAML configuration."""
        # Write config to file
        with open(self.config_path, 'w') as f:
            yaml.dump(self.sample_config, f)
        
        with patch.dict(os.environ, {
            'AI_PROVIDER': 'mock',
            'AI_MAX_TOKENS': '3000',
            'COVERAGE_THRESHOLD': '95.0'
        }):
            config_manager = ConfigurationManager(config_path=self.config_path)
            
            # Environment variables should override YAML values
            assert config_manager.config.ai_provider == "mock"
            assert config_manager.config.ai_max_tokens == 3000
            assert config_manager.config.coverage_threshold == 95.0
            
            # Non-overridden values should come from YAML
            assert config_manager.config.ai_temperature == 0.5  # from YAML
            assert config_manager.config.output_format == "json"  # from YAML
    
    def test_validate_config_valid(self):
        """Test configuration validation with valid config."""
        config_manager = ConfigurationManager(config_path=None)
        
        valid_config = {
            'ai': {
                'provider': 'openai',
                'max_tokens': 1000,
                'temperature': 0.5,
                'timeout': 30
            },
            'test_generation': {
                'coverage_threshold': 85.0,
                'max_test_cases_per_function': 5
            }
        }
        
        assert config_manager.validate_config(valid_config) is True
    
    def test_validate_config_invalid_provider(self):
        """Test configuration validation with invalid AI provider."""
        config_manager = ConfigurationManager(config_path=None)
        
        invalid_config = {
            'ai': {
                'provider': 'invalid_provider'
            }
        }
        
        assert config_manager.validate_config(invalid_config) is False
    
    def test_validate_config_invalid_numeric_values(self):
        """Test configuration validation with invalid numeric values."""
        config_manager = ConfigurationManager(config_path=None)
        
        # Test invalid max_tokens
        invalid_config1 = {
            'ai': {
                'max_tokens': -100
            }
        }
        assert config_manager.validate_config(invalid_config1) is False
        
        # Test invalid temperature
        invalid_config2 = {
            'ai': {
                'temperature': 5.0  # Should be between 0 and 2
            }
        }
        assert config_manager.validate_config(invalid_config2) is False
        
        # Test invalid coverage threshold
        invalid_config3 = {
            'test_generation': {
                'coverage_threshold': 150.0  # Should be between 0 and 100
            }
        }
        assert config_manager.validate_config(invalid_config3) is False
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'ANTHROPIC_API_KEY': 'test_anthropic_key'
    })
    def test_get_available_ai_providers(self):
        """Test detection of available AI providers based on API keys."""
        config_manager = ConfigurationManager(config_path=None)
        
        available = config_manager.get_available_ai_providers()
        
        assert available['openai'] is True
        assert available['anthropic'] is True
    
    def test_get_available_ai_providers_no_keys(self):
        """Test detection when no API keys are available."""
        with patch.dict(os.environ, {}, clear=True):
            config_manager = ConfigurationManager(config_path=None)
            
            available = config_manager.get_available_ai_providers()
            
            assert available['openai'] is False
            assert available['anthropic'] is False
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_get_preferred_ai_provider_auto_mode(self):
        """Test preferred AI provider selection in auto mode."""
        config_manager = ConfigurationManager(config_path=None)
        config_manager.config.ai_provider = "auto"
        
        preferred = config_manager.get_preferred_ai_provider()
        
        assert preferred == "openai"  # Should prefer OpenAI when available
    
    def test_get_preferred_ai_provider_no_keys(self):
        """Test preferred AI provider when no API keys are available."""
        with patch.dict(os.environ, {}, clear=True):
            config_manager = ConfigurationManager(config_path=None)
            config_manager.config.ai_provider = "auto"
            
            preferred = config_manager.get_preferred_ai_provider()
            
            assert preferred == "mock"
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_key'})
    def test_get_preferred_ai_provider_specific(self):
        """Test preferred AI provider when specific provider is configured."""
        config_manager = ConfigurationManager(config_path=None)
        config_manager.config.ai_provider = "anthropic"
        
        preferred = config_manager.get_preferred_ai_provider()
        
        assert preferred == "anthropic"
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_openai_key'})
    def test_get_api_key(self):
        """Test API key retrieval."""
        config_manager = ConfigurationManager(config_path=None)
        
        openai_key = config_manager.get_api_key('openai')
        anthropic_key = config_manager.get_api_key('anthropic')
        invalid_key = config_manager.get_api_key('invalid_provider')
        
        assert openai_key == 'test_openai_key'
        assert anthropic_key is None
        assert invalid_key is None
    
    def test_get_ai_provider_config(self):
        """Test AI provider configuration retrieval."""
        config_manager = ConfigurationManager(config_path=None)
        
        ai_config = config_manager.get_ai_provider_config()
        
        expected_keys = ['provider', 'openai_model', 'anthropic_model', 'max_tokens', 'temperature', 'timeout']
        for key in expected_keys:
            assert key in ai_config
        
        assert ai_config['provider'] == config_manager.config.ai_provider
        assert ai_config['max_tokens'] == config_manager.config.ai_max_tokens
    
    def test_get_language_config_python(self):
        """Test language-specific configuration for Python."""
        config_manager = ConfigurationManager(config_path=None)
        
        python_config = config_manager.get_language_config(Language.PYTHON)
        
        assert python_config['test_framework'] == 'pytest'
        assert python_config['file_extension'] == '.py'
        assert python_config['import_style'] == 'from module import function'
        assert python_config['test_file_pattern'] == 'test_*.py'
        assert 'setup_imports' in python_config
        assert python_config['assertion_style'] == 'assert'
    
    def test_get_language_config_javascript(self):
        """Test language-specific configuration for JavaScript."""
        config_manager = ConfigurationManager(config_path=None)
        
        js_config = config_manager.get_language_config(Language.JAVASCRIPT)
        
        assert js_config['test_framework'] == 'jest'
        assert js_config['file_extension'] == '.js'
        assert js_config['import_style'] == 'const { function } = require("module")'
        assert js_config['test_file_pattern'] == '*.test.js'
        assert 'setup_imports' in js_config
        assert js_config['assertion_style'] == 'expect'
    
    def test_get_language_config_with_yaml_override(self):
        """Test language configuration with YAML file overrides."""
        # Write config with language-specific overrides
        config_with_overrides = {
            'languages': {
                'python': {
                    'test_framework': 'unittest',
                    'custom_setting': 'custom_value'
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_with_overrides, f)
        
        config_manager = ConfigurationManager(config_path=self.config_path)
        python_config = config_manager.get_language_config(Language.PYTHON)
        
        # Should merge YAML overrides with defaults
        assert python_config['test_framework'] == 'unittest'  # from YAML
        assert python_config['custom_setting'] == 'custom_value'  # from YAML
        assert python_config['file_extension'] == '.py'  # from defaults
    
    def test_get_test_generation_config(self):
        """Test test generation configuration retrieval."""
        config_manager = ConfigurationManager(config_path=None)
        
        test_config = config_manager.get_test_generation_config()
        
        expected_keys = ['coverage_threshold', 'max_test_cases_per_function', 
                        'include_edge_cases', 'include_integration_tests', 'default_test_framework']
        for key in expected_keys:
            assert key in test_config
        
        assert test_config['coverage_threshold'] == config_manager.config.coverage_threshold
        assert test_config['include_edge_cases'] == config_manager.config.include_edge_cases
    
    def test_get_output_config(self):
        """Test output configuration retrieval."""
        config_manager = ConfigurationManager(config_path=None)
        
        output_config = config_manager.get_output_config()
        
        expected_keys = ['output_format', 'test_file_prefix', 'test_directory']
        for key in expected_keys:
            assert key in output_config
        
        assert output_config['output_format'] == config_manager.config.output_format
        assert output_config['test_file_prefix'] == config_manager.config.test_file_prefix
    
    def test_get_integration_config(self):
        """Test integration configuration retrieval."""
        config_manager = ConfigurationManager(config_path=None)
        
        integration_config = config_manager.get_integration_config()
        
        expected_keys = ['github_integration', 'auto_pr_comments', 'coverage_check_enabled']
        for key in expected_keys:
            assert key in integration_config
        
        assert integration_config['github_integration'] == config_manager.config.github_integration
        assert integration_config['auto_pr_comments'] == config_manager.config.auto_pr_comments
    
    def test_save_config(self):
        """Test saving configuration to YAML file."""
        config_manager = ConfigurationManager(config_path=None)
        
        # Modify some configuration values
        config_manager.config.ai_provider = "anthropic"
        config_manager.config.coverage_threshold = 95.0
        config_manager.config.output_format = "json"
        
        # Save to file
        output_path = os.path.join(self.temp_dir, "saved_config.yaml")
        config_manager.save_config(output_path)
        
        # Verify file was created and contains expected data
        assert os.path.exists(output_path)
        
        with open(output_path, 'r') as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config['ai']['provider'] == "anthropic"
        assert saved_config['test_generation']['coverage_threshold'] == 95.0
        assert saved_config['output']['output_format'] == "json"
        
        # Verify structure is organized into sections
        expected_sections = ['ai', 'test_generation', 'output', 'integration']
        for section in expected_sections:
            assert section in saved_config


class TestTestGeneratorConfig:
    """Test suite for TestGeneratorConfig dataclass."""
    
    def test_default_values(self):
        """Test that TestGeneratorConfig initializes with correct defaults."""
        config = TestGeneratorConfig()
        
        # AI Configuration defaults
        assert config.ai_provider == "auto"
        assert config.openai_model == "gpt-4"
        assert config.anthropic_model == "claude-3-sonnet-20240229"
        assert config.ai_max_tokens == 1000
        assert config.ai_temperature == 0.3
        assert config.ai_timeout == 30
        
        # Test Generation defaults
        assert config.coverage_threshold == 80.0
        assert config.max_test_cases_per_function == 5
        assert config.include_edge_cases is True
        assert config.include_integration_tests is True
        
        # Output defaults
        assert config.output_format == "files"
        assert config.test_file_prefix == "test_"
        assert config.test_directory == "tests"
        
        # CI/CD defaults
        assert config.github_integration is False
        assert config.auto_pr_comments is True
        assert config.coverage_check_enabled is True
    
    def test_default_test_framework_initialization(self):
        """Test that default test framework is properly initialized."""
        config = TestGeneratorConfig()
        
        expected_frameworks = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "java": "junit"
        }
        
        assert config.default_test_framework == expected_frameworks
    
    def test_custom_initialization(self):
        """Test TestGeneratorConfig with custom values."""
        custom_frameworks = {
            "python": "unittest",
            "javascript": "mocha"
        }
        
        config = TestGeneratorConfig(
            ai_provider="openai",
            ai_max_tokens=2000,
            coverage_threshold=90.0,
            default_test_framework=custom_frameworks
        )
        
        assert config.ai_provider == "openai"
        assert config.ai_max_tokens == 2000
        assert config.coverage_threshold == 90.0
        assert config.default_test_framework == custom_frameworks


if __name__ == "__main__":
    pytest.main([__file__])