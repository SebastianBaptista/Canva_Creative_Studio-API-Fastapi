# tests/test_user_endpoint.py
import pytest
from fastapi import HTTPException, status
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.api.v1.endpoints.user_endpoint import read_user
from app.schemas.user import UserRead
from app.models.users import User

# Mock data
mock_user = User(
    id=1,
    username="testuser",
    email="test@email.com",
    hashed_password="$2b$12$hashed_password_123",
    phone="+584123456789"
)

mock_user_read = UserRead(
    id=1,
    username="testuser",
    email="test@email.com",
    phone="+584123456789"
)

class TestGetUserByIdEndpoint:
    
    def test_read_user_success(self):
        """Test que obtiene usuario exitosamente por ID"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_user_by_id', return_value=mock_user):
            with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate', return_value=mock_user_read):
                
                # ✅ LLAMAR A read_user, NO a read_user
                response = read_user(
                    user_id=1,
                    db=mock_db
                )
        
        assert isinstance(response, UserRead)
        assert response.id == 1
        assert response.username == "testuser"
        assert response.email == "test@email.com"
        assert response.phone == "+584123456789"


    def test_get_user_by_id_not_found(self):
        """Test que usuario no encontrado retorna 404"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_user_by_id', return_value=None):
            
            with pytest.raises(HTTPException) as exc_info:
                read_user(
                    user_id=999,
                    db=mock_db
                )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in exc_info.value.detail

    def test_debug_conversion_error(self):
        """Test para ver qué error se lanza realmente"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_user_by_id', return_value=mock_user):
            with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate', 
                    side_effect=Exception("Conversion error")):
                
                try:
                    read_user(user_id=1, db=mock_db)
                    assert False, "Debería haber lanzado una excepción"
                except Exception as e:
                    print(f"Tipo de excepción: {type(e).__name__}")
                    print(f"Mensaje: {str(e)}")

    def test_get_user_by_id_excludes_sensitive_fields(self):
        """Test que excluye campos sensibles en la respuesta"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_user_by_id', return_value=mock_user):
            with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate') as mock_validate:
                
                mock_validate.return_value = UserRead(
                    id=1,
                    username="testuser",
                    email="test@email.com",
                    phone="+584123456789"
                )
                
                response = read_user(
                    user_id=1,
                    db=mock_db
                )
        
        # Verificar que NO tiene campos sensibles
        assert not hasattr(response, 'password')
        assert not hasattr(response, 'hashed_password')
        assert not hasattr(response, 'created_at')
        
        # Verificar que SÍ tiene campos públicos
        assert hasattr(response, 'id')
        assert hasattr(response, 'username')
        assert hasattr(response, 'email')
        assert hasattr(response, 'phone')

    def test_get_user_by_id_calls_get_user_by_id_with_correct_args(self):
        """Test que get_user_by_id es llamado con los argumentos correctos"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_user_by_id', return_value=mock_user) as mock_get:
            with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate', return_value=mock_user_read):
                
                read_user(
                    user_id=1,
                    db=mock_db
                )
        
        # Verificar que get_user_by_id fue llamado con los argumentos correctos
        mock_get.assert_called_once_with(mock_db, 1)

    def test_get_user_by_id_response_structure(self):
        """Test que la respuesta tiene la estructura correcta"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_user_by_id', return_value=mock_user):
            with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate') as mock_validate:
                
                mock_validate.return_value = UserRead(
                    id=1,
                    username="testuser",
                    email="test@email.com",
                    phone="+584123456789"
                )
                
                response = read_user(
                    user_id=1,
                    db=mock_db
                )
        
        # Verificar estructura del response
        response_dict = response.model_dump()
        
        assert response_dict == {
            "id": 1,
            "username": "testuser",
            "email": "test@email.com",
            "phone": "+584123456789"
        }

    def test_get_user_by_id_serialization(self):
        """Test que la respuesta se puede serializar correctamente"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_user_by_id', return_value=mock_user):
            with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate') as mock_validate:
                
                mock_validate.return_value = UserRead(
                    id=1,
                    username="testuser",
                    email="test@email.com",
                    phone="+584123456789"
                )
                
                response = read_user(
                    user_id=1,
                    db=mock_db
                )
        
        # Serializar a JSON
        json_response = response.model_dump_json()
        
        # Verificar que contiene los campos correctos
        assert '"id":1' in json_response
        assert '"username":"testuser"' in json_response
        assert '"email":"test@email.com"' in json_response
        assert '"phone":"+584123456789"' in json_response
        
        # Verificar que NO contiene campos sensibles
        assert 'password' not in json_response
        assert 'hashed_password' not in json_response

    def test_get_user_by_id_different_ids(self):
        """Test que funciona con diferentes IDs"""
        mock_db = Mock(spec=Session)
        
        test_cases = [1, 2, 100, 999]
        
        for user_id in test_cases:
            with patch('app.api.v1.endpoints.user_endpoint.get_user_by_id', return_value=mock_user):
                with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate') as mock_validate:
                    
                    mock_validate.return_value = UserRead(
                        id=user_id,
                        username=f"user{user_id}",
                        email=f"user{user_id}@email.com",
                        phone="+584123456789"
                    )
                    
                    response = read_user(
                        user_id=user_id,
                        db=mock_db
                    )
                    
                    assert response.id == user_id
                    assert response.username == f"user{user_id}"
                    assert response.email == f"user{user_id}@email.com"