#!/usr/bin/env python3
"""
Sistema de Testes Automatizados para API Lycosidae Interpreter
Testa todas as rotas da API com requisições HTTP reais
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sys
import os

# Configurações
BASE_URL = "http://localhost:8080"
ROUTE_PREFIX = "/route"
print(BASE_URL)
print(ROUTE_PREFIX)    
class TestResult:
    """Classe para armazenar resultados de testes"""
    def __init__(self, test_name: str, endpoint: str, method: str):
        self.test_name = test_name
        self.endpoint = endpoint
        self.method = method
        self.status_code = None
        self.response_time = 0
        self.success = False
        self.error_message = None
        self.response_data = None
        self.created_id = None

class APITester:
    """Classe principal para executar testes da API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results: List[TestResult] = []
        self.created_resources = {
            'users': [],
            'competitions': [],
            'exercises': [],
            'tags': [],
            'teams': [],
            'containers': [],
            'user_competitions': [],
            'user_teams': [],
            'team_competitions': [],
            'exercise_tags': [],
            'exercise_competitions': [],
            'container_competitions': []
        }
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, max_retries: int = 3) -> TestResult:
        """
        Faz uma requisição HTTP com retry automático e retorna o resultado
        """
        url = f"{self.base_url}{endpoint}"
        test_name = f"{method.upper()} {endpoint}"
        
        result = TestResult(test_name, endpoint, method)
        start_time = time.time()
        
        for attempt in range(max_retries + 1):
            try:
                # Configurar timeout para evitar travamentos
                timeout = (5, 30)  # (connect timeout, read timeout)
                
                if method.upper() == "GET":
                    response = self.session.get(url, params=params, timeout=timeout)
                elif method.upper() == "POST":
                    response = self.session.post(url, json=data, timeout=timeout)
                elif method.upper() == "PUT":
                    response = self.session.put(url, json=data, timeout=timeout)
                elif method.upper() == "DELETE":
                    response = self.session.delete(url, timeout=timeout)
                else:
                    raise ValueError(f"Método HTTP não suportado: {method}")
                
                result.response_time = time.time() - start_time
                result.status_code = response.status_code
                result.success = 200 <= response.status_code < 300
                
                try:
                    result.response_data = response.json()
                except:
                    result.response_data = response.text
                    
                if not result.success:
                    result.error_message = f"Status {result.status_code}: {result.response_data}"
                
                # Se chegou até aqui, a requisição foi feita com sucesso
                break
                
            except requests.exceptions.Timeout as e:
                if attempt < max_retries:
                    print(f"  ⏰ Timeout na tentativa {attempt + 1}/{max_retries + 1}, tentando novamente...")
                    time.sleep(1)  # Aguarda 1 segundo antes de tentar novamente
                    continue
                else:
                    result.response_time = time.time() - start_time
                    result.success = False
                    result.error_message = f"Timeout após {max_retries + 1} tentativas: {str(e)}"
                    break
                    
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries:
                    print(f"  🔌 Erro de conexão na tentativa {attempt + 1}/{max_retries + 1}, tentando novamente...")
                    time.sleep(2)  # Aguarda 2 segundos antes de tentar novamente
                    continue
                else:
                    result.response_time = time.time() - start_time
                    result.success = False
                    result.error_message = f"Erro de conexão após {max_retries + 1} tentativas: {str(e)}"
                    break
                    
            except Exception as e:
                result.response_time = time.time() - start_time
                result.success = False
                result.error_message = str(e)
                break
            
        self.test_results.append(result)
        return result
    
    def test_health_check(self):
        """Testa o endpoint de health check"""
        print("🔍 Testando Health Check...")
        result = self.make_request("GET", "/")
        if result.success:
            print(f"✅ Health Check: OK ({result.response_time:.3f}s)")
        else:
            print(f"❌ Health Check: FALHOU - {result.error_message}")
        return result
    
    def test_root_route(self):
        """Testa a rota raiz do router"""
        print("🔍 Testando Rota Raiz...")
        result = self.make_request("GET", f"{ROUTE_PREFIX}")
        if result.success:
            print(f"✅ Rota Raiz: OK ({result.response_time:.3f}s)")
        else:
            print(f"❌ Rota Raiz: FALHOU - {result.error_message}")
        return result
    
    def test_user_operations(self):
        """Testa todas as operações de usuários"""
        print("\n👤 Testando Operações de Usuários...")
        
        # Dados de teste para usuário
        user_data = {
            "username": f"testuser_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "testpassword123",
            "phone_number": "+5511999999999"
        }
        
        # Teste 1: Criar usuário
        print("  📝 Criando usuário...")
        result = self.make_request("POST", f"{ROUTE_PREFIX}/register", user_data)
        if result.success:
            print(f"  ✅ Usuário criado: OK ({result.response_time:.3f}s)")
            if result.response_data and 'id' in result.response_data:
                self.created_resources['users'].append(result.response_data['id'])
                result.created_id = result.response_data['id']
        else:
            print(f"  ❌ Criação de usuário: FALHOU - {result.error_message}")
        
        # Teste 2: Tentar criar usuário com email duplicado
        print("  📝 Testando email duplicado...")
        result = self.make_request("POST", f"{ROUTE_PREFIX}/register", user_data)
        if result.status_code == 400:
            # Para este teste específico, status 400 é sucesso
            result.success = True
            print(f"  ✅ Validação de email duplicado: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Validação de email duplicado: FALHOU - {result.error_message}")
    
    def test_competition_operations(self):
        """Testa todas as operações de competições"""
        print("\n🏆 Testando Operações de Competições...")
        
        # Dados de teste para competição
        competition_data = {
            "name": f"Competição Teste {uuid.uuid4().hex[:8]}",
            "organizer": "Organizador Teste",
            "invite_code": f"TEST{uuid.uuid4().hex[:8].upper()}",
            "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        # Teste 1: Criar competição
        print("  📝 Criando competição...")
        result = self.make_request("POST", f"{ROUTE_PREFIX}/competitions", competition_data)
        if result.success:
            print(f"  ✅ Competição criada: OK ({result.response_time:.3f}s)")
            if result.response_data and 'id' in result.response_data:
                self.created_resources['competitions'].append(result.response_data['id'])
                result.created_id = result.response_data['id']
            else:
                print(f"  ❌ Competição criada mas sem ID na resposta")
                return
        else:
            print(f"  ❌ Criação de competição: FALHOU - {result.error_message}")
            return
        
        competition_id = result.created_id
        
        # Teste 2: Buscar competição por ID
        print("  🔍 Buscando competição por ID...")
        result = self.make_request("GET", f"{ROUTE_PREFIX}/competitions/{competition_id}")
        if result.success:
            print(f"  ✅ Busca por ID: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Busca por ID: FALHOU - {result.error_message}")
        
        # Teste 3: Buscar competição por código de convite
        print("  🔍 Buscando competição por código de convite...")
        result = self.make_request("GET", f"{ROUTE_PREFIX}/competitions/invite/{competition_data['invite_code']}")
        if result.success:
            print(f"  ✅ Busca por código: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Busca por código: FALHOU - {result.error_message}")
        
        # Teste 4: Atualizar competição
        print("  📝 Atualizando competição...")
        updated_data = competition_data.copy()
        updated_data["name"] = f"Competição Atualizada {uuid.uuid4().hex[:8]}"
        result = self.make_request("PUT", f"{ROUTE_PREFIX}/competitions/{competition_id}", updated_data)
        if result.success:
            print(f"  ✅ Atualização: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Atualização: FALHOU - {result.error_message}")
        
        # Teste 5: Deletar competição
        print("  🗑️ Deletando competição...")
        result = self.make_request("DELETE", f"{ROUTE_PREFIX}/competitions/{competition_id}")
        if result.success:
            print(f"  ✅ Deleção: OK ({result.response_time:.3f}s)")
            self.created_resources['competitions'].remove(competition_id)
        else:
            print(f"  ❌ Deleção: FALHOU - {result.error_message}")
    
    def test_exercise_operations(self):
        """Testa todas as operações de exercícios"""
        print("\n💪 Testando Operações de Exercícios...")
        
        # Dados de teste para exercício
        exercise_data = {
            "link": f"https://example.com/exercise/{uuid.uuid4().hex[:8]}",
            "name": f"Exercício Teste {uuid.uuid4().hex[:8]}",
            "score": 100,
            "difficulty": "medium",
            "port": 8080
        }
        
        # Teste 1: Criar exercício
        print("  📝 Criando exercício...")
        result = self.make_request("POST", f"{ROUTE_PREFIX}/exercises", exercise_data)
        if result.success:
            print(f"  ✅ Exercício criado: OK ({result.response_time:.3f}s)")
            if result.response_data and 'id' in result.response_data:
                self.created_resources['exercises'].append(result.response_data['id'])
                result.created_id = result.response_data['id']
        else:
            print(f"  ❌ Criação de exercício: FALHOU - {result.error_message}")
            return
        
        exercise_id = result.created_id
        
        # Teste 2: Buscar exercício por ID
        print("  🔍 Buscando exercício por ID...")
        result = self.make_request("GET", f"{ROUTE_PREFIX}/exercises/{exercise_id}")
        if result.success:
            print(f"  ✅ Busca por ID: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Busca por ID: FALHOU - {result.error_message}")
        
        # Teste 3: Atualizar exercício
        print("  📝 Atualizando exercício...")
        updated_data = exercise_data.copy()
        updated_data["name"] = f"Exercício Atualizado {uuid.uuid4().hex[:8]}"
        updated_data["score"] = 150
        result = self.make_request("PUT", f"{ROUTE_PREFIX}/exercises/{exercise_id}", updated_data)
        if result.success:
            print(f"  ✅ Atualização: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Atualização: FALHOU - {result.error_message}")
        
        # Teste 4: Deletar exercício
        print("  🗑️ Deletando exercício...")
        result = self.make_request("DELETE", f"{ROUTE_PREFIX}/exercises/{exercise_id}")
        if result.success:
            print(f"  ✅ Deleção: OK ({result.response_time:.3f}s)")
            self.created_resources['exercises'].remove(exercise_id)
        else:
            print(f"  ❌ Deleção: FALHOU - {result.error_message}")
    
    def test_tag_operations(self):
        """Testa todas as operações de tags"""
        print("\n🏷️ Testando Operações de Tags...")
        
        # Dados de teste para tag
        tag_data = {
            "type": f"test_tag_{uuid.uuid4().hex[:8]}"
        }
        
        # Teste 1: Criar tag
        print("  📝 Criando tag...")
        result = self.make_request("POST", f"{ROUTE_PREFIX}/tags", tag_data)
        if result.success:
            print(f"  ✅ Tag criada: OK ({result.response_time:.3f}s)")
            if result.response_data and 'id' in result.response_data:
                self.created_resources['tags'].append(result.response_data['id'])
                result.created_id = result.response_data['id']
        else:
            print(f"  ❌ Criação de tag: FALHOU - {result.error_message}")
            return
        
        tag_id = result.created_id
        
        # Teste 2: Buscar tag por ID
        print("  🔍 Buscando tag por ID...")
        result = self.make_request("GET", f"{ROUTE_PREFIX}/tags/{tag_id}")
        if result.success:
            print(f"  ✅ Busca por ID: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Busca por ID: FALHOU - {result.error_message}")
        
        # Teste 3: Buscar tag por tipo
        print("  🔍 Buscando tag por tipo...")
        result = self.make_request("GET", f"{ROUTE_PREFIX}/tags/type/{tag_data['type']}")
        if result.success:
            print(f"  ✅ Busca por tipo: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Busca por tipo: FALHOU - {result.error_message}")
        
        # Teste 4: Atualizar tag
        print("  📝 Atualizando tag...")
        updated_data = tag_data.copy()
        updated_data["type"] = f"updated_tag_{uuid.uuid4().hex[:8]}"
        result = self.make_request("PUT", f"{ROUTE_PREFIX}/tags/{tag_id}", updated_data)
        if result.success:
            print(f"  ✅ Atualização: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Atualização: FALHOU - {result.error_message}")
        
        # Teste 5: Deletar tag
        print("  🗑️ Deletando tag...")
        result = self.make_request("DELETE", f"{ROUTE_PREFIX}/tags/{tag_id}")
        if result.success:
            print(f"  ✅ Deleção: OK ({result.response_time:.3f}s)")
            self.created_resources['tags'].remove(tag_id)
        else:
            print(f"  ❌ Deleção: FALHOU - {result.error_message}")
    
    def test_team_operations(self):
        """Testa todas as operações de times"""
        print("\n👥 Testando Operações de Times...")
        
        # Primeiro, precisamos criar uma competição e um usuário
        print("  📝 Preparando dependências...")
        
        # Criar competição
        competition_data = {
            "name": f"Competição para Time {uuid.uuid4().hex[:8]}",
            "organizer": "Organizador Teste",
            "invite_code": f"TEAM{uuid.uuid4().hex[:8].upper()}",
            "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        comp_result = self.make_request("POST", f"{ROUTE_PREFIX}/competitions", competition_data)
        if not comp_result.success:
            print(f"  ❌ Falha ao criar competição: {comp_result.error_message}")
            return
        
        # Definir created_id se a resposta contém um ID
        if comp_result.response_data and 'id' in comp_result.response_data:
            comp_result.created_id = comp_result.response_data['id']
        
        competition_id = comp_result.created_id
        print(f"  🔍 Debug - competition_id: {competition_id}")
        if not competition_id:
            print(f"  ❌ Competição criada mas sem ID")
            return
        
        self.created_resources['competitions'].append(competition_id)
        
        # Criar usuário
        user_data = {
            "username": f"teamuser_{uuid.uuid4().hex[:8]}",
            "email": f"team_{uuid.uuid4().hex[:8]}@example.com",
            "password": "testpassword123",
            "phone_number": "+5511999999999"
        }
        
        user_result = self.make_request("POST", f"{ROUTE_PREFIX}/register", user_data)
        if not user_result.success:
            print(f"  ❌ Falha ao criar usuário: {user_result.error_message}")
            return
        
        # Definir created_id se a resposta contém um ID
        if user_result.response_data and 'id' in user_result.response_data:
            user_result.created_id = user_result.response_data['id']
        
        user_id = user_result.created_id
        if not user_id:
            print(f"  ❌ Usuário criado mas sem ID")
            return
        
        self.created_resources['users'].append(user_id)
        
        # Dados de teste para time
        team_data = {
            "name": f"Time Teste {uuid.uuid4().hex[:8]}",
            "competition": competition_id,
            "creator": user_id,
            "score": 0
        }
        
        # Verificar se os IDs são válidos
        if not competition_id or not user_id:
            print(f"  ❌ IDs inválidos - competition_id: {competition_id}, user_id: {user_id}")
            return
        
        print(f"  🔍 Debug - competition_id: {competition_id}, user_id: {user_id}")
        
        # Teste 1: Criar time
        print("  📝 Criando time...")
        result = self.make_request("POST", f"{ROUTE_PREFIX}/teams", team_data)
        if result.success:
            print(f"  ✅ Time criado: OK ({result.response_time:.3f}s)")
            if result.response_data and 'id' in result.response_data:
                self.created_resources['teams'].append(result.response_data['id'])
                result.created_id = result.response_data['id']
        else:
            print(f"  ❌ Criação de time: FALHOU - {result.error_message}")
            return
        
        team_id = result.created_id
        
        # Teste 2: Buscar time por ID
        print("  🔍 Buscando time por ID...")
        result = self.make_request("GET", f"{ROUTE_PREFIX}/teams/{team_id}")
        if result.success:
            print(f"  ✅ Busca por ID: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Busca por ID: FALHOU - {result.error_message}")
        
        # Teste 3: Atualizar time
        print("  📝 Atualizando time...")
        updated_data = team_data.copy()
        updated_data["name"] = f"Time Atualizado {uuid.uuid4().hex[:8]}"
        updated_data["score"] = 50
        result = self.make_request("PUT", f"{ROUTE_PREFIX}/teams/{team_id}", updated_data)
        if result.success:
            print(f"  ✅ Atualização: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Atualização: FALHOU - {result.error_message}")
        
        # Teste 4: Deletar time
        print("  🗑️ Deletando time...")
        result = self.make_request("DELETE", f"{ROUTE_PREFIX}/teams/{team_id}")
        if result.success:
            print(f"  ✅ Deleção: OK ({result.response_time:.3f}s)")
            self.created_resources['teams'].remove(team_id)
        else:
            print(f"  ❌ Deleção: FALHOU - {result.error_message}")
    
    def test_container_operations(self):
        """Testa todas as operações de containers"""
        print("\n📦 Testando Operações de Containers...")
        
        # Dados de teste para container
        container_data = {
            "deadline": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        # Teste 1: Criar container
        print("  📝 Criando container...")
        result = self.make_request("POST", f"{ROUTE_PREFIX}/containers", container_data)
        if result.success:
            print(f"  ✅ Container criado: OK ({result.response_time:.3f}s)")
            if result.response_data and 'id' in result.response_data:
                self.created_resources['containers'].append(result.response_data['id'])
                result.created_id = result.response_data['id']
        else:
            print(f"  ❌ Criação de container: FALHOU - {result.error_message}")
            return
        
        container_id = result.created_id
        
        # Teste 2: Buscar container por ID
        print("  🔍 Buscando container por ID...")
        result = self.make_request("GET", f"{ROUTE_PREFIX}/containers/{container_id}")
        if result.success:
            print(f"  ✅ Busca por ID: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Busca por ID: FALHOU - {result.error_message}")
        
        # Teste 3: Atualizar container
        print("  📝 Atualizando container...")
        updated_data = container_data.copy()
        updated_data["deadline"] = (datetime.now() + timedelta(days=14)).isoformat()
        result = self.make_request("PUT", f"{ROUTE_PREFIX}/containers/{container_id}", updated_data)
        if result.success:
            print(f"  ✅ Atualização: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Atualização: FALHOU - {result.error_message}")
        
        # Teste 4: Deletar container
        print("  🗑️ Deletando container...")
        result = self.make_request("DELETE", f"{ROUTE_PREFIX}/containers/{container_id}")
        if result.success:
            print(f"  ✅ Deleção: OK ({result.response_time:.3f}s)")
            self.created_resources['containers'].remove(container_id)
        else:
            print(f"  ❌ Deleção: FALHOU - {result.error_message}")
    
    def test_relationship_operations(self):
        """Testa todas as operações de relacionamentos"""
        print("\n🔗 Testando Operações de Relacionamentos...")
        
        # Preparar dados necessários
        print("  📝 Preparando dependências...")
        
        # Criar usuário
        user_data = {
            "username": f"reluser_{uuid.uuid4().hex[:8]}",
            "email": f"rel_{uuid.uuid4().hex[:8]}@example.com",
            "password": "testpassword123",
            "phone_number": "+5511999999999"
        }
        
        user_result = self.make_request("POST", f"{ROUTE_PREFIX}/register", user_data)
        if not user_result.success:
            print(f"  ❌ Falha ao criar usuário: {user_result.error_message}")
            return
        
        # Definir created_id se a resposta contém um ID
        if user_result.response_data and 'id' in user_result.response_data:
            user_result.created_id = user_result.response_data['id']
        
        user_id = user_result.created_id
        self.created_resources['users'].append(user_id)
        
        # Criar competição
        competition_data = {
            "name": f"Competição para Relacionamentos {uuid.uuid4().hex[:8]}",
            "organizer": "Organizador Teste",
            "invite_code": f"REL{uuid.uuid4().hex[:8].upper()}",
            "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        comp_result = self.make_request("POST", f"{ROUTE_PREFIX}/competitions", competition_data)
        if not comp_result.success:
            print(f"  ❌ Falha ao criar competição: {comp_result.error_message}")
            return
        
        # Definir created_id se a resposta contém um ID
        if comp_result.response_data and 'id' in comp_result.response_data:
            comp_result.created_id = comp_result.response_data['id']
        
        competition_id = comp_result.created_id
        self.created_resources['competitions'].append(competition_id)
        
        # Criar time
        team_data = {
            "name": f"Time para Relacionamentos {uuid.uuid4().hex[:8]}",
            "competition": competition_id,
            "creator": user_id,
            "score": 0
        }
        
        team_result = self.make_request("POST", f"{ROUTE_PREFIX}/teams", team_data)
        if not team_result.success:
            print(f"  ❌ Falha ao criar time: {team_result.error_message}")
            return
        
        # Definir created_id se a resposta contém um ID
        if team_result.response_data and 'id' in team_result.response_data:
            team_result.created_id = team_result.response_data['id']
        
        team_id = team_result.created_id
        self.created_resources['teams'].append(team_id)
        
        # Criar exercício
        exercise_data = {
            "link": f"https://example.com/rel_exercise/{uuid.uuid4().hex[:8]}",
            "name": f"Exercício para Relacionamentos {uuid.uuid4().hex[:8]}",
            "score": 100,
            "difficulty": "medium",
            "port": 9090
        }
        
        exercise_result = self.make_request("POST", f"{ROUTE_PREFIX}/exercises", exercise_data)
        if not exercise_result.success:
            print(f"  ❌ Falha ao criar exercício: {exercise_result.error_message}")
            return
        
        # Definir created_id se a resposta contém um ID
        if exercise_result.response_data and 'id' in exercise_result.response_data:
            exercise_result.created_id = exercise_result.response_data['id']
        
        exercise_id = exercise_result.created_id
        self.created_resources['exercises'].append(exercise_id)
        
        # Criar tag
        tag_data = {
            "type": f"rel_tag_{uuid.uuid4().hex[:8]}"
        }
        
        tag_result = self.make_request("POST", f"{ROUTE_PREFIX}/tags", tag_data)
        if not tag_result.success:
            print(f"  ❌ Falha ao criar tag: {tag_result.error_message}")
            return
        
        # Definir created_id se a resposta contém um ID
        if tag_result.response_data and 'id' in tag_result.response_data:
            tag_result.created_id = tag_result.response_data['id']
        
        tag_id = tag_result.created_id
        self.created_resources['tags'].append(tag_id)
        
        # Criar container
        container_data = {
            "deadline": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        container_result = self.make_request("POST", f"{ROUTE_PREFIX}/containers", container_data)
        if not container_result.success:
            print(f"  ❌ Falha ao criar container: {container_result.error_message}")
            return
        
        # Definir created_id se a resposta contém um ID
        if container_result.response_data and 'id' in container_result.response_data:
            container_result.created_id = container_result.response_data['id']
        
        container_id = container_result.created_id
        self.created_resources['containers'].append(container_id)
        
        # Teste 1: User-Competition
        print("  🔗 Testando User-Competition...")
        user_comp_data = {
            "user_id": user_id,
            "competition_id": competition_id
        }
        
        result = self.make_request("POST", f"{ROUTE_PREFIX}/user-competitions", user_comp_data)
        if result.success:
            print(f"  ✅ User-Competition criado: OK ({result.response_time:.3f}s)")
            self.created_resources['user_competitions'].append(f"{user_id}_{competition_id}")
        else:
            print(f"  ❌ User-Competition: FALHOU - {result.error_message}")
        
        # Teste 2: User-Team
        print("  🔗 Testando User-Team...")
        user_team_data = {
            "user_id": user_id,
            "team_id": team_id
        }
        
        result = self.make_request("POST", f"{ROUTE_PREFIX}/user-teams", user_team_data)
        if result.success:
            print(f"  ✅ User-Team criado: OK ({result.response_time:.3f}s)")
            self.created_resources['user_teams'].append(f"{user_id}_{team_id}")
        else:
            print(f"  ❌ User-Team: FALHOU - {result.error_message}")
        
        # Teste 3: Team-Competition
        print("  🔗 Testando Team-Competition...")
        team_comp_data = {
            "team_id": team_id,
            "competition_id": competition_id
        }
        
        result = self.make_request("POST", f"{ROUTE_PREFIX}/team-competitions", team_comp_data)
        if result.success:
            print(f"  ✅ Team-Competition criado: OK ({result.response_time:.3f}s)")
            self.created_resources['team_competitions'].append(f"{team_id}_{competition_id}")
        else:
            print(f"  ❌ Team-Competition: FALHOU - {result.error_message}")
        
        # Teste 4: Exercise-Tag
        print("  🔗 Testando Exercise-Tag...")
        exercise_tag_data = {
            "exercise_id": exercise_id,
            "tag_id": tag_id
        }
        
        result = self.make_request("POST", f"{ROUTE_PREFIX}/exercise-tags", exercise_tag_data)
        if result.success:
            print(f"  ✅ Exercise-Tag criado: OK ({result.response_time:.3f}s)")
            self.created_resources['exercise_tags'].append(f"{exercise_id}_{tag_id}")
        else:
            print(f"  ❌ Exercise-Tag: FALHOU - {result.error_message}")
        
        # Teste 5: Exercise-Competition
        print("  🔗 Testando Exercise-Competition...")
        exercise_comp_data = {
            "exercise_id": exercise_id,
            "competition_id": competition_id
        }
        
        result = self.make_request("POST", f"{ROUTE_PREFIX}/exercise-competitions", exercise_comp_data)
        if result.success:
            print(f"  ✅ Exercise-Competition criado: OK ({result.response_time:.3f}s)")
            self.created_resources['exercise_competitions'].append(f"{exercise_id}_{competition_id}")
        else:
            print(f"  ❌ Exercise-Competition: FALHOU - {result.error_message}")
        
        # Teste 6: Container-Competition
        print("  🔗 Testando Container-Competition...")
        container_comp_data = {
            "container_id": container_id,
            "competition_id": competition_id
        }
        
        result = self.make_request("POST", f"{ROUTE_PREFIX}/container-competitions", container_comp_data)
        if result.success:
            print(f"  ✅ Container-Competition criado: OK ({result.response_time:.3f}s)")
            self.created_resources['container_competitions'].append(f"{container_id}_{competition_id}")
        else:
            print(f"  ❌ Container-Competition: FALHOU - {result.error_message}")
        
        # Testes de deleção dos relacionamentos
        print("  🗑️ Testando deleções de relacionamentos...")
        
        # Deletar User-Competition
        result = self.make_request("DELETE", f"{ROUTE_PREFIX}/user-competitions/{user_id}/{competition_id}")
        if result.success:
            print(f"  ✅ User-Competition deletado: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Deleção User-Competition: FALHOU - {result.error_message}")
        
        # Deletar User-Team
        result = self.make_request("DELETE", f"{ROUTE_PREFIX}/user-teams/{user_id}/{team_id}")
        if result.success:
            print(f"  ✅ User-Team deletado: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Deleção User-Team: FALHOU - {result.error_message}")
        
        # Deletar Team-Competition
        result = self.make_request("DELETE", f"{ROUTE_PREFIX}/team-competitions/{team_id}/{competition_id}")
        if result.success:
            print(f"  ✅ Team-Competition deletado: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Deleção Team-Competition: FALHOU - {result.error_message}")
        
        # Deletar Exercise-Tag
        result = self.make_request("DELETE", f"{ROUTE_PREFIX}/exercise-tags/{exercise_id}/{tag_id}")
        if result.success:
            print(f"  ✅ Exercise-Tag deletado: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Deleção Exercise-Tag: FALHOU - {result.error_message}")
        
        # Deletar Exercise-Competition
        result = self.make_request("DELETE", f"{ROUTE_PREFIX}/exercise-competitions/{exercise_id}/{competition_id}")
        if result.success:
            print(f"  ✅ Exercise-Competition deletado: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Deleção Exercise-Competition: FALHOU - {result.error_message}")
        
        # Deletar Container-Competition
        result = self.make_request("DELETE", f"{ROUTE_PREFIX}/container-competitions/{container_id}/{competition_id}")
        if result.success:
            print(f"  ✅ Container-Competition deletado: OK ({result.response_time:.3f}s)")
        else:
            print(f"  ❌ Deleção Container-Competition: FALHOU - {result.error_message}")
    
    def cleanup_resources(self):
        """Limpa todos os recursos criados durante os testes"""
        print("\n🧹 Limpando recursos criados...")
        
        # Deletar todos os recursos na ordem inversa de criação
        for container_id in reversed(self.created_resources['containers']):
            self.make_request("DELETE", f"{ROUTE_PREFIX}/containers/{container_id}")
        
        for exercise_id in reversed(self.created_resources['exercises']):
            self.make_request("DELETE", f"{ROUTE_PREFIX}/exercises/{exercise_id}")
        
        for tag_id in reversed(self.created_resources['tags']):
            self.make_request("DELETE", f"{ROUTE_PREFIX}/tags/{tag_id}")
        
        for team_id in reversed(self.created_resources['teams']):
            self.make_request("DELETE", f"{ROUTE_PREFIX}/teams/{team_id}")
        
        for competition_id in reversed(self.created_resources['competitions']):
            self.make_request("DELETE", f"{ROUTE_PREFIX}/competitions/{competition_id}")
        
        # Usuários não podem ser deletados via API, então apenas listamos
        if self.created_resources['users']:
            print(f"  ⚠️ {len(self.created_resources['users'])} usuários criados (não podem ser deletados via API)")
    
    def generate_report(self):
        """Gera um relatório detalhado dos testes"""
        print("\n" + "="*80)
        print("📊 RELATÓRIO DE TESTES")
        print("="*80)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.success)
        failed_tests = total_tests - successful_tests
        
        print(f"Total de testes executados: {total_tests}")
        print(f"Testes bem-sucedidos: {successful_tests} ✅")
        print(f"Testes falharam: {failed_tests} ❌")
        print(f"Taxa de sucesso: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ TESTES QUE FALHARAM:")
            print("-" * 50)
            for result in self.test_results:
                if not result.success:
                    print(f"• {result.test_name}")
                    print(f"  Status: {result.status_code}")
                    print(f"  Erro: {result.error_message}")
                    print(f"  Tempo: {result.response_time:.3f}s")
                    print()
        
        print("\n⏱️ ESTATÍSTICAS DE TEMPO:")
        print("-" * 50)
        response_times = [result.response_time for result in self.test_results if result.success]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            print(f"Tempo médio de resposta: {avg_time:.3f}s")
            print(f"Tempo mínimo: {min_time:.3f}s")
            print(f"Tempo máximo: {max_time:.3f}s")
        
        print("\n🔗 ENDPOINTS TESTADOS:")
        print("-" * 50)
        endpoints = set()
        for result in self.test_results:
            endpoints.add(f"{result.method.upper()} {result.endpoint}")
        
        for endpoint in sorted(endpoints):
            print(f"• {endpoint}")
        
        print("\n" + "="*80)
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': (successful_tests/total_tests)*100 if total_tests > 0 else 0,
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0
        }
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🚀 Iniciando Testes da API Lycosidae Interpreter")
        print("="*60)
        
        start_time = time.time()
        
        # Executar todos os testes
        self.test_health_check()
        self.test_root_route()
        self.test_user_operations()
        self.test_competition_operations()
        self.test_exercise_operations()
        self.test_tag_operations()
        self.test_team_operations()
        self.test_container_operations()
        self.test_relationship_operations()
        
        # Limpar recursos
        self.cleanup_resources()
        
        # Gerar relatório
        total_time = time.time() - start_time
        print(f"\n⏱️ Tempo total de execução: {total_time:.2f}s")
        
        report = self.generate_report()
        return report

def main():
    """Função principal"""
    print("🔧 Configurando testes...")
    
    # Verificar se a API está rodando
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print(f"❌ API não está respondendo corretamente. Status: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Não foi possível conectar à API em {BASE_URL}")
        print(f"   Certifique-se de que a API está rodando com: uvicorn app.main:app --reload")
        print(f"   Erro: {e}")
        sys.exit(1)
    
    # Executar testes
    tester = APITester()
    report = tester.run_all_tests()
    
    # Retornar código de saída baseado no sucesso
    if report['failed_tests'] == 0:
        print("\n🎉 Todos os testes passaram com sucesso!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {report['failed_tests']} testes falharam. Verifique os logs acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()
