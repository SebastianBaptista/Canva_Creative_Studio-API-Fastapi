import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=35,
        pattern=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ]+$",
        description="Username must contain only letters (can include accents and ñ)",
        examples=["johndoe", "maria", "carlos"]
    )
    
    email: EmailStr = Field(
        ...,
        max_length=255,
        description="Valid email address",
        examples=["user@example.com", "test@domain.com"]
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must have at least 8 characters with uppercase, lowercase, numbers and symbols",
        examples=["SecurePass123!", "StrongP@ssword99"]
    )
    phone: str = Field(
        ...,
        min_length=10,
        max_length=20,
        description="Phone number must be valid",
        examples=["+58 412 345 6789", "0412 345 6789"]
    )
    
    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        errors = []
        if not re.search(r'[a-z]', v):
            errors.append('at least one lowercase letter')
        if not re.search(r'[A-Z]', v):
            errors.append('at least one uppercase letter')
        if not re.search(r'\d', v):
            errors.append('at least one number')
        if not re.search(r'[@$!%*?&]', v):
            errors.append('at least one symbol (@$!%*?&)')
        if errors:
            raise ValueError(f'Password must contain: {", ".join(errors)}')
        
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username_reserved(cls, v: str) -> str:
        reserved_usernames = {'admin', 'root', 'system', 'user', 'test'}
        if v.lower() in reserved_usernames:
            raise ValueError('This username is not available')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone_ve(cls, v):
        pattern = r'^(\+58|0058|58)?[-\s]?0?(4(1[2-9]|24|14|[2-9]\d)|2(12|[2-9]\d))[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}$'
        
        v_clean = re.sub(r'[-\s]', '', v)
        if not re.match(pattern, v_clean):
            raise ValueError('Invalid Venezuelan phone number format')
        
        match v_clean:
            case phone_number if phone_number.startswith('0058'):
                phone_number_normalized = '+58' + phone_number[4:]
            case phone_number if phone_number.startswith('58') and len(phone_number) == 11:
                phone_number_normalized = '+58' + phone_number[2:]
            case phone_number if phone_number.startswith('0') and len(phone_number) == 11:
                phone_number_normalized = '+58' + phone_number[1:]
            case phone_number if len(phone_number) == 10 and phone_number.startswith('4'):
                phone_number_normalized = '+58' + phone_number
            case phone_number if phone_number.startswith('+'):
                phone_number_normalized = phone_number
            case _:
                phone_number_normalized = '+58' + v_clean
                
        return phone_number_normalized

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone: str

    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    username: Optional[str] = Field(  
        None,  
        min_length=3,
        max_length=35,
        pattern=r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ]+$", 
        description="Username must contain only letters and spaces (can include accents and ñ)",
        examples=["johndoe", "maria garcia", "carlos pérez"]
    )
    
    email: Optional[EmailStr] = Field(  
        None,
        max_length=255,
        description="Valid email address (optional)",
        examples=["user@example.com", "test@domain.com"]
    )

    password: Optional[str] = Field( 
        None,
        min_length=8,
        max_length=128,
        description="Password must have at least 8 characters with uppercase, lowercase, numbers and symbols",
        examples=["SecurePass123!", "StrongP@ssword99"]
    )
    
    phone: Optional[str] = Field( 
        None,
        min_length=10,
        max_length=20,
        description="Phone number must be valid (optional)",
        examples=["+58 412 345 6789", "0412 345 6789"]
    )
    
    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: Optional[str]) -> Optional[str]:
        if v is None:  
            return None
        errors = []
        if not re.search(r'[a-z]', v):
            errors.append('at least one lowercase letter')
        if not re.search(r'[A-Z]', v):
            errors.append('at least one uppercase letter')
        if not re.search(r'\d', v):
            errors.append('at least one number')
        if not re.search(r'[@$!%*?&]', v):
            errors.append('at least one symbol (@$!%*?&)')
        if errors:
            raise ValueError(f'Password must contain: {", ".join(errors)}')
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username_reserved(cls, v: Optional[str]) -> Optional[str]:
        if v is None:  
            return None 
        reserved_usernames = {'admin', 'root', 'system', 'user', 'test'}
        if v.lower() in reserved_usernames:
            raise ValueError('This username is not available')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone_ve(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        pattern = r'^(\+58|0058|58)?[-\s]?0?(4(1[2-9]|24|14|[2-9]\d)|2(12|[2-9]\d))[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}$'
        v_clean = re.sub(r'[-\s]', '', v)
        if not re.match(pattern, v_clean):
            raise ValueError('Invalid Venezuelan phone number format')
        match v_clean:
            case phone_number if phone_number.startswith('0058'):
                phone_number_normalized = '+58' + phone_number[4:]
            case phone_number if phone_number.startswith('58') and len(phone_number) == 11:
                phone_number_normalized = '+58' + phone_number[2:]
            case phone_number if phone_number.startswith('0') and len(phone_number) == 11:
                phone_number_normalized = '+58' + phone_number[1:]
            case phone_number if len(phone_number) == 10 and phone_number.startswith('4'):
                phone_number_normalized = '+58' + phone_number
            case phone_number if phone_number.startswith('+'):
                phone_number_normalized = phone_number
            case _:
                phone_number_normalized = '+58' + v_clean
        return phone_number_normalized