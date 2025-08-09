"""
Unit tests for AI Provider Manager
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.config.ai_provider_manager import AIProviderManager
from src.config.configuration_manager import ConfigurationManager
from src.factories.ai_provider_factory import AIProviderFactory, MockAIProvider


class TestAIProviderManager:
    """Test cases for AIProviderManager."""
    
    def test_manager_initialization(self):
        """Test manager initializes correctly."""
        manager = AIProviderManager()
        
        assert manager.config_manager is not None
        assert isinstance(manager.factory, AIProviderFactory)
        assert manager._current_provider is None
        assert manager._fallback_order == ['openai', 'anthropic', 'mock']
    
    def test_manager_initialization_with_config(self):
        """Test manager initializes with provided config manager."""
        config_manager = Mock(spec=ConfigurationManager)
        manager = AIProviderManager(config_manager)
        
        assert manager.config_manager is config_manager
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_provider_no_api_keys(self):
        """Test get_provider returns mock when no API keys available."""
        manager = AIProviderManager()
        
        provider = manager.get_provider()
        
        assert isinstance(provider, MockAIProvider)
        assert manager._current_provider is provider
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.factories.ai_provider_factory.openai')
    def test_get_provider_with_openai_key(self, mock_openai):
        """Test get_provider returns OpenAI provider when key available."""
        # Mock the OpenAI client to avoid actual API calls
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "test analysis"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        manager = AIProviderManager()
        
        provider = manager.get_provider()
        
        # Should get OpenAI provider since it's preferred and available
        assert provider is not None
        assert manager._current_provider is provider
    
    def test_get_provider_info_no_keys(self):
        """Test get_provider_info returns correct information when no API keys."""
        with patch.dict(os.environ, {}, clear=True):
            manager = AIProviderManager()
            
            info = manager.get_provider_info()
            
            assert info['current_provider'] == 'mock'
            assert info['available_providers']['openai'] is False
            assert info['available_providers']['anthropic'] is False
            assert info['has_ai_capability'] is False
            assert info['fallback_order'] == ['openai', 'anthropic', 'mock']
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key', 'ANTHROPIC_API_KEY': 'test_key'})
    def test_get_provider_info_with_keys(self):
        """Test get_provider_info returns correct information when API keys available."""
        manager = AIProviderManager()
        
        info = manager.get_provider_info()
        
        assert info['current_provider'] == 'openai'  # Should prefer OpenAI
        assert info['available_providers']['openai'] is True
        assert info['available_providers']['anthropic'] is True
        assert info['has_ai_capability'] is True
    
    def test_test_provider_connection_mock(self):
        """Test testing mock provider connection always succeeds."""
        manager = AIProviderManager()
        
        result = manager.test_provider_connection('mock')
        
        assert result is True
        assert manager._provider_health['mock'] is True
    
    @patch.dict(os.environ, {}, clear=True)
    def test_test_provider_connection_no_api_key(self):
        """Test testing provider connection fails when no API key."""
        manager = AIProviderManager()
        
        result = manager.test_provider_connection('openai')
        
        assert result is False
        assert manager._provider_health['openai'] is False
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.factories.ai_provider_factory.openai')
    def test_test_provider_connection_success(self, mock_openai):
        """Test testing provider connection succeeds with valid API key."""
        # Mock successful API response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "test analysis"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        manager = AIProviderManager()
        
        result = manager.test_provider_connection('openai')
        
        assert result is True
        assert manager._provider_health['openai'] is True
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.factories.ai_provider_factory.openai')
    def test_test_provider_connection_api_error(self, mock_openai):
        """Test testing provider connection fails with API error."""
        # Mock API error
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.OpenAI.return_value = mock_client
        
        manager = AIProviderManager()
        
        result = manager.test_provider_connection('openai')
        
        assert result is False
        assert manager._provider_health['openai'] is False
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key', 'ANTHROPIC_API_KEY': 'test_key'})
    def test_test_all_providers(self):
        """Test testing all providers."""
        with patch.object(AIProviderManager, 'test_provider_connection') as mock_test:
            mock_test.side_effect = lambda provider: provider == 'mock'
            
            manager = AIProviderManager()
            
            results = manager.test_all_providers()
            
            # Should test available providers and mock
            assert 'mock' in results
            assert results['mock'] is True
    
    @patch('src.factories.ai_provider_factory.openai')
    def test_force_provider_success(self, mock_openai):
        """Test forcing a specific provider succeeds."""
        mock_openai.OpenAI.return_value = Mock()
        
        manager = AIProviderManager()
        
        result = manager.force_provider('mock')
        
        assert result is True
        assert isinstance(manager._current_provider, MockAIProvider)
    
    def test_force_provider_failure(self):
        """Test forcing an invalid provider fails."""
        manager = AIProviderManager()
        
        result = manager.force_provider('invalid_provider')
        
        assert result is False
    
    def test_reset_provider(self):
        """Test resetting provider clears current provider and health."""
        manager = AIProviderManager()
        manager._current_provider = Mock()
        manager._provider_health = {'openai': True}
        
        manager.reset_provider()
        
        assert manager._current_provider is None
        assert manager._provider_health == {}
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_fallback_recommendations_no_providers(self):
        """Test fallback recommendations when no providers configured."""
        manager = AIProviderManager()
        
        recommendations = manager.get_fallback_recommendations()
        
        assert len(recommendations) >= 3
        assert any("No AI providers configured" in rec for rec in recommendations)
        assert any("OPENAI_API_KEY" in rec for rec in recommendations)
        assert any("mock provider" in rec for rec in recommendations)
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_get_fallback_recommendations_partial_setup(self):
        """Test fallback recommendations with partial setup."""
        manager = AIProviderManager()
        
        recommendations = manager.get_fallback_recommendations()
        
        # Should suggest setting up both providers for reliability
        assert any("both OpenAI and Anthropic" in rec for rec in recommendations)
    
    def test_get_fallback_recommendations_unhealthy_providers(self):
        """Test fallback recommendations with unhealthy providers."""
        manager = AIProviderManager()
        manager._provider_health = {'openai': False, 'anthropic': False}
        
        recommendations = manager.get_fallback_recommendations()
        
        assert any("not responding correctly" in rec for rec in recommendations)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_create_best_provider_no_keys(self):
        """Test creating best provider falls back to mock when no keys."""
        manager = AIProviderManager()
        
        provider = manager._create_best_provider()
        
        assert isinstance(provider, MockAIProvider)
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.factories.ai_provider_factory.openai')
    def test_create_best_provider_openai_success(self, mock_openai):
        """Test creating best provider succeeds with OpenAI."""
        # Mock successful API response for quick test
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "test analysis"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        manager = AIProviderManager()
        
        provider = manager._create_best_provider()
        
        # Should successfully create OpenAI provider
        assert provider is not None
        assert not isinstance(provider, MockAIProvider)
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    @patch('src.factories.ai_provider_factory.openai')
    def test_create_best_provider_openai_fails_fallback_mock(self, mock_openai):
        """Test creating best provider falls back to mock when OpenAI fails."""
        # Mock API failure
        mock_openai.OpenAI.side_effect = Exception("API Error")
        
        manager = AIProviderManager()
        
        provider = manager._create_best_provider()
        
        # Should fall back to mock provider
        assert isinstance(provider, MockAIProvider)
    
    def test_quick_provider_test_mock(self):
        """Test quick provider test always passes for mock."""
        manager = AIProviderManager()
        mock_provider = MockAIProvider()
        
        result = manager._quick_provider_test(mock_provider, 'mock')
        
        assert result is True
    
    @patch('src.factories.ai_provider_factory.openai')
    def test_quick_provider_test_success(self, mock_openai):
        """Test quick provider test succeeds with valid response."""
        # Create a mock provider that returns valid response
        mock_provider = Mock()
        mock_provider.analyze_code_patterns.return_value = {
            'analysis': 'test analysis',
            'provider': 'openai'
        }
        
        manager = AIProviderManager()
        
        result = manager._quick_provider_test(mock_provider, 'openai')
        
        assert result is True
        assert manager._provider_health['openai'] is True
    
    def test_quick_provider_test_failure(self):
        """Test quick provider test fails with invalid response."""
        mock_provider = Mock()
        mock_provider.analyze_code_patterns.side_effect = Exception("Test error")
        
        manager = AIProviderManager()
        
        result = manager._quick_provider_test(mock_provider, 'openai')
        
        assert result is False
        assert manager._provider_health['openai'] is False
    
    def test_quick_provider_test_invalid_response(self):
        """Test quick provider test fails with invalid response format."""
        mock_provider = Mock()
        mock_provider.analyze_code_patterns.return_value = None
        
        manager = AIProviderManager()
        
        result = manager._quick_provider_test(mock_provider, 'openai')
        
        assert result is False
        assert manager._provider_health['openai'] is False


class TestAIProviderManagerIntegration:
    """Integration tests for AIProviderManager with real configuration."""
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_integration_with_real_config_manager(self):
        """Test manager works with real configuration manager."""
        config_manager = ConfigurationManager(config_path=None)
        manager = AIProviderManager(config_manager)
        
        # Should be able to get provider info
        info = manager.get_provider_info()
        
        assert 'current_provider' in info
        assert 'available_providers' in info
        assert 'has_ai_capability' in info
    
    def test_integration_provider_selection_logic(self):
        """Test the complete provider selection logic."""
        with patch.dict(os.environ, {}, clear=True):
            manager = AIProviderManager()
            
            # Should fall back to mock
            provider = manager.get_provider()
            assert isinstance(provider, MockAIProvider)
            
            # Provider info should reflect mock usage
            info = manager.get_provider_info()
            assert info['current_provider'] == 'mock'
            assert info['has_ai_capability'] is False