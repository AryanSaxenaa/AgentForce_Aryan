"""
Integration tests for the complete AI provider system
"""
import pytest
import os
from unittest.mock import patch, Mock
from src.config.ai_provider_manager import AIProviderManager
from src.config.configuration_manager import ConfigurationManager
from src.factories.ai_provider_factory import AIProviderFactory, MockAIProvider
from src.interfaces.base_interfaces import TestCase, TestType


class TestAIProviderSystemIntegration:
    """Integration tests for the complete AI provider system."""
    
    def test_complete_system_no_api_keys(self):
        """Test the complete system works with no API keys (mock mode)."""
        with patch.dict(os.environ, {}, clear=True):
            # Initialize the complete system
            config_manager = ConfigurationManager(config_path=None)
            ai_manager = AIProviderManager(config_manager)
            
            # Get provider (should be mock)
            provider = ai_manager.get_provider()
            assert isinstance(provider, MockAIProvider)
            
            # Test provider functionality
            test_case = TestCase(
                name="test_example",
                test_type=TestType.UNIT,
                function_name="example_function",
                description="Test example function",
                test_code="def test_example(): pass"
            )
            
            # Test enhancement
            enhancement = provider.enhance_test_case(test_case, {'language': 'python'})
            assert enhancement is not None
            assert 'code' in enhancement
            assert 'description' in enhancement
            
            # Test suggestions
            suggestions = provider.suggest_test_improvements(test_case, {'language': 'python'})
            assert isinstance(suggestions, str)
            assert len(suggestions) > 0
            
            # Test code analysis
            analysis = provider.analyze_code_patterns("def example(): return True", "python")
            assert isinstance(analysis, dict)
            assert 'analysis' in analysis
            assert analysis['provider'] == 'mock'
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.factories.ai_provider_factory.openai')
    def test_complete_system_with_openai(self, mock_openai):
        """Test the complete system works with OpenAI provider."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Enhanced test with OpenAI"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        # Initialize the complete system
        config_manager = ConfigurationManager(config_path=None)
        ai_manager = AIProviderManager(config_manager)
        
        # Get provider (should be OpenAI)
        provider = ai_manager.get_provider()
        assert not isinstance(provider, MockAIProvider)
        
        # Test provider functionality
        test_case = TestCase(
            name="test_example",
            test_type=TestType.UNIT,
            function_name="example_function",
            description="Test example function",
            test_code="def test_example(): pass"
        )
        
        # Test code analysis (this should work with mocked OpenAI)
        analysis = provider.analyze_code_patterns("def example(): return True", "python")
        assert isinstance(analysis, dict)
        assert 'analysis' in analysis
        assert analysis['provider'] == 'openai'
    
    def test_provider_fallback_system(self):
        """Test the provider fallback system works correctly."""
        with patch.dict(os.environ, {}, clear=True):
            ai_manager = AIProviderManager()
            
            # Test provider info shows correct fallback
            info = ai_manager.get_provider_info()
            assert info['current_provider'] == 'mock'
            assert info['has_ai_capability'] is False
            
            # Test recommendations
            recommendations = ai_manager.get_fallback_recommendations()
            assert len(recommendations) > 0
            assert any("No AI providers configured" in rec for rec in recommendations)
    
    def test_provider_health_monitoring(self):
        """Test the provider health monitoring system."""
        ai_manager = AIProviderManager()
        
        # Test mock provider health
        assert ai_manager.test_provider_connection('mock') is True
        
        # Test provider without API key
        assert ai_manager.test_provider_connection('openai') is False
        
        # Test all providers
        health_results = ai_manager.test_all_providers()
        assert 'mock' in health_results
        assert health_results['mock'] is True
    
    def test_configuration_integration(self):
        """Test integration with configuration system."""
        config_manager = ConfigurationManager(config_path=None)
        ai_manager = AIProviderManager(config_manager)
        
        # Test AI provider config
        ai_config = config_manager.get_ai_provider_config()
        assert 'provider' in ai_config
        assert 'openai_model' in ai_config
        assert 'anthropic_model' in ai_config
        
        # Test available providers detection
        available = config_manager.get_available_ai_providers()
        assert 'openai' in available
        assert 'anthropic' in available
        
        # Test preferred provider selection
        preferred = config_manager.get_preferred_ai_provider()
        assert preferred in ['openai', 'anthropic', 'mock']
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.factories.ai_provider_factory.openai')
    def test_provider_switching(self, mock_openai):
        """Test switching between providers."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "OpenAI response"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        ai_manager = AIProviderManager()
        
        # Initially should get OpenAI provider
        provider1 = ai_manager.get_provider()
        assert not isinstance(provider1, MockAIProvider)
        
        # Force switch to mock
        assert ai_manager.force_provider('mock') is True
        provider2 = ai_manager.get_provider()
        assert isinstance(provider2, MockAIProvider)
        
        # Reset and should get OpenAI again
        ai_manager.reset_provider()
        provider3 = ai_manager.get_provider()
        assert not isinstance(provider3, MockAIProvider)
    
    def test_factory_provider_registration(self):
        """Test custom provider registration through factory."""
        factory = AIProviderFactory()
        
        # Create custom provider
        class CustomTestProvider(MockAIProvider):
            def analyze_code_patterns(self, code: str, language: str):
                return {
                    'analysis': f'Custom analysis for {language} code',
                    'provider': 'custom'
                }
        
        # Register custom provider
        factory.register_provider('custom_test', CustomTestProvider)
        
        # Create and test custom provider
        provider = factory.create_provider('custom_test', {})
        assert isinstance(provider, CustomTestProvider)
        
        result = provider.analyze_code_patterns("test code", "python")
        assert result['provider'] == 'custom'
        assert 'Custom analysis' in result['analysis']


class TestAIProviderErrorHandling:
    """Test error handling in the AI provider system."""
    
    def test_invalid_provider_type(self):
        """Test handling of invalid provider types."""
        factory = AIProviderFactory()
        
        with pytest.raises(ValueError, match="Unsupported AI provider"):
            factory.create_provider('invalid_provider', {})
    
    def test_provider_creation_failure(self):
        """Test handling of provider creation failures."""
        ai_manager = AIProviderManager()
        
        # Try to force an invalid provider
        assert ai_manager.force_provider('invalid_provider') is False
    
    @patch('src.factories.ai_provider_factory.openai', None)
    def test_missing_openai_package(self):
        """Test handling when OpenAI package is not installed."""
        factory = AIProviderFactory()
        
        # Should fall back to mock when OpenAI package is missing
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            provider = factory.create_provider('openai', {})
            assert isinstance(provider, MockAIProvider)
    
    @patch('src.factories.ai_provider_factory.anthropic', None)
    def test_missing_anthropic_package(self):
        """Test handling when Anthropic package is not installed."""
        factory = AIProviderFactory()
        
        # Should fall back to mock when Anthropic package is missing
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test_key'}):
            provider = factory.create_provider('anthropic', {})
            assert isinstance(provider, MockAIProvider)


class TestAIProviderPerformance:
    """Test performance aspects of the AI provider system."""
    
    def test_provider_caching(self):
        """Test that providers are cached and reused."""
        ai_manager = AIProviderManager()
        
        # Get provider twice
        provider1 = ai_manager.get_provider()
        provider2 = ai_manager.get_provider()
        
        # Should be the same instance (cached)
        assert provider1 is provider2
    
    def test_provider_reset_clears_cache(self):
        """Test that resetting clears the provider cache."""
        ai_manager = AIProviderManager()
        
        # Get provider
        provider1 = ai_manager.get_provider()
        
        # Reset
        ai_manager.reset_provider()
        
        # Get provider again
        provider2 = ai_manager.get_provider()
        
        # Should be different instances
        assert provider1 is not provider2
    
    def test_health_check_caching(self):
        """Test that health check results are cached."""
        ai_manager = AIProviderManager()
        
        # Test provider connection
        result1 = ai_manager.test_provider_connection('mock')
        
        # Check that health status is cached
        assert 'mock' in ai_manager._provider_health
        assert ai_manager._provider_health['mock'] is True
        
        # Test again - should use cached result
        result2 = ai_manager.test_provider_connection('mock')
        assert result1 == result2