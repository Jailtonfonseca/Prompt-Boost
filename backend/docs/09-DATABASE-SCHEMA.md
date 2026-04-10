# 09 - Database Schema & SQLAlchemy Models

## 🎯 Objetivo

Documentar o **design de banco de dados** para Prompt-Boost v2.0 usando SQLAlchemy ORM. Este documento cobre:

- Modelos SQLAlchemy para todas entidades
- Relacionamentos e constraints
- Estratégia de migrations com Alembic
- Indexação e performance
- Audit trails e soft deletes
- Query patterns otimizadas
- Backup e recovery strategy

Suporta PostgreSQL, MySQL, SQLite com adaptações mínimas.

---

## 📐 Diagrama ER (Entity-Relationship)

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ id (PK)                                                    │ │
│  │ email (UNIQUE, indexed)                                   │ │
│  │ api_key (UNIQUE)                                          │ │
│  │ created_at, updated_at                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────┬────────────────────────────────────────────────────────┘
         │ 1:N
         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    RECURSION_SESSION                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ id (PK)                                                    │ │
│  │ user_id (FK) indexed                                      │ │
│  │ technique (enum: self_refine, tot, mcts, etc)            │ │
│  │ status (queued, running, completed, failed)              │ │
│  │ created_at, updated_at                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────┬────────┬─────────────────────────────────────────────────┘
         │ 1:N    │ 1:N
         ↓        ↓
    ┌─────────────────┐    ┌──────────────────────┐
    │  ITERATION      │    │  VERIFICATION_RESULT │
    ├─────────────────┤    ├──────────────────────┤
    │ id (PK)         │    │ id (PK)              │
    │ session_id (FK) │    │ session_id (FK)      │
    │ iteration_num   │    │ status (pass/fail)   │
    │ candidates (JSON│    │ alignment_score      │
    │ feedback (TEXT) │    │ verification_json    │
    └─────────────────┘    └──────────────────────┘
```

---

## 🏗️ Modelos SQLAlchemy

### 1. Base Model Mixin

```python
from sqlalchemy import Column, String, DateTime, Integer, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin
from datetime import datetime
import uuid

Base = declarative_base()

@declarative_mixin
class TimestampMixin:
    """Adiciona timestamps criação e atualização."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

@declarative_mixin
class AuditMixin:
    """Adiciona auditoria de mudanças."""
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    deleted_at = Column(DateTime, nullable=True, index=True)
    deleted_by = Column(String(255), nullable=True)

@declarative_mixin
class IdMixin:
    """Adiciona ID primária com UUID."""
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

class BaseModel(Base, IdMixin, TimestampMixin, AuditMixin):
    """Classe base para todos os modelos."""
    __abstract__ = True
    
    def to_dict(self):
        """Converte para dicionário."""
        return {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }
```

### 2. User Model

```python
from sqlalchemy import Column, String, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

class User(BaseModel):
    """
    Usuário do sistema.
    
    Atributos:
        email: Email único
        api_key: Chave API para autenticação
        full_name: Nome completo
        is_active: Se usuário está ativo
        subscription_tier: free, pro, enterprise
        max_monthly_tokens: Limite de tokens/mês
        sessions: Relacionamento com RecursionSession
    """
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
        UniqueConstraint('api_key', name='uq_user_api_key'),
    )
    
    email = Column(String(255), nullable=False, index=True, unique=True)
    api_key = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    subscription_tier = Column(String(50), default='free')  # free, pro, enterprise
    max_monthly_tokens = Column(Integer, default=1_000_000)
    
    # Relacionamentos
    sessions = relationship('RecursionSession', back_populates='user', cascade='all, delete-orphan')
    usage_stats = relationship('UsageStats', back_populates='user', cascade='all, delete-orphan')
    
    def is_within_quota(self, tokens_used: int) -> bool:
        """Verifica se usuário está dentro da cota."""
        total_used = sum(s.tokens_used for s in self.usage_stats)
        return total_used + tokens_used <= self.max_monthly_tokens

class UsageStats(BaseModel):
    """Rastreia uso mensal de tokens."""
    __tablename__ = 'usage_stats'
    
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    year_month = Column(String(7), nullable=False)  # YYYY-MM
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    requests_count = Column(Integer, default=0)
    
    user = relationship('User', back_populates='usage_stats')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'year_month', name='uq_usage_user_month'),
        Index('idx_usage_user_month', 'user_id', 'year_month'),
    )
```

### 3. RecursionSession Model

```python
from sqlalchemy import Enum as SQLEnum
from enum import Enum as PyEnum

class TechniqueType(PyEnum):
    """Técnicas disponíveis."""
    SELF_REFINE = "self_refine"
    TOT = "tree_of_thoughts"
    GOT = "graph_of_thoughts"
    MCTS = "mcts"
    DEBATE = "debate"
    ALIGNMENT = "alignment"
    AUTOFORMAL = "autoformal"

class SessionStatus(PyEnum):
    """Estados da sessão."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RecursionSession(BaseModel):
    """
    Sessão de raciocínio recursivo.
    Representa uma execução completa de um engine.
    """
    __tablename__ = 'recursion_sessions'
    __table_args__ = (
        Index('idx_session_user_created', 'user_id', 'created_at'),
        Index('idx_session_status_created', 'status', 'created_at'),
    )
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Conteúdo
    initial_prompt = Column(Text, nullable=False)
    technique = Column(SQLEnum(TechniqueType), nullable=False, index=True)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.QUEUED, nullable=False, index=True)
    
    # Parâmetros
    temperature = Column(Float, default=0.7)
    max_iterations = Column(Integer, default=5)
    max_tokens = Column(Integer, default=2000)
    provider_config = Column(JSON, nullable=True)  # Config do LLM provider
    
    # Resultados
    final_answer = Column(Text, nullable=True)
    quality_score = Column(Float, nullable=True)
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    execution_time_ms = Column(Integer, nullable=True)
    
    # Metadata
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)
    
    # Relacionamentos
    user = relationship('User', back_populates='sessions')
    iterations = relationship('IterationRecord', back_populates='session', cascade='all, delete-orphan')
    verification_results = relationship('VerificationResult', back_populates='session', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<RecursionSession {self.id} technique={self.technique.value} status={self.status.value}>"
```

### 4. IterationRecord Model

```python
class IterationRecord(BaseModel):
    """
    Registro de uma iteração dentro de uma sessão.
    Captures candidates, scores, feedback em cada passo.
    """
    __tablename__ = 'iteration_records'
    __table_args__ = (
        Index('idx_iteration_session', 'session_id'),
        Index('idx_iteration_num', 'session_id', 'iteration_number'),
    )
    
    # Foreign key
    session_id = Column(String(36), ForeignKey('recursion_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Iteração
    iteration_number = Column(Integer, nullable=False)
    
    # Dados
    candidates = Column(JSON, nullable=False)  # List of candidates generated
    candidates_scores = Column(JSON, nullable=False)  # {candidate_id: score}
    selected_candidate = Column(String(255), nullable=True)
    
    # Feedback e refinamento
    feedback = Column(Text, nullable=True)
    reasoning = Column(Text, nullable=True)
    
    # Tokens
    tokens_generated = Column(Integer, default=0)
    tokens_feedback = Column(Integer, default=0)
    
    # Relacionamento
    session = relationship('RecursionSession', back_populates='iterations')
    
    def get_best_candidate(self):
        """Retorna candidato com melhor score."""
        if not self.candidates_scores:
            return None
        best_id = max(self.candidates_scores, key=self.candidates_scores.get)
        for cand in self.candidates:
            if cand.get('id') == best_id:
                return cand
        return None
```

### 5. VerificationResult Model

```python
class VerificationStatus(PyEnum):
    """Status de verificação."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    INCONCLUSIVE = "inconclusive"

class VerificationResult(BaseModel):
    """
    Resultado de verificação de uma resposta.
    Vinculado com sessão e iteração.
    """
    __tablename__ = 'verification_results'
    __table_args__ = (
        Index('idx_verification_session', 'session_id'),
        Index('idx_verification_status', 'status'),
    )
    
    # Foreign keys
    session_id = Column(String(36), ForeignKey('recursion_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    iteration_id = Column(String(36), ForeignKey('iteration_records.id', ondelete='SET NULL'), nullable=True)
    
    # Verificação
    verification_type = Column(String(50), nullable=False)  # logical, relevance, safety, bias, etc
    status = Column(SQLEnum(VerificationStatus), nullable=False, index=True)
    alignment_score = Column(Float, nullable=False)
    
    # Detalhes
    checks = Column(JSON, nullable=False)  # List of individual checks
    warnings = Column(JSON, default=list)
    errors = Column(JSON, default=list)
    
    # Conteúdo verificado
    content_verified = Column(Text, nullable=False)
    verification_metadata = Column(JSON, nullable=True)
    
    # Relacionamento
    session = relationship('RecursionSession', back_populates='verification_results')
    
    def get_critical_failures(self) -> int:
        """Conta falhas críticas."""
        return sum(1 for check in self.checks if check.get('severity') == 'critical' and not check.get('passed'))
```

### 6. Cache Model

```python
class ResponseCache(BaseModel):
    """
    Cache de respostas LLM para reutilização.
    Reduz custos ao reutilizar respostas idênticas.
    """
    __tablename__ = 'response_cache'
    __table_args__ = (
        Index('idx_cache_hash', 'prompt_hash'),
        Index('idx_cache_created', 'created_at'),
        UniqueConstraint('prompt_hash', 'model_id', name='uq_cache_prompt_model'),
    )
    
    prompt_hash = Column(String(64), nullable=False, index=True)  # SHA256
    model_id = Column(String(100), nullable=False, index=True)
    prompt_full = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    tokens_saved = Column(Integer, default=0)
    hit_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    
    ttl_seconds = Column(Integer, default=86400)  # 24 horas padrão
    
    def is_expired(self) -> bool:
        """Verifica se cache expirou."""
        if not self.ttl_seconds:
            return False
        age_seconds = (datetime.utcnow() - self.created_at).total_seconds()
        return age_seconds > self.ttl_seconds
```

---

## 🔄 Migrations com Alembic

### alembic/versions/001_initial_schema.py

```python
"""Initial schema creation."""
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Criar tabelas iniciais."""
    
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('api_key', sa.String(255), unique=True, nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('subscription_tier', sa.String(50), default='free'),
        sa.Column('max_monthly_tokens', sa.Integer, default=1000000),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.Column('created_by', sa.String(255)),
        sa.Column('updated_by', sa.String(255)),
        sa.Column('deleted_at', sa.DateTime),
        sa.Column('deleted_by', sa.String(255)),
    )
    
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_user_api_key', 'users', ['api_key'])
    op.create_index('idx_user_active', 'users', ['is_active'])
    
    # ... Criar outras tabelas ...

def downgrade():
    """Reverter schema."""
    op.drop_table('users')
```

---

## 📦 Repository Pattern for Data Access

```python
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

class BaseRepository:
    """Base para todos os repositories."""
    
    def __init__(self, session: Session, model_class):
        self.session = session
        self.model_class = model_class
    
    def create(self, **kwargs):
        """Cria nova entidade."""
        entity = self.model_class(**kwargs)
        self.session.add(entity)
        self.session.commit()
        return entity
    
    def get_by_id(self, id: str):
        """Busca por ID."""
        return self.session.query(self.model_class).filter(
            self.model_class.id == id,
            self.model_class.deleted_at.is_(None)
        ).first()
    
    def get_all(self, limit: int = 100, offset: int = 0):
        """Lista com paginação."""
        return self.session.query(self.model_class).filter(
            self.model_class.deleted_at.is_(None)
        ).limit(limit).offset(offset).all()
    
    def update(self, id: str, **kwargs):
        """Atualiza entidade."""
        entity = self.get_by_id(id)
        for key, value in kwargs.items():
            setattr(entity, key, value)
        self.session.commit()
        return entity
    
    def soft_delete(self, id: str):
        """Soft delete (marca deleted_at)."""
        return self.update(id, deleted_at=datetime.utcnow())

class RecursionSessionRepository(BaseRepository):
    """Repository para RecursionSession."""
    
    def __init__(self, session: Session):
        super().__init__(session, RecursionSession)
    
    def get_by_user(self, user_id: str, limit: int = 50):
        """Lista sessões de um usuário."""
        return self.session.query(RecursionSession).filter(
            RecursionSession.user_id == user_id,
            RecursionSession.deleted_at.is_(None)
        ).order_by(desc(RecursionSession.created_at)).limit(limit).all()
    
    def get_stats_by_user(self, user_id: str):
        """Retorna estatísticas do usuário."""
        return self.session.query(
            func.count(RecursionSession.id).label('total_sessions'),
            func.sum(RecursionSession.tokens_used).label('total_tokens'),
            func.avg(RecursionSession.quality_score).label('avg_quality'),
            func.sum(RecursionSession.cost_usd).label('total_cost')
        ).filter(
            RecursionSession.user_id == user_id,
            RecursionSession.status == SessionStatus.COMPLETED
        ).first()
    
    def get_running_sessions(self):
        """Retorna sessões em execução."""
        return self.session.query(RecursionSession).filter(
            RecursionSession.status == SessionStatus.RUNNING
        ).all()
```

---

## ✅ Checklist de Implementação

- [ ] Criar modelos SQLAlchemy para todas 6+ entidades
- [ ] Implementar base model mixins (timestamp, audit, id)
- [ ] Criar indexes de performance (user_id, created_at, status)
- [ ] Implementar soft deletes com deleted_at
- [ ] Criar constraints UNIQUE apropriados
- [ ] Implementar relationships com cascade
- [ ] Criar migration initial com Alembic
- [ ] Implementar repository pattern
- [ ] Adicionar query optimization (selects específicos)
- [ ] Criar fixtures para testes
- [ ] Implementar connection pooling
- [ ] Adicionar logging de queries lentas
- [ ] Criar backup strategy
- [ ] Documentar índices e performance tuning

---

## 🔗 Referências Cruzadas

- **10-WEBSOCKET-PROTOCOL.md**: Armazenar dados de conexão
- **11-PERFORMANCE-MONITORING.md**: Métricas de database performance
- **13-API-REFERENCE.md**: Endpoints que usam modelos

---

---

**Última atualização**: 2025-04-10
**Versão**: 2.0.0
**Status**: Completo
