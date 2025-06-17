"""
Tests to improve coverage for client.py module.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, mock_open, MagicMock
import httpx
from lucidpy.client import LucidchartClient
from lucidpy.models import Document


class TestLucidchartClientCoverage:
    """Test coverage for LucidchartClient methods."""

    def test_init_with_config_file(self):
        """Test initialization with config.toml file."""
        # Create a temporary config file
        config_content = """
[api]
key = "test-api-key-from-config"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write(config_content)
            config_path = f.name

        try:
            # Mock toml.load to return our test config
            with patch('lucidpy.client.toml.load') as mock_load:
                mock_load.return_value = {"api": {"key": "test-api-key-from-config"}}

                client = LucidchartClient()  # No API key provided

                assert client.api_key == "test-api-key-from-config"
                mock_load.assert_called_once_with("config.toml")
        finally:
            os.unlink(config_path)

    @patch('lucidpy.client.httpx.request')
    def test_make_request_success(self, mock_request):
        """Test successful HTTP request."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "id": "doc123"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        client = LucidchartClient(api_key="test-key")
        result = client._make_request("GET", "/test-endpoint")

        assert result == {"success": True, "id": "doc123"}
        mock_request.assert_called_once()

        # Check the request was made with correct parameters
        call_args = mock_request.call_args
        assert call_args[0][0] == "GET"  # method
        assert call_args[0][1] == "https://api.lucid.co/test-endpoint"  # url
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-key"
        assert call_args[1]["headers"]["Lucid-Api-Version"] == "1"

    @patch('lucidpy.client.httpx.request')
    def test_make_request_http_error(self, mock_request):
        """Test HTTP request with error response."""
        # Mock response that raises HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPError("API Error")
        mock_request.return_value = mock_response

        client = LucidchartClient(api_key="test-key")

        with pytest.raises(httpx.HTTPError):
            client._make_request("POST", "/error-endpoint")

    def test_create_document_validation_errors(self):
        """Test create_document validation errors."""
        client = LucidchartClient(api_key="test-key")

        # Test: Both document and json provided
        doc = Document.create("Test")
        with pytest.raises(ValueError, match="Only one of document or json must be provided"):
            client.create_document("Test Title", document=doc, json='{"test": true}')

        # Test: Neither document nor json provided
        with pytest.raises(ValueError, match="Either document or json must be provided"):
            client.create_document("Test Title")

    @patch('lucidpy.client.httpx.request')
    @patch('tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open)
    def test_create_document_with_json_string(self, mock_file_open, mock_temp_file, mock_request):
        """Test create_document with JSON string."""
        # Mock tempfile and request
        mock_temp_file.return_value.__enter__.return_value.name = "/tmp/test.lucid"
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "documentId": "doc123"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        client = LucidchartClient(api_key="test-key")

        json_data = '{"version": 1, "pages": []}'
        result = client.create_document("Test Document", json=json_data)

        assert result == {"success": True, "documentId": "doc123"}
        mock_request.assert_called_once()

        # Verify the request was made with correct files parameter
        call_args = mock_request.call_args
        assert call_args[1]["files"]["title"][1] == "Test Document"
        assert call_args[1]["files"]["product"][1] == "lucidchart"

    @patch('lucidpy.client.httpx.request')
    @patch('tempfile.NamedTemporaryFile')
    @patch('builtins.open', new_callable=mock_open)
    def test_create_document_with_document_object(self, mock_file_open, mock_temp_file, mock_request):
        """Test create_document with Document object."""
        # Mock tempfile and request
        mock_temp_file.return_value.__enter__.return_value.name = "/tmp/test.lucid"
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "documentId": "doc456"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        client = LucidchartClient(api_key="test-key")

        # Create a document object
        doc = Document.create("Test Page")
        result = client.create_document("Test Document", document=doc)

        assert result == {"success": True, "documentId": "doc456"}
        mock_request.assert_called_once()

        # Verify the document was serialized to JSON
        call_args = mock_request.call_args
        assert call_args[1]["files"]["title"][1] == "Test Document"


class TestClientIntegration:
    """Integration tests for client functionality."""

    def test_client_with_real_document_structure(self):
        """Test client with a real document structure (no actual API call)."""
        client = LucidchartClient(api_key="test-key")

        # Create a complex document
        doc = Document.create("Integration Test")
        page = doc.pages[0]

        # Add shapes and connections
        start = page.add_shape("circle", x=50, y=50, text="Start")
        process = page.add_shape("rectangle", x=200, y=50, text="Process")
        end = page.add_shape("circle", x=350, y=50, text="End")

        page.connect_shapes(start, process)
        page.connect_shapes(process, end)

        # Test document serialization (what would be sent to API)
        json_output = doc.model_dump_json()

        # Verify the JSON contains expected structure
        import json
        parsed = json.loads(json_output)

        assert parsed["version"] == 1
        assert len(parsed["pages"]) == 1
        assert len(parsed["pages"][0]["shapes"]) == 3
        assert len(parsed["pages"][0]["lines"]) == 2

        # Verify IDs were generated
        for shape in parsed["pages"][0]["shapes"]:
            assert shape["id"].startswith("shape-")
        for line in parsed["pages"][0]["lines"]:
            assert line["id"].startswith("line-")
