# tests/test_user_endpoint.py
import pytest
from fastapi import HTTPException, status
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.api.v1.endpoints.user_endpoint import delete_user
from app.models.users import User

# Mock data
mock_user = User(
    id=1,
    username="user1",
    email="user1@email.com",
    hashed_password="$2b$12$hashed_password_123",
    phone="+584123456789"
)

class TestDeleteUserEndpoint:
    
    def test_delete_user_success(self):
        """Test que elimina un usuario exitosamente"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.delete_user_by_id', return_value=mock_user):
            # El endpoint debería retornar None (status 204) en caso de éxito
            response = delete_user(user_id=1, db=mock_db)
            
        # Verificar que la respuesta es None (status 204 No Content)
        assert response is None

    def test_delete_user_not_found(self):
        """Test que usuario no encontrado retorna 404"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.delete_user_by_id', return_value=None):
            
            with pytest.raises(HTTPException) as exc_info:
                delete_user(user_id=999, db=mock_db)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "User to delete not found"

    def test_delete_user_calls_delete_user_by_id(self):
        """Test que delete_user_by_id es llamado correctamente"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.delete_user_by_id', return_value=mock_user) as mock_delete:
            
            delete_user(user_id=1, db=mock_db)
        
        # Verificar que delete_user_by_id fue llamado con los parámetros correctos
        mock_delete.assert_called_once_with(mock_db, 1)

    def test_delete_user_database_error(self):
        """Test que maneja errores de base de datos"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.delete_user_by_id', 
                  side_effect=Exception("Database connection error")):
            
            # El endpoint debería propagar la excepción
            with pytest.raises(Exception) as exc_info:
                delete_user(user_id=1, db=mock_db)
            
            assert "Database connection error" in str(exc_info.value)

    def test_delete_user_with_different_ids(self):
        """Test que funciona con diferentes IDs de usuario"""
        mock_db = Mock(spec=Session)
        
        # Test con ID 1
        with patch('app.api.v1.endpoints.user_endpoint.delete_user_by_id', return_value=mock_user):
            response = delete_user(user_id=1, db=mock_db)
            assert response is None
        
        # Test con ID 100
        mock_user_100 = User(id=100, username="user100", email="user100@email.com", 
                           hashed_password="hashed_100", phone="+584100000000")
        
        with patch('app.api.v1.endpoints.user_endpoint.delete_user_by_id', return_value=mock_user_100):
            response = delete_user(user_id=100, db=mock_db)
            assert response is None

    def test_delete_user_verify_db_operations(self):
        """Test que verifica las operaciones de base de datos"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.delete_user_by_id', return_value=mock_user) as mock_delete:
            
            delete_user(user_id=1, db=mock_db)
            
            # Verificar que la función de eliminación fue llamada
            mock_delete.assert_called_once()
            
            # Verificar que se pasó la sesión de base de datos correcta
            args, _ = mock_delete.call_args
            assert args[0] == mock_db
            assert args[1] == 1

    def test_delete_user_edge_cases(self):
        """Test para casos extremos de IDs"""
        mock_db = Mock(spec=Session)
        
        # Test con el ID mínimo válido (1)
        with patch('app.api.v1.endpoints.user_endpoint.delete_user_by_id', return_value=mock_user):
            response = delete_user(user_id=1, db=mock_db)
            assert response is None
        
        # Test con un ID grande
        large_id_user = User(id=999999, username="large_user", email="large@email.com", 
                           hashed_password="hashed_large", phone="+584999999999")
        
        with patch('app.api.v1.endpoints.user_endpoint.delete_user_by_id', return_value=large_id_user):
            response = delete_user(user_id=999999, db=mock_db)
            assert response is None

    def test_delete_user_multiple_calls(self):
        """Test que verifica múltiples llamadas al endpoint"""
        mock_db = Mock(spec=Session)
        
        # Primera llamada - usuario existe
        with patch('app.api.v1.endpoints.user_endpoint.delete_user_by_id', return_value=mock_user):
            response1 = delete_user(user_id=1, db=mock_db)
            assert response1 is None
        
        # Segunda llamada - usuario no existe (después de ser eliminado)
        with patch('app.api.v1.endpoints.user_endpoint.delete_user_by_id', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                delete_user(user_id=1, db=mock_db)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_error_messages(self):
        """Test que verifica los mensajes de error"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.delete_user_by_id', return_value=None):
            
            with pytest.raises(HTTPException) as exc_info:
                delete_user(user_id=999, db=mock_db)
            
            # Verificar el mensaje de error exacto
            assert exc_info.value.detail == "User to delete not found"
            assert "not found" in exc_info.value.detail.lower()

    def test_delete_user_response_type(self):
        """Test que verifica el tipo de respuesta"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.delete_user_by_id', return_value=mock_user):
            
            response = delete_user(user_id=1, db=mock_db)
            
            # El endpoint debería retornar None para status 204 No Content
            assert response is None
            assert isinstance(response, type(None))