import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.models.billing_plan import UserSubscription, BillingPlan
from main import app
from api.v1.services.user import user_service
from api.db.database import get_db
from datetime import datetime, timezone, timedelta
from uuid_extensions import uuid7
from api.v1.services.stripe_payment import update_user_plan, fetch_all_organisations_with_users_and_plans

client = TestClient(app)

# Mock Data
email = "test@gmail.com"
user_id = "user_123"
plan_id = "plan_123"
org_id = "org_123"
start_date = datetime.utcnow()
end_date = start_date + timedelta(days=30)

mock_user = User(id=user_id, email=email, first_name="Mike", last_name="Zeus", is_superadmin=True)
mock_plan = BillingPlan(id=plan_id, name="Premium", price=29.99, currency="USD", duration="monthly", organisation_id=org_id)
mock_subscription = UserSubscription(user_id=user_id, plan_id=plan_id, organisation_id=org_id, start_date=start_date, end_date=end_date)

@pytest.fixture
def mock_db_session():
    session = MagicMock(spec=Session)
    session.query().filter().first.side_effect = lambda: {
        User: mock_user,
        BillingPlan: mock_plan,
        UserSubscription: mock_subscription
    }[session.query.call_args[0][0]]
    return session

@pytest.fixture
def mock_subscribe_user_to_plan():
    with patch("api.v1.services.stripe_payment.update_user_plan") as mock_service:
        yield mock_service

@pytest.fixture
def mock_user_service():
    """Fixture to create a mock user service."""
    with patch("api.v1.services.user.user_service", autospec=True) as mock_service:
        yield mock_service

def create_mock_user(mock_user_service, mock_db_session):
    """Create a mock user in the mock database session."""
    mock_user = User(
        id=user_id,
        email="testuser@gmail.com",
        password=user_service.hash_password("Testpassword@123"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_superadmin=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    return mock_user

@pytest.fixture
def mock_fetch_all_organisations_with_users_and_plans():
    with patch("api.v1.services.stripe_payment.fetch_all_organisations_with_users_and_plans") as mock_service:
        yield mock_service

@pytest.mark.asyncio
async def test_subscribe_user_to_plan(mock_db_session, mock_subscribe_user_to_plan):
    # Mock the behavior of the service function
    mock_subscribe_user_to_plan.return_value = mock_subscription

    # Call the actual service function
    response = await update_user_plan(mock_db_session, user_id=user_id, plan_name="Premium")

    # Assertions
    assert response.user_id == user_id
    assert response.plan_id == plan_id
    assert response.organisation_id == org_id