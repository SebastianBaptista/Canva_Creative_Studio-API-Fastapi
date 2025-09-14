import pytest
from fastapi import HTTPException, status
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.api.v1.endpoints.user_endpoint import patch_user
from app.schemas.user import UserUpdate
from app.models.users import User

# Mock data
mock_user = User(
    id=1,
    username="testuser",
    email="test@email.com", 
    hashed_password="hashed_old_password",
    phone="+584123456789"
)
def test_patch_user_empty_json():
    """Test que JSON vacío retorna error 400"""
    with pytest.raises(HTTPException) as exc_info:
        patch_user(
            user_id=1,
            user_changes=UserUpdate(),  # Todos los campos None
            db=Mock()
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "No fields provided" in exc_info.value.detail
    
def test_patch_user_not_found():
    """Test que usuario no existente retorna 404"""
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        patch_user(
            user_id=999,
            user_changes=UserUpdate(username="newusername"),
            db=mock_db
        )
    
    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail

def test_patch_user_email_exists():
    """Test que email existente en otro usuario retorna error"""
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Mock para que check_email_exists retorne True
    with patch('app.api.v1.endpoints.user_endpoint.check_email_exists', return_value=True):
        with pytest.raises(HTTPException) as exc_info:
            patch_user(
                user_id=1,
                user_changes=UserUpdate(email="existing@email.com"),
                db=mock_db
            )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in exc_info.value.detail

def test_patch_user_success_username():
    """Test actualización exitosa de username"""
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Mock de update_user
    updated_user = User(
        id=1,
        username="newusername",
        email="test@email.com",
        hashed_password="hashed_old_password", 
        phone="+584123456789"
    )
    
    with patch('app.api.v1.endpoints.user_endpoint.update_user', return_value=updated_user):
        with patch('app.api.v1.endpoints.user_endpoint.check_email_exists', return_value=False):
            response = patch_user(
                user_id=1,
                user_changes=UserUpdate(username="newusername"),
                db=mock_db
            )
    
    assert response.username == "newusername"
    assert response.email == "test@email.com"  # No cambió

def test_patch_user_success_email():
    """Test actualización exitosa de email"""
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    updated_user = User(
        id=1,
        username="testuser",
        email="new@email.com",
        hashed_password="hashed_old_password",
        phone="+584123456789"
    )
    
    with patch('app.api.v1.endpoints.user_endpoint.update_user', return_value=updated_user):
        with patch('app.api.v1.endpoints.user_endpoint.check_email_exists', return_value=False):
            response = patch_user(
                user_id=1,
                user_changes=UserUpdate(email="new@email.com"),
                db=mock_db
            )
    
    assert response.email == "new@email.com"
    assert response.username == "testuser"  # No cambió
def test_patch_user_success_multiple_fields():
    """Test actualización exitosa de múltiples campos"""
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    updated_user = User(
        id=1,
        username="newusername",
        email="new@email.com",
        hashed_password="hashed_new_password",
        phone="+584123456780"
    )
    
    with patch('app.api.v1.endpoints.user_endpoint.update_user', return_value=updated_user):
        with patch('app.api.v1.endpoints.user_endpoint.check_email_exists', return_value=False):
            response = patch_user(
                user_id=1,
                user_changes=UserUpdate(
                    username="newusername",
                    email="new@email.com",
                    password="newpassWord123!",
                    phone="+584123456780"
                ),
                db=mock_db
            )
    
    assert response.username == "newusername"
    assert response.email == "new@email.com"
    assert response.phone == "+584123456780"

def test_patch_user_same_email_no_validation():
    """Test que no valida email si es el mismo que el actual"""
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    updated_user = User(
        id=1,
        username="testuser",
        email="test@email.com",  # Mismo email
        hashed_password="hashed_old_password",
        phone="+584123456789"
    )
    
    # check_email_exists NO debería llamarse si el email es el mismo
    with patch('app.api.v1.endpoints.user_endpoint.update_user', return_value=updated_user):
        with patch('app.api.v1.endpoints.user_endpoint.check_email_exists') as mock_check:
            response = patch_user(
                user_id=1,
                user_changes=UserUpdate(email="test@email.com"),  # Mismo email
                db=mock_db
            )
    
    # Verificar que NO se llamó a check_email_exists
    mock_check.assert_not_called()
    assert response.email == "test@email.com"

def test_patch_user_update_error():
    """Test que error en update_user propaga la excepción"""
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    with patch('app.api.v1.endpoints.user_endpoint.update_user', return_value=None):
        with patch('app.api.v1.endpoints.user_endpoint.check_email_exists', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                patch_user(
                    user_id=1,
                    user_changes=UserUpdate(username="newusername"),
                    db=mock_db
                )
    
    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail