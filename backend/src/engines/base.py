"""
Base RecursiveThinkingEngine - Abstract base class for all reasoning techniques
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class EngineStatus(Enum):
    """Engine execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class IterationState:
    """State of a single iteration."""
    iteration_number: int
    prompt: str
    response: str
    quality_score: Optional[float] = None
    tokens_used: int = 0
    reasoning_trace: dict = field(default_factory=dict)
    candidates: list[str] = field(default_factory=list)


@dataclass
class EngineConfig:
    """Configuration for recursive engines."""
    max_iterations: int = 5
    temperature: float = 0.7
    max_tokens_per_iteration: int = 2000
    quality_threshold: float = 0.8
    timeout_seconds: int = 300
    provider: str = "openai"
    model: str = "gpt-4"
    extra_params: dict = field(default_factory=dict)


class EngineResult(BaseModel):
    """Result from engine execution."""
    status: EngineStatus
    final_answer: str
    iterations: list[IterationState]
    total_tokens_used: int
    total_cost_usd: float
    quality_score: float
    execution_time_ms: int
    error_message: Optional[str] = None


class RecursiveThinkingEngine(ABC):
    """
    Abstract base class for all recursive thinking engines.
    
    Implements a 5-step loop:
    1. Analyze: Understand the problem
    2. Generate: Create solution candidates
    3. Evaluate: Score quality of each candidate
    4. Refine: Improve based on evaluation
    5. Decide: Choose best solution or iterate
    """

    def __init__(self, config: EngineConfig):
        """Initialize engine with configuration."""
        self.config = config
        self.iterations: list[IterationState] = []
        self.status = EngineStatus.PENDING
        self.total_tokens_used = 0
        self.total_cost_usd = 0.0

    @abstractmethod
    async def analyze(self, prompt: str) -> dict[str, Any]:
        """
        Step 1: Analyze the problem.
        
        Args:
            prompt: The user's input prompt
            
        Returns:
            Analysis dictionary with problem decomposition
        """
        pass

    @abstractmethod
    async def generate(self, analysis: dict[str, Any], iteration: int) -> list[str]:
        """
        Step 2: Generate solution candidates.
        
        Args:
            analysis: Result from analyze step
            iteration: Current iteration number
            
        Returns:
            List of candidate solutions
        """
        pass

    @abstractmethod
    async def evaluate(self, candidates: list[str], analysis: dict[str, Any]) -> list[float]:
        """
        Step 3: Evaluate quality of candidates.
        
        Args:
            candidates: List of candidate solutions
            analysis: Result from analyze step
            
        Returns:
            List of quality scores (0.0 to 1.0)
        """
        pass

    @abstractmethod
    async def refine(self, best_candidate: str, analysis: dict[str, Any], iteration: int) -> str:
        """
        Step 4: Refine the best candidate.
        
        Args:
            best_candidate: The highest-scoring candidate
            analysis: Result from analyze step
            iteration: Current iteration number
            
        Returns:
            Refined solution
        """
        pass

    @abstractmethod
    async def decide(self, scores: list[float], iteration: int) -> tuple[bool, int]:
        """
        Step 5: Decide whether to continue or stop iterating.
        
        Args:
            scores: Quality scores from this iteration
            iteration: Current iteration number
            
        Returns:
            Tuple of (should_continue, best_candidate_index)
        """
        pass

    async def execute(self, prompt: str) -> EngineResult:
        """
        Execute the complete reasoning loop.
        
        Args:
            prompt: The input prompt
            
        Returns:
            EngineResult with final answer and metrics
        """
        import time
        from datetime import datetime

        start_time = time.time()
        self.status = EngineStatus.RUNNING
        self.iterations = []
        self.total_tokens_used = 0
        self.total_cost_usd = 0.0

        try:
            # Step 1: Analyze
            analysis = await self.analyze(prompt)

            for iteration_num in range(1, self.config.max_iterations + 1):
                # Step 2: Generate candidates
                candidates = await self.generate(analysis, iteration_num)

                # Step 3: Evaluate candidates
                scores = await self.evaluate(candidates, analysis)
                best_idx = scores.index(max(scores))
                best_candidate = candidates[best_idx]
                best_score = scores[best_idx]

                # Step 4: Refine best candidate
                refined = await self.refine(best_candidate, analysis, iteration_num)

                # Record iteration
                iteration_state = IterationState(
                    iteration_number=iteration_num,
                    prompt=prompt,
                    response=refined,
                    quality_score=best_score,
                    candidates=candidates,
                )
                self.iterations.append(iteration_state)

                # Step 5: Decide to continue or stop
                should_continue, _ = await self.decide(scores, iteration_num)
                if not should_continue or best_score >= self.config.quality_threshold:
                    break

            # Get final answer
            final_answer = self.iterations[-1].response if self.iterations else ""
            final_quality = self.iterations[-1].quality_score or 0.0

            self.status = EngineStatus.COMPLETED

            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            return EngineResult(
                status=self.status,
                final_answer=final_answer,
                iterations=self.iterations,
                total_tokens_used=self.total_tokens_used,
                total_cost_usd=self.total_cost_usd,
                quality_score=final_quality,
                execution_time_ms=execution_time_ms,
            )

        except Exception as e:
            self.status = EngineStatus.FAILED
            execution_time_ms = int((time.time() - start_time) * 1000)

            return EngineResult(
                status=self.status,
                final_answer="",
                iterations=self.iterations,
                total_tokens_used=self.total_tokens_used,
                total_cost_usd=self.total_cost_usd,
                quality_score=0.0,
                execution_time_ms=execution_time_ms,
                error_message=str(e),
            )
