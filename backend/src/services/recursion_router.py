"""
RecursionRouter - Dispatcher for selecting and executing reasoning engines
"""

from typing import Dict, List, Optional, Type

from src.engines.alignment import AlignmentEngine
from src.engines.autoformal import AutoFormalEngine
from src.engines.base import EngineConfig, EngineResult, RecursiveThinkingEngine
from src.engines.graph_of_thoughts import GraphOfThoughtsEngine
from src.engines.mcts import MCTSEngine
from src.engines.multi_agent_debate import MultiAgentDebateEngine
from src.engines.self_refine import SelfRefineEngine
from src.engines.tree_of_thoughts import TreeOfThoughtsEngine


class RecursionRouter:
    """
    Router for selecting and executing the appropriate reasoning engine.
    
    Maps technique names to engine implementations and handles execution.
    """

    # Technique -> Engine mapping
    ENGINES: Dict[str, Type[RecursiveThinkingEngine]] = {
        "self_refine": SelfRefineEngine,
        "tree_of_thoughts": TreeOfThoughtsEngine,
        "graph_of_thoughts": GraphOfThoughtsEngine,
        "mcts": MCTSEngine,
        "multi_agent_debate": MultiAgentDebateEngine,
        "alignment": AlignmentEngine,
        "autoformal": AutoFormalEngine,
    }

    @classmethod
    def get_engine(cls, technique: str) -> Type[RecursiveThinkingEngine]:
        """
        Get engine class for a technique.
        
        Args:
            technique: Technique name (e.g., "self_refine")
            
        Returns:
            Engine class
            
        Raises:
            ValueError: If technique not found
        """
        if technique not in cls.ENGINES:
            available = ", ".join(cls.ENGINES.keys())
            raise ValueError(
                f"Unknown technique '{technique}'. Available: {available}"
            )
        return cls.ENGINES[technique]

    @classmethod
    def list_techniques(cls) -> List[str]:
        """Get list of available techniques."""
        return list(cls.ENGINES.keys())

    @classmethod
    async def execute(
        cls,
        technique: str,
        prompt: str,
        config: Optional[EngineConfig] = None,
    ) -> EngineResult:
        """
        Execute reasoning engine for a technique.
        
        Args:
            technique: Technique to use
            prompt: Input prompt
            config: Engine configuration (uses defaults if None)
            
        Returns:
            EngineResult with final answer and metrics
        """
        if config is None:
            config = EngineConfig()

        engine_class = cls.get_engine(technique)
        engine = engine_class(config)

        result = await engine.execute(prompt)
        return result

    @classmethod
    async def execute_multi(
        cls,
        techniques: List[str],
        prompt: str,
        config: Optional[EngineConfig] = None,
    ) -> Dict[str, EngineResult]:
        """
        Execute multiple techniques in parallel.
        
        Args:
            techniques: List of techniques to run
            prompt: Input prompt
            config: Engine configuration
            
        Returns:
            Dictionary mapping technique -> result
        """
        import asyncio

        if config is None:
            config = EngineConfig()

        tasks = {
            technique: cls.execute(technique, prompt, config)
            for technique in techniques
        }

        results = await asyncio.gather(*tasks.values())
        return dict(zip(tasks.keys(), results))

    @classmethod
    def get_technique_info(cls, technique: str) -> dict:
        """
        Get information about a technique.
        
        Args:
            technique: Technique name
            
        Returns:
            Dictionary with technique description
        """
        descriptions = {
            "self_refine": {
                "name": "Self-Refine",
                "description": "Iteratively improve solutions through self-critique",
                "best_for": "Refinement and quality improvement",
                "iterations": 5,
            },
            "tree_of_thoughts": {
                "name": "Tree of Thoughts",
                "description": "Explore multiple reasoning branches",
                "best_for": "Complex problems with multiple solutions",
                "iterations": 3,
            },
            "graph_of_thoughts": {
                "name": "Graph of Thoughts",
                "description": "Build interconnected reasoning paths",
                "best_for": "Knowledge synthesis and relationships",
                "iterations": 4,
            },
            "mcts": {
                "name": "Monte Carlo Tree Search",
                "description": "Balance exploration and exploitation probabilistically",
                "best_for": "Strategic reasoning and decision making",
                "iterations": 5,
            },
            "multi_agent_debate": {
                "name": "Multi-Agent Debate",
                "description": "Collaborative reasoning through agent discussion",
                "best_for": "Consensus building and diverse perspectives",
                "iterations": 3,
            },
            "alignment": {
                "name": "Alignment",
                "description": "Ensure solution alignment with requirements",
                "best_for": "Constraint satisfaction and validation",
                "iterations": 4,
            },
            "autoformal": {
                "name": "AutoFormal",
                "description": "Formalize and verify solutions mathematically",
                "best_for": "Logical rigor and formal verification",
                "iterations": 4,
            },
        }

        return descriptions.get(
            technique,
            {"name": technique, "description": "Unknown technique"},
        )
