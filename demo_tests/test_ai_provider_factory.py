"""
Unit tests for AI Provider Factory and AI Provider implementations
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.factories.ai_provider_factory import (
    AIProviderFactory, 
    OpenAIProvider, 
    AnthropicProvider, 
    MockAIProvider
)
from src.interfaces.base_interfaces import TestCase, TestType


class TestAIProviderFactory:
    """Test cases for AIProviderFactory."""
    
    def test_factory_initialization(self):
        """Test factory initializes with correct providers."""
        factory = AIProviderFactory()
        
        supported_providers = factory.get_supported_providers()
        assert 'openai' in supported_providers
        assert 'anthropic' in supported_providers
        assert 'mock' in supported_providers
    
    def test_create_mock_provider(self):
        """Test creating mock provider."""
        factory = AIProviderFactory()
        config = {'max_tokens': 1000}
        
        provider = factory.create_provider('mock', config)
        
        assert isinstance(provider, MockAIProvider)
        assert provider.config == config
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.factories.ai_provider_factory._OpenAIClient')
    def test_create_openai_provider_with_key(self, mock_openai):
        """Test creating OpenAI provider when API key is available."""
        factory = AIProviderFactory()
        config = {'openai_model': 'gpt-4', 'max_tokens': 1000}
        
        provider = factory.create_provider('openai', config)
        
        assert isinstance(provider, OpenAIProvider)
        assert provider.api_key == 'test_key'
        assert provider.model == 'gpt-4'
        assert provider.max_tokens == 1000
    
    @patch.dict(os.environ, {}, clear=True)
    def test_create_openai_provider_without_key(self):
        """Test creating OpenAI provider falls back to mock when no API key."""
        factory = AIProviderFactory()
        config = {'openai_model': 'gpt-4'}
        
        provider = factory.create_provider('openai', config)
        
        assert isinstance(provider, MockAIProvider)
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_key'})
    @patch('src.factories.ai_provider_factory._AnthropicClient')
    def test_create_anthropic_provider_with_key(self, mock_anthropic):
        """Test creating Anthropic provider when API key is available."""
        factory = AIProviderFactory()
        config = {'anthropic_model': 'claude-3-sonnet-20240229', 'max_tokens': 1000}
        
        provider = factory.create_provider('anthropic', config)
        
        assert isinstance(provider, AnthropicProvider)
        assert provider.api_key == 'test_key'
        assert provider.model == 'claude-3-sonnet-20240229'
        assert provider.max_tokens == 1000
    
    @patch.dict(os.environ, {}, clear=True)
    def test_create_anthropic_provider_without_key(self):
        """Test creating Anthropic provider falls back to mock when no API key."""
        factory = AIProviderFactory()
        config = {'anthropic_model': 'claude-3-sonnet-20240229'}
        
        provider = factory.create_provider('anthropic', config)
        
        assert isinstance(provider, MockAIProvider)
    
    def test_create_unsupported_provider(self):
        """Test creating unsupported provider raises ValueError."""
        factory = AIProviderFactory()
        config = {}
        
        with pytest.raises(ValueError, match="Unsupported AI provider: unsupported"):
            factory.create_provider('unsupported', config)
    
    def test_register_custom_provider(self):
        """Test registering a custom provider."""
        factory = AIProviderFactory()
        
        class CustomProvider(MockAIProvider):
            pass
        
        factory.register_provider('custom', CustomProvider)
        
        assert 'custom' in factory.get_supported_providers()
        provider = factory.create_provider('custom', {})
        assert isinstance(provider, CustomProvider)


class TestMockAIProvider:
    """Test cases for MockAIProvider."""
    
    def test_mock_provider_initialization(self):
        """Test mock provider initializes correctly."""
        config = {'max_tokens': 500}
        provider = MockAIProvider(config)
        
        assert provider.config == config
    
    def test_mock_provider_initialization_no_config(self):
        """Test mock provider initializes with empty config."""
        provider = MockAIProvider()
        
        assert provider.config == {}
    
    def test_enhance_test_case(self):
        """Test mock provider enhances test cases."""
        provider = MockAIProvider()
        test_case = TestCase(
            name="test_function",
            test_type=TestType.UNIT,
            function_name="my_function",
            description="Test my function",
            test_code="def test_function(): pass"
        )
        context = {'language': 'python'}
        
        result = provider.enhance_test_case(test_case, context)
        
        assert result is not None
        assert 'code' in result
        assert 'description' in result
        assert 'assertions' in result
        assert result['description'] == "Enhanced: Test my function"
        assert len(result['assertions']) == 3
    
    def test_enhance_test_case_edge_type(self):
        """Test mock provider handles edge test cases differently."""
        provider = MockAIProvider()
        test_case = TestCase(
            name="test_edge_case",
            test_type=TestType.EDGE,
            function_name="my_function",
            description="Test edge case",
            test_code="def test_edge_case(): # Assert"
        )
        context = {'language': 'python'}
        
        result = provider.enhance_test_case(test_case, context)
        
        assert result is not None
        assert 'pytest.raises' in result['code']
    
    def test_suggest_test_improvements(self):
        """Test mock provider suggests test improvements."""
        provider = MockAIProvider()
        test_case = TestCase(
            name="test_function",
            test_type=TestType.UNIT,
            function_name="my_function",
            description="Test my function",
            test_code="def test_function(): pass"
        )
        context = {'language': 'python'}
        
        suggestions = provider.suggest_test_improvements(test_case, context)
        
        assert isinstance(suggestions, str)
        assert "Consider adding more specific assertions" in suggestions
        assert "Set OPENAI_API_KEY or ANTHROPIC_API_KEY" in suggestions
    
    def test_analyze_code_patterns(self):
        """Test mock provider analyzes code patterns."""
        provider = MockAIProvider()
        code = "def my_function(x): return x * 2"
        language = "python"
        
        result = provider.analyze_code_patterns(code, language)
        
        assert isinstance(result, dict)
        assert 'analysis' in result
        assert 'provider' in result
        assert result['provider'] == 'mock'
        assert 'python' in result['analysis']
        assert 'Set OPENAI_API_KEY or ANTHROPIC_API_KEY' in result['analysis']


class TestOpenAIProvider:
    """Test cases for OpenAIProvider."""
    
    @patch('src.factories.ai_provider_factory._OpenAIClient')
    def test_openai_provider_initialization(self, mock_openai):
        """Test OpenAI provider initializes correctly."""
        api_key = 'test_key'
        config = {
            'openai_model': 'gpt-4',
            'max_tokens': 1000,
            'temperature': 0.3,
            'timeout': 30
        }
        
        provider = OpenAIProvider(api_key, config)
        
        assert provider.api_key == api_key
        assert provider.model == 'gpt-4'
        assert provider.max_tokens == 1000
        assert provider.temperature == 0.3
        assert provider.timeout == 30
        mock_openai.OpenAI.assert_called_once_with(api_key=api_key, timeout=30)
    
    @patch('src.factories.ai_provider_factory._OpenAIClient')
    def test_openai_provider_initialization_defaults(self, mock_openai):
        """Test OpenAI provider uses defaults when config values missing."""
        api_key = 'test_key'
        config = {}
        
        provider = OpenAIProvider(api_key, config)
        
        assert provider.model == 'gpt-4'  # default
        assert provider.max_tokens == 1000  # default
        assert provider.temperature == 0.3  # default
        assert provider.timeout == 30  # default
    
    def test_openai_provider_missing_package(self):
        """Test OpenAI provider raises ImportError when package not installed."""
        with patch('src.factories.ai_provider_factory._OpenAIClient', None):
            with pytest.raises(ImportError, match="openai package not installed"):
                OpenAIProvider('test_key', {})
    
    @patch('src.factories.ai_provider_factory._OpenAIClient')
    def test_enhance_test_case_success(self, mock_openai):
        """Test OpenAI provider successfully enhances test case."""
        # Setup mock client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
ENHANCED_CODE:
def test_enhanced():
    result = my_function(5)
    assert result == 10

DESCRIPTION:
Added specific assertion and realistic test data

ASSERTIONS:
- assert result == 10
- assert isinstance(result, int)
"""
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        provider = OpenAIProvider('test_key', {})
        test_case = TestCase(
            name="test_function",
            test_type=TestType.UNIT,
            function_name="my_function",
            description="Test my function",
            test_code="def test_function(): pass"
        )
        context = {'language': 'python'}
        
        result = provider.enhance_test_case(test_case, context)
        
        assert result is not None
        assert 'code' in result
        assert 'description' in result
        assert 'assertions' in result
        assert 'def test_enhanced():' in result['code']
        assert 'Added specific assertion' in result['description']
        assert len(result['assertions']) == 2
    
    @patch('src.factories.ai_provider_factory._OpenAIClient')
    def test_enhance_test_case_api_error(self, mock_openai):
        """Test OpenAI provider handles API errors gracefully."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.OpenAI.return_value = mock_client
        
        provider = OpenAIProvider('test_key', {})
        test_case = TestCase(
            name="test_function",
            test_type=TestType.UNIT,
            function_name="my_function",
            description="Test my function",
            test_code="def test_function(): pass"
        )
        context = {'language': 'python'}
        
        result = provider.enhance_test_case(test_case, context)
        
        assert result is None
    
    @patch('src.factories.ai_provider_factory._OpenAIClient')
    def test_suggest_test_improvements_success(self, mock_openai):
        """Test OpenAI provider successfully suggests improvements."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "1. Add more assertions\n2. Use realistic data"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        provider = OpenAIProvider('test_key', {})
        test_case = TestCase(
            name="test_function",
            test_type=TestType.UNIT,
            function_name="my_function",
            description="Test my function",
            test_code="def test_function(): pass"
        )
        context = {'language': 'python'}
        
        suggestions = provider.suggest_test_improvements(test_case, context)
        
        assert suggestions == "1. Add more assertions\n2. Use realistic data"
    
    @patch('src.factories.ai_provider_factory._OpenAIClient')
    def test_analyze_code_patterns_success(self, mock_openai):
        """Test OpenAI provider successfully analyzes code patterns."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Code analysis: Simple function detected"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        provider = OpenAIProvider('test_key', {})
        code = "def my_function(x): return x * 2"
        language = "python"
        
        result = provider.analyze_code_patterns(code, language)
        
        assert isinstance(result, dict)
        assert result['analysis'] == "Code analysis: Simple function detected"
        assert result['provider'] == 'openai'


class TestAnthropicProvider:
    """Test cases for AnthropicProvider."""
    
    @patch('src.factories.ai_provider_factory._AnthropicClient')
    def test_anthropic_provider_initialization(self, mock_anthropic):
        """Test Anthropic provider initializes correctly."""
        api_key = 'test_key'
        config = {
            'anthropic_model': 'claude-3-sonnet-20240229',
            'max_tokens': 1000,
            'temperature': 0.3,
            'timeout': 30
        }
        
        provider = AnthropicProvider(api_key, config)
        
        assert provider.api_key == api_key
        assert provider.model == 'claude-3-sonnet-20240229'
        assert provider.max_tokens == 1000
        assert provider.temperature == 0.3
        assert provider.timeout == 30
        mock_anthropic.Anthropic.assert_called_once_with(api_key=api_key, timeout=30)
    
    def test_anthropic_provider_missing_package(self):
        """Test Anthropic provider raises ImportError when package not installed."""
        with patch('src.factories.ai_provider_factory._AnthropicClient', None):
            with pytest.raises(ImportError, match="anthropic package not installed"):
                AnthropicProvider('test_key', {})
    
    @patch('src.factories.ai_provider_factory._AnthropicClient')
    def test_enhance_test_case_success(self, mock_anthropic):
        """Test Anthropic provider successfully enhances test case."""
        # Setup mock client
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = """
ENHANCED_CODE:
def test_enhanced():
    result = my_function(5)
    assert result == 10

DESCRIPTION:
Added specific assertion and realistic test data

ASSERTIONS:
- assert result == 10
- assert isinstance(result, int)
"""
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client
        
        provider = AnthropicProvider('test_key', {})
        test_case = TestCase(
            name="test_function",
            test_type=TestType.UNIT,
            function_name="my_function",
            description="Test my function",
            test_code="def test_function(): pass"
        )
        context = {'language': 'python'}
        
        result = provider.enhance_test_case(test_case, context)
        
        assert result is not None
        assert 'code' in result
        assert 'description' in result
        assert 'assertions' in result
        assert 'def test_enhanced():' in result['code']
        assert 'Added specific assertion' in result['description']
        assert len(result['assertions']) == 2
    
    @patch('src.factories.ai_provider_factory._AnthropicClient')
    def test_enhance_test_case_api_error(self, mock_anthropic):
        """Test Anthropic provider handles API errors gracefully."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.Anthropic.return_value = mock_client
        
        provider = AnthropicProvider('test_key', {})
        test_case = TestCase(
            name="test_function",
            test_type=TestType.UNIT,
            function_name="my_function",
            description="Test my function",
            test_code="def test_function(): pass"
        )
        context = {'language': 'python'}
        
        result = provider.enhance_test_case(test_case, context)
        
        assert result is None