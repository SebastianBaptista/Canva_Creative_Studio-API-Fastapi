import pytest
from fastapi import HTTPException, status
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from pydantic import ValidationError  # ← Importación añadida

from app.api.v1.endpoints.user_endpoint import create_new_user
from app.schemas.user import UserCreate
from app.models.users import User

# Mock data
mock_user = User(
    id=1,
    username="testuser",
    email="test@email.com",
    hashed_password="$2b$12$hashed_password_123",
    phone="+584123456789"
)

class TestCreateNewUser:
    
    def test_create_user_success(self):
        """Test creación exitosa de usuario"""
        mock_db = Mock(spec=Session)
        
        # Mock de create_user que retorna usuario creado
        with patch('app.api.v1.endpoints.user_endpoint.create_user', return_value=mock_user):
            response = create_new_user(
                user=UserCreate(
                    username="testuser",
                    email="test@email.com",
                    password="SecurePass123!",  # ✅ Password válida
                    phone="+584123456789"
                ),
                db=mock_db
            )
        
        assert response.id == 1
        assert response.username == "testuser"
        assert response.email == "test@email.com"
        assert response.phone == "+584123456789"

    def test_create_user_failure_returns_400(self):
        """Test que creación fallida retorna error 400"""
        mock_db = Mock(spec=Session)
        
        # Mock de create_user que retorna None (fallo)
        with patch('app.api.v1.endpoints.user_endpoint.create_user', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                create_new_user(
                    user=UserCreate(
                        username="testuser",
                        email="test@email.com",
                        password="SecurePass123!",
                        phone="+584123456789"
                    ),
                    db=mock_db
                )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "User could not be created" in exc_info.value.detail

    def test_create_user_with_invalid_data_raises_validation_error(self):
        """Test que datos inválidos lanzan ValidationError"""
        mock_db = Mock(spec=Session)
        
        # Intentar crear con password inválida (8+ caracteres pero sin mayúsculas/símbolos)
        with pytest.raises(ValidationError) as exc_info:  # ✅ Cambiado a ValidationError
            UserCreate(
                username="testuser",
                email="test@email.com",
                password="invalidpassword",  # ❌ 14 caracteres pero sin mayúsculas/símbolos
                phone="+584123456789"
            )
        
        # Ahora sí llegará a tu validador personalizado
        error_str = str(exc_info.value)
        assert "Password must contain" in error_str
        
    def test_create_user_with_reserved_username(self):
        """Test que username reservado lanza error"""
        mock_db = Mock(spec=Session)
        
        # Intentar crear con username reservado
        with pytest.raises(ValidationError) as exc_info:  # ✅ Cambiado a ValidationError
            UserCreate(
                username="admin",  # ❌ Username reservado
                email="test@email.com",
                password="SecurePass123!",
                phone="+584123456789"
            )
        
        assert "not available" in str(exc_info.value)

    def test_create_user_with_invalid_phone(self):
        """Test que teléfono inválido lanza error"""
        mock_db = Mock(spec=Session)

        # Teléfono con longitud suficiente pero formato venezolano inválido
        with pytest.raises(ValidationError) as exc_info:  # ✅ Cambiado a ValidationError
            UserCreate(
                username="testuser",
                email="test@email.com",
                password="SecurePass123!",
                phone="123456789012"  # ❌ 12 chars, formato no venezolano
            )

        error_str = str(exc_info.value)
        print(f"Error completo: {error_str}")  # Para debug
        
        # Verificar que es tu validador personalizado el que falla
        assert "Invalid Venezuelan phone number" in error_str

    def test_create_user_calls_create_user_with_correct_args(self):
        """Test que create_user es llamado con los argumentos correctos"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.create_user', return_value=mock_user) as mock_create:
            create_new_user(
                user=UserCreate(
                    username="testuser",
                    email="test@email.com",
                    password="SecurePass123!",
                    phone="+584123456789"
                ),
                db=mock_db
            )
        
        # Verificar que create_user fue llamado con los argumentos correctos
        mock_create.assert_called_once_with(
            mock_db,
            "testuser",
            "test@email.com",
            "SecurePass123!",
            "+584123456789"
        )

    def test_create_user_returns_correct_response_model(self):
        """Test que retorna el modelo de respuesta correcto"""
        mock_db = Mock(spec=Session)
        
        with patch('app.api.v1.endpoints.user_endpoint.create_user', return_value=mock_user):
            response = create_new_user(
                user=UserCreate(
                    username="testuser",
                    email="test@email.com",
                    password="SecurePass123!",
                    phone="+584123456789"
                ),
                db=mock_db
            )
        
        # Verificar que la respuesta tiene el formato correcto
        assert hasattr(response, 'id')
        assert hasattr(response, 'username')
        assert hasattr(response, 'email')
        assert hasattr(response, 'phone')
        assert not hasattr(response, 'password')  # No debe incluir password
        assert not hasattr(response, 'hashed_password')  # No debe incluir hash

    def test_create_user_status_code_201(self):
        """Test que verifica el código de status 201"""
        # Este test verificaría el decorador @status_code, pero requiere TestClient
        # Se puede hacer con TestClient en tests de integración
        pass