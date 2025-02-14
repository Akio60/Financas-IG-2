
import jwt
import datetime
import hashlib
from functools import wraps
import time
from typing import Dict, Optional
import logging
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta

# Configurações
SECRET_KEY = "seu_secret_key_seguro_aqui"  # Em produção, usar variável de ambiente
TOKEN_EXPIRATION = 30  # minutos
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 15  # minutos
RATE_LIMIT_WINDOW = 60  # segundos
RATE_LIMIT_MAX_REQUESTS = 30

@dataclass
class LoginAttempt:
    ip: str
    timestamp: datetime
    success: bool
    username: str

class AuthManager:
    def __init__(self):
        self.login_attempts: Dict[str, list] = {}
        self.rate_limit_counters: Dict[str, list] = {}
        self.setup_database()

    def setup_database(self):
        """Inicializa o banco de dados SQLite para auditoria"""
        db_path = "security/audit.db"
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS login_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    ip_address TEXT,
                    username TEXT,
                    success BOOLEAN,
                    user_agent TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    event_type TEXT,
                    username TEXT,
                    ip_address TEXT,
                    details TEXT
                )
            """)

    def check_rate_limit(self, ip: str) -> bool:
        """Implementa rate limiting baseado em janela deslizante"""
        current_time = datetime.now()
        if ip not in self.rate_limit_counters:
            self.rate_limit_counters[ip] = []

        # Remove timestamps antigos
        self.rate_limit_counters[ip] = [
            ts for ts in self.rate_limit_counters[ip]
            if (current_time - ts) < timedelta(seconds=RATE_LIMIT_WINDOW)
        ]

        if len(self.rate_limit_counters[ip]) >= RATE_LIMIT_MAX_REQUESTS:
            return False

        self.rate_limit_counters[ip].append(current_time)
        return True

    def record_login_attempt(self, attempt: LoginAttempt, user_agent: str):
        """Registra tentativa de login no banco de dados"""
        with sqlite3.connect("security/audit.db") as conn:
            conn.execute(
                """
                INSERT INTO login_attempts 
                (timestamp, ip_address, username, success, user_agent)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    attempt.timestamp.isoformat(),
                    attempt.ip,
                    attempt.username,
                    attempt.success,
                    user_agent
                )
            )

    def is_account_locked(self, username: str, ip: str) -> bool:
        """Verifica se a conta está bloqueada por muitas tentativas"""
        recent_attempts = [
            attempt for attempt in self.login_attempts.get(username, [])
            if not attempt.success and 
            (datetime.now() - attempt.timestamp).total_seconds() < LOCKOUT_TIME * 60
        ]
        return len(recent_attempts) >= MAX_LOGIN_ATTEMPTS

    def generate_token(self, user_data: dict) -> str:
        """Gera um token JWT"""
        expiration = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION)
        payload = {
            **user_data,
            'exp': expiration
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    def validate_token(self, token: str) -> Optional[dict]:
        """Valida um token JWT"""
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def log_security_event(self, event_type: str, username: str, ip: str, details: str):
        """Registra eventos de segurança no banco de dados"""
        with sqlite3.connect("security/audit.db") as conn:
            conn.execute(
                """
                INSERT INTO security_events 
                (timestamp, event_type, username, ip_address, details)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(),
                    event_type,
                    username,
                    ip,
                    details
                )
            )

def require_auth(f):
    """Decorador para requerer autenticação em rotas"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = kwargs.get('token')
        if not token:
            return {'message': 'Token ausente'}, 401

        auth_manager = AuthManager()
        user_data = auth_manager.validate_token(token)
        if not user_data:
            return {'message': 'Token inválido'}, 401

        return f(*args, **kwargs, user_data=user_data)
    return decorated
