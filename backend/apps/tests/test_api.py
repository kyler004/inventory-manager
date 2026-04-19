import pytest
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from apps.tests.factories import (
    UserFactory, AdminUserFactory, ProductFactory,
    CategoryFactory, StockLevelFactory
)
from apps.users.models import Role


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client):
    """Returns an API client authenticated as a store manager."""
    user = UserFactory()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def admin_client(api_client):
    """Returns an API client authenticated as an admin."""
    user = AdminUserFactory()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.mark.django_db
class TestAuthEndpoints:

    def test_login_returns_tokens_and_user(self, api_client):
        """
        POST /auth/login/ should return access token,
        refresh token, and user info in one response.
        """
        user = UserFactory()
        user.set_password('testpassword123')
        user.save()

        response = api_client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'testpassword123'
        })

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data['data']
        assert 'refresh' in response.data['data']
        assert response.data['data']['user']['email'] == user.email

    def test_login_invalid_credentials(self, api_client):
        """Wrong password should return 401."""
        user = UserFactory()
        response = api_client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'wrongpassword'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_endpoint_returns_current_user(self, auth_client):
        """GET /auth/me/ should return the authenticated user."""
        client, user = auth_client
        response = client.get('/api/v1/auth/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['email'] == user.email

    def test_me_endpoint_requires_auth(self, api_client):
        """Unauthenticated request to /auth/me/ should return 401."""
        response = api_client.get('/api/v1/auth/me/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProductEndpoints:

    def test_list_products_authenticated(self, auth_client):
        """Any authenticated user can list products."""
        client, _ = auth_client
        ProductFactory.create_batch(5)

        response = client.get('/api/v1/products/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['meta']['total_count'] == 5

    def test_create_product_requires_manager(self, auth_client):
        """
        Store manager should NOT be able to create products.
        Only warehouse manager or above.
        Matches our permission matrix.
        """
        client, _ = auth_client  # Store manager by default
        category = CategoryFactory()

        response = client.post('/api/v1/products/', {
            'name': 'Test Product',
            'sku': 'TEST-001',
            'category': category.id,
            'unit_of_measure': 'piece',
            'unit_price_cost': '1.00',
            'unit_price_retail': '1.50',
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_product_as_admin(self, admin_client):
        """Admin should be able to create products."""
        client, _ = admin_client
        category = CategoryFactory()

        response = client.post('/api/v1/products/', {
            'name': 'Test Product',
            'sku': 'TEST-002',
            'category': category.id,
            'unit_of_measure': 'piece',
            'unit_price_cost': '1.00',
            'unit_price_retail': '1.50',
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Test Product'

    def test_delete_product_soft_deletes(self, admin_client):
        """
        DELETE should set is_active=False, not remove from DB.
        Product should still exist but be inactive.
        """
        client, _ = admin_client
        product = ProductFactory()

        response = client.delete(f'/api/v1/products/{product.id}/')

        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.is_active is False  # Still exists, just deactivated

    def test_retail_price_validation(self, admin_client):
        """
        Retail price below cost price should be rejected.
        Connects to our serializer validation.
        """
        client, _ = admin_client
        category = CategoryFactory()

        response = client.post('/api/v1/products/', {
            'name': 'Invalid Product',
            'sku': 'TEST-003',
            'category': category.id,
            'unit_of_measure': 'piece',
            'unit_price_cost': '5.00',
            'unit_price_retail': '3.00',  # Lower than cost — invalid
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestStockEndpoints:

    def test_low_stock_endpoint_filters_correctly(self, auth_client):
        """
        GET /stock/low/ should only return items
        at or below their reorder point.
        """
        client, user = auth_client

        # Below reorder point
        StockLevelFactory(
            location=user.location,
            quantity_on_hand=Decimal('10.00'),
            quantity_reserved=Decimal('0.00'),
            reorder_point=Decimal('20.00')
        )

        # Above reorder point — should NOT appear
        StockLevelFactory(
            location=user.location,
            quantity_on_hand=Decimal('100.00'),
            quantity_reserved=Decimal('0.00'),
            reorder_point=Decimal('20.00')
        )

        response = client.get('/api/v1/stock/low/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1