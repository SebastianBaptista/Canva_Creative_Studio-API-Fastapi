# tests/test_user_endpoint.py
import pytest
from fastapi import HTTPException, status
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.api.v1.endpoints.user_endpoint import read_users
from app.schemas.user import UserRead
from app.models.users import User

# Mock data
mock_users = [
    User(
        id=1,
        username="user1",
        email="user1@email.com",
        hashed_password="$2b$12$hashed_password_123",
        phone="+584123456789"
    ),
    User(
        id=2, 
        username="user2",
        email="user2@email.com",
        hashed_password="$2b$12$hashed_password_456",
        phone="+584987654321"
    )
]

mock_users_read = [
    UserRead(
        id=1,
        username="user1",
        email="user1@email.com",
        phone="+584123456789"
    ),
    UserRead(
        id=2,
        username="user2", 
        email="user2@email.com",
        phone="+584987654321"
    )
]

class TestReadUsersEndpoint:
    
    def test_read_users_success(self):
        """Test que obtiene todos los usuarios exitosamente"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_all_users', return_value=mock_users):
            with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate', side_effect=mock_users_read):
                
                response = read_users(db=mock_db)
        
        # Verificar que la respuesta es una lista de UserRead
        assert isinstance(response, list)
        assert len(response) == 2
        assert all(isinstance(user, UserRead) for user in response)
        
        # Verificar datos del primer usuario
        assert response[0].id == 1
        assert response[0].username == "user1"
        assert response[0].email == "user1@email.com"
        assert response[0].phone == "+584123456789"
        
        # Verificar datos del segundo usuario
        assert response[1].id == 2
        assert response[1].username == "user2"
        assert response[1].email == "user2@email.com"
        assert response[1].phone == "+584987654321"

    def test_read_users_empty(self):
        """Test que lista vacía de usuarios retorna 404"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_all_users', return_value=[]):
            
            with pytest.raises(HTTPException) as exc_info:
                read_users(db=mock_db)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Users not found" in exc_info.value.detail

    def test_read_users_none(self):
        """Test que None retorna 404"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_all_users', return_value=None):
            
            with pytest.raises(HTTPException) as exc_info:
                read_users(db=mock_db)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Users not found" in exc_info.value.detail

    def test_read_users_conversion_error(self):
        """Test que error en conversión muestra el comportamiento actual"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_all_users', return_value=mock_users):
            with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate', 
                    side_effect=Exception("Conversion error")):
                
                # El endpoint actual probablemente lanzará la excepción directamente
                with pytest.raises(Exception) as exc_info:  # ✅ Capturar Exception genérica
                    read_users(db=mock_db)
                
                assert "Conversion error" in str(exc_info.value)

    def test_read_users_excludes_sensitive_fields(self):
        """Test que excluye campos sensibles en la respuesta"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_all_users', return_value=mock_users):
            with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate', side_effect=mock_users_read):
                
                response = read_users(db=mock_db)
        
        # Verificar que NINGÚN usuario tiene campos sensibles
        for user in response:
            assert not hasattr(user, 'password')
            assert not hasattr(user, 'hashed_password')
            assert not hasattr(user, 'created_at')
            
            # Verificar que SÍ tiene campos públicos
            assert hasattr(user, 'id')
            assert hasattr(user, 'username')
            assert hasattr(user, 'email')
            assert hasattr(user, 'phone')

    def test_read_users_calls_get_all_users(self):
        """Test que get_all_users es llamado correctamente"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_all_users', return_value=mock_users) as mock_get:
            with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate', side_effect=mock_users_read):
                
                read_users(db=mock_db)
        
        # Verificar que get_all_users fue llamado
        mock_get.assert_called_once_with(mock_db)

    def test_read_users_response_structure(self):
        """Test que la respuesta tiene la estructura correcta"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_all_users', return_value=mock_users):
            with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate', side_effect=mock_users_read):
                
                response = read_users(db=mock_db)
        
        # Verificar estructura del response
        assert isinstance(response, list)
        assert len(response) == 2
        
        for user in response:
            user_dict = user.model_dump()
            assert set(user_dict.keys()) == {'id', 'username', 'email', 'phone'}

    def test_read_users_serialization(self):
        """Test que la respuesta se puede serializar correctamente"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.get_all_users', return_value=mock_users):
            with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate', side_effect=mock_users_read):
                
                response = read_users(db=mock_db)
        
        # Serializar a JSON
        json_response = [user.model_dump_json() for user in response]
        
        # Verificar que contiene los campos correctos
        assert '"id":1' in json_response[0]
        assert '"username":"user1"' in json_response[0]
        assert '"email":"user1@email.com"' in json_response[0]
        
        assert '"id":2' in json_response[1]
        assert '"username":"user2"' in json_response[1]
        assert '"email":"user2@email.com"' in json_response[1]
        
        # Verificar que NO contiene campos sensibles
        assert all('password' not in json for json in json_response)
        assert all('hashed_password' not in json for json in json_response)

    def test_read_users_single_user(self):
        """Test que funciona con un solo usuario"""
        mock_db = Mock(spec=Session)
        
        single_user = [mock_users[0]]  # Lista con un solo usuario
        single_user_read = [mock_users_read[0]]
        
        with patch('app.api.v1.endpoints.user_endpoint.get_all_users', return_value=single_user):
            with patch('app.api.v1.endpoints.user_endpoint.UserRead.model_validate', side_effect=single_user_read):
                
                response = read_users(db=mock_db)
        
        assert isinstance(response, list)
        assert len(response) == 1
        assert response[0].id == 1
        assert response[0].username == "user1"