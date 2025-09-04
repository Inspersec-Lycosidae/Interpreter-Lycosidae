"""
Sistema de logging personalizado para o Dashboard
"""
import json
import logging
import re
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Union

class BracketLevelFormatter(logging.Formatter):
    """
    Formatter que exibe: "YYYY-MM-DD HH:MM:SS | [LEVEL] Mensagem"
    com cores para INFO, WARNING, ERROR e CRITICAL.
    Suporte para formatação JSON melhorada.
    """

    COLOR_RESET = "\033[0m"
    COLORS = {
        logging.DEBUG: "\033[35m",     # Magenta
        logging.INFO: "\033[36m",      # Ciano
        logging.WARNING: "\033[33m",   # Amarelo
        logging.ERROR: "\033[31m",     # Vermelho
        logging.CRITICAL: "\033[1;31m"  # Vermelho brilhante
    }
    
    # Cores específicas para JSON
    JSON_COLORS = {
        "key": "\033[34m",        # Azul para chaves
        "string": "\033[32m",     # Verde para strings
        "number": "\033[33m",     # Amarelo para números
        "boolean": "\033[35m",    # Magenta para booleanos
        "null": "\033[90m",       # Cinza para null
        "bracket": "\033[37m",    # Branco para colchetes/chaves
    }
    
    # Cor para links (verde)
    LINK_COLOR = "\033[32m"

    def __init__(self, fmt=None, datefmt=None, use_color=True, pretty_json=True):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.use_color = use_color
        self.pretty_json = pretty_json

    def format(self, record: logging.LogRecord) -> str:
        level_tag = f"[{record.levelname}]"
        if self.use_color:
            color = self.COLORS.get(record.levelno)
            if color:
                level_tag = f"{color}{level_tag}{self.COLOR_RESET}"
        
        # Processar mensagem para colorir links e JSON
        if self.use_color:
            record.msg = self._colorize_links(str(record.msg))
            record.msg = self._colorize_json(record.msg)
        
        # Injeta campo customizado para uso no fmt
        setattr(record, "levelname_br", level_tag)
        return super().format(record)
    
    def _colorize_links(self, message: str) -> str:
        """Coloriza links (http/https) na mensagem"""
        # Regex para encontrar URLs
        url_pattern = r'https?://[^\s]+'
        
        def replace_url(match):
            url = match.group(0)
            return f"{self.LINK_COLOR}{url}{self.COLOR_RESET}"
        
        # Substituir URLs encontradas
        colored_message = re.sub(url_pattern, replace_url, message)
        return colored_message
    
    def _colorize_json(self, message: str) -> str:
        """Coloriza JSON na mensagem com cores específicas"""
        if not self.use_color:
            return message
            
        try:
            # Tenta detectar se a mensagem contém JSON
            if not any(char in message for char in ['{', '}', '[', ']']):
                return message
            
            # Verifica se a mensagem inteira é JSON válido
            if message.strip().startswith('{') and message.strip().endswith('}'):
                try:
                    json_data = json.loads(message.strip())
                    if self.pretty_json:
                        formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
                    else:
                        formatted_json = json.dumps(json_data, ensure_ascii=False)
                    return self._apply_json_colors(formatted_json)
                except json.JSONDecodeError:
                    return message
            
            # Verifica se há JSON no final da mensagem (após quebra de linha)
            lines = message.split('\n')
            if len(lines) > 1 and lines[-1].strip().startswith('{'):
                try:
                    json_data = json.loads(lines[-1].strip())
                    if self.pretty_json:
                        formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
                    else:
                        formatted_json = json.dumps(json_data, ensure_ascii=False)
                    lines[-1] = self._apply_json_colors(formatted_json)
                    return '\n'.join(lines)
                except json.JSONDecodeError:
                    pass
            
            # Se não for JSON válido, retorna a mensagem original
            return message
            
        except Exception:
            # Se houver qualquer erro, retorna a mensagem original
            return message
    
    def _apply_json_colors(self, json_str: str) -> str:
        """Aplica cores específicas a elementos JSON"""
        if not self.use_color:
            return json_str
        
        try:
            # Primeiro, colorir colchetes e chaves
            json_str = re.sub(
                r'([\{\}\[\]])',
                rf'{self.JSON_COLORS["bracket"]}\1{self.COLOR_RESET}',
                json_str
            )
            
            # Colorir chaves (strings antes de :)
            json_str = re.sub(
                r'"([^"]+)"\s*:',
                rf'{self.JSON_COLORS["key"]}"\1"{self.COLOR_RESET}:',
                json_str
            )
            
            # Colorir strings (valores entre aspas) - mais específico
            json_str = re.sub(
                r':\s*"([^"]*)"',
                rf': {self.JSON_COLORS["string"]}"\1"{self.COLOR_RESET}',
                json_str
            )
            
            # Colorir números (mais específico para evitar conflitos)
            json_str = re.sub(
                r':\s*(\d+\.?\d*)(?=\s*[,}\]]|$)',
                rf': {self.JSON_COLORS["number"]}\1{self.COLOR_RESET}',
                json_str
            )
            
            # Colorir booleanos
            json_str = re.sub(
                r':\s*(true|false)(?=\s*[,}\]]|$)',
                rf': {self.JSON_COLORS["boolean"]}\1{self.COLOR_RESET}',
                json_str
            )
            
            # Colorir null
            json_str = re.sub(
                r':\s*(null)(?=\s*[,}\]]|$)',
                rf': {self.JSON_COLORS["null"]}\1{self.COLOR_RESET}',
                json_str
            )
            
        except Exception:
            # Se houver erro, retorna o JSON sem cores
            return json_str
        
        return json_str

def setup_logging(level: int = logging.INFO, use_color: bool = True, pretty_json: bool = True) -> logging.Logger:
    """Configura logging global com formatter padronizado e cores."""
    root = logging.getLogger()

    # Evita handlers duplicados em hot-reload
    if root.handlers:
        for h in list(root.handlers):
            root.removeHandler(h)

    # Configura primeiro os loggers de terceiros para evitar conflitos
    _configure_third_party_loggers()

    handler = logging.StreamHandler()
    formatter = BracketLevelFormatter(
        fmt="%(levelname_br)s | %(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        use_color=use_color,
        pretty_json=pretty_json,
    )
    handler.setFormatter(formatter)
    handler.setLevel(level)

    root.setLevel(level)
    root.addHandler(handler)

    # Configuração específica para uvicorn
    _setup_uvicorn_logging(use_color)
    
    # Configuração específica para SQLAlchemy
    _setup_sqlalchemy_logging(use_color, pretty_json)

    return root

def _setup_sqlalchemy_logging(use_color: bool = True, pretty_json: bool = True):
    """Configura logging específico para SQLAlchemy com nosso formatter."""
    sqlalchemy_loggers = [
        'sqlalchemy.engine',
        'sqlalchemy.pool',
        'sqlalchemy.dialects',
        'sqlalchemy.orm',
        'sqlalchemy'
    ]
    
    for logger_name in sqlalchemy_loggers:
        logger = logging.getLogger(logger_name)
        
        # Remove handlers existentes para evitar duplicação
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
        
        # Apenas habilita propagação para o root logger (que já tem nosso formatter)
        logger.propagate = True
        logger.setLevel(logging.INFO)

def _setup_uvicorn_logging(use_color: bool = True):
    """Configura logging específico para uvicorn com compatibilidade."""
    # Configura uvicorn para usar nosso formatter
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    
    # Remove handlers padrão do uvicorn
    for logger in [uvicorn_logger, uvicorn_access_logger]:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
    
    # Apenas habilita propagação para o root logger (que já tem nosso formatter)
    uvicorn_logger.propagate = True
    uvicorn_access_logger.propagate = True
    
    # Configura níveis específicos
    uvicorn_logger.setLevel(logging.INFO)
    uvicorn_access_logger.setLevel(logging.INFO)

def _configure_third_party_loggers():
    """Configura níveis de log para bibliotecas de terceiros."""
    third_party_loggers = {
        'apscheduler': logging.WARNING,
        'apscheduler.executors.default': logging.WARNING,
        'httpx': logging.WARNING,
        'httpcore': logging.WARNING,
        'urllib3': logging.WARNING,
        'pymongo': logging.WARNING,
    }
    
    for logger_name, level in third_party_loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        # Remove handlers existentes para evitar duplicação
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
        # Habilita propagação para usar nosso formatter
        logger.propagate = True

def get_logger(name: str) -> logging.Logger:
    """Retorna um logger configurado para o módulo especificado."""
    return logging.getLogger(name)

class StructuredLogger:
    """Logger estruturado para diferentes contextos de aplicação."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context = {}
    
    def set_context(self, **kwargs):
        """Define contexto adicional para os logs."""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Limpa o contexto atual."""
        self.context.clear()
    
    def _format_message(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> str:
        """Formata mensagem com contexto e dados extras."""
        if not self.context and not extra_data:
            return message
        
        # Combina contexto e dados extras
        all_data = {**self.context}
        if extra_data:
            all_data.update(extra_data)
        
        # Formata como JSON se houver dados
        if all_data:
            # Para dados simples, usa formatação compacta
            if len(all_data) <= 3 and all(isinstance(v, (str, int, float, bool)) for v in all_data.values()):
                json_data = json.dumps(all_data, ensure_ascii=False)
                return f"{message} {json_data}"
            else:
                json_data = json.dumps(all_data, indent=2, ensure_ascii=False)
                return f"{message}\n{json_data}"
        
        return message
    
    def debug(self, message: str, **kwargs):
        """Log de debug com contexto."""
        formatted_msg = self._format_message(message, kwargs)
        self.logger.debug(formatted_msg)
    
    def info(self, message: str, **kwargs):
        """Log de info com contexto."""
        formatted_msg = self._format_message(message, kwargs)
        self.logger.info(formatted_msg)
    
    def warning(self, message: str, **kwargs):
        """Log de warning com contexto."""
        formatted_msg = self._format_message(message, kwargs)
        self.logger.warning(formatted_msg)
    
    def error(self, message: str, **kwargs):
        """Log de error com contexto."""
        formatted_msg = self._format_message(message, kwargs)
        self.logger.error(formatted_msg)
    
    def critical(self, message: str, **kwargs):
        """Log crítico com contexto."""
        formatted_msg = self._format_message(message, kwargs)
        self.logger.critical(formatted_msg)
    
    def log_json(self, message: str, data: Union[Dict, list], level: int = logging.INFO):
        """Log específico para dados JSON."""
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        formatted_msg = f"{message}\n{json_str}"
        self.logger.log(level, formatted_msg)
    
    def log_request(self, method: str, url: str, status_code: int, response_time: float, **kwargs):
        """Log específico para requisições HTTP."""
        self.info(
            f"HTTP {method} {url} - {status_code}",
            method=method,
            url=url,
            status_code=status_code,
            response_time_ms=round(response_time * 1000, 2),
            **kwargs
        )
    
    def log_database(self, operation: str, table: str, duration: float, **kwargs):
        """Log específico para operações de banco de dados."""
        self.info(
            f"DB {operation} on {table}",
            operation=operation,
            table=table,
            duration_ms=round(duration * 1000, 2),
            **kwargs
        )
    
    def log_api_response(self, endpoint: str, status_code: int, data: Any, **kwargs):
        """Log específico para respostas de API."""
        self.info(
            f"API Response: {endpoint} - {status_code}",
            endpoint=endpoint,
            status_code=status_code,
            **kwargs
        )
        self.log_json("Response data:", data, logging.DEBUG)

def get_structured_logger(name: str) -> StructuredLogger:
    """Retorna um logger estruturado para o módulo especificado."""
    return StructuredLogger(name)

def log_json_response(logger: logging.Logger, message: str, data: Any, level: int = logging.INFO):
    """Função utilitária para log de respostas JSON."""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    formatted_msg = f"{message}\n{json_str}"
    logger.log(level, formatted_msg)

def log_http_request(logger: logging.Logger, method: str, url: str, status_code: int, 
                    response_time: float = None, **extra_data):
    """Função utilitária para log de requisições HTTP."""
    msg = f"HTTP {method} {url} - {status_code}"
    if response_time:
        msg += f" ({response_time:.3f}s)"
    
    logger.info(msg, extra={
        'method': method,
        'url': url,
        'status_code': status_code,
        'response_time': response_time,
        **extra_data
    })

def configure_production_logging():
    """Configura logging otimizado para produção."""
    # Desabilita cores em produção (assumindo que não há terminal colorido)
    setup_logging(
        level=logging.INFO,
        use_color=False,
        pretty_json=False
    )
    
    # Configura loggers específicos para produção
    production_loggers = {
        'sqlalchemy.engine': logging.ERROR,
        'sqlalchemy.pool': logging.ERROR,
        'httpx': logging.ERROR,
        'httpcore': logging.ERROR,
    }
    
    for logger_name, level in production_loggers.items():
        logging.getLogger(logger_name).setLevel(level)

def configure_development_logging():
    """Configura logging otimizado para desenvolvimento."""
    setup_logging(
        level=logging.INFO,  # Mudei para INFO para reduzir verbosidade
        use_color=True,
        pretty_json=True
    )
    
    # Configuração específica para desenvolvimento
    dev_loggers = {
        'sqlalchemy.engine': logging.INFO,  # Mantém INFO para ver queries formatadas
        'sqlalchemy.pool': logging.WARNING,
        'sqlalchemy.dialects': logging.WARNING,
        'sqlalchemy.orm': logging.WARNING,
        'sqlalchemy': logging.INFO,
    }
    
    for logger_name, level in dev_loggers.items():
        logging.getLogger(logger_name).setLevel(level)

def configure_test_logging():
    """Configura logging otimizado para testes."""
    setup_logging(
        level=logging.WARNING,
        use_color=False,
        pretty_json=False
    )
    
    # Silencia logs durante testes
    test_loggers = [
        'sqlalchemy.engine',
        'sqlalchemy.pool',
        'httpx',
        'httpcore',
        'urllib3',
    ]
    
    for logger_name in test_loggers:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL) 