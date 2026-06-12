"""
Tests for the root endpoint (GET /).
Uses AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestRootEndpoint:
    """Test suite for GET / endpoint"""
    
    def test_root_redirects_to_static_index_html(self, client):
        """
        Arrange: TestClient is available via fixture.
        Act: Request the root path.
        Assert: Verify redirect to /static/index.html.
        """
        # Arrange: (fixture already provides client)
        
        # Act: Make request to root endpoint
        response = client.get("/", follow_redirects=False)
        
        # Assert: Verify it's a redirect
        assert response.status_code in [307, 302], "Root should return redirect status"
        assert "/static/index.html" in response.headers.get("location", ""), \
            "Redirect should point to /static/index.html"
