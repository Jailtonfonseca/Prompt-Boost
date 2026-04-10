"""
Unit Tests for Recursive Thinking Engines
"""

import pytest

from src.engines import (
    AlignmentEngine,
    AutoFormalEngine,
    EngineConfig,
    EngineStatus,
    GraphOfThoughtsEngine,
    MCTSEngine,
    MultiAgentDebateEngine,
    SelfRefineEngine,
    TreeOfThoughtsEngine,
)
from src.services.recursion_router import RecursionRouter


class TestRecursionRouter:
    """Test RecursionRouter dispatcher."""

    def test_list_techniques(self):
        """Test listing available techniques."""
        techniques = RecursionRouter.list_techniques()
        assert len(techniques) == 7
        assert "self_refine" in techniques
        assert "tree_of_thoughts" in techniques
        assert "multi_agent_debate" in techniques

    def test_get_engine(self):
        """Test getting engine by technique."""
        engine_class = RecursionRouter.get_engine("self_refine")
        assert engine_class == SelfRefineEngine

    def test_get_engine_invalid(self):
        """Test error on invalid technique."""
        with pytest.raises(ValueError):
            RecursionRouter.get_engine("invalid_technique")

    def test_get_technique_info(self):
        """Test getting technique information."""
        info = RecursionRouter.get_technique_info("tree_of_thoughts")
        assert info["name"] == "Tree of Thoughts"
        assert "description" in info
        assert "best_for" in info


class TestEngineBase:
    """Test engine base functionality."""

    @pytest.mark.asyncio
    async def test_self_refine_engine_init(self):
        """Test SelfRefineEngine initialization."""
        config = EngineConfig(max_iterations=3)
        engine = SelfRefineEngine(config)
        assert engine.config == config
        assert engine.status == EngineStatus.PENDING

    @pytest.mark.asyncio
    async def test_self_refine_analyze(self):
        """Test SelfRefineEngine.analyze method."""
        config = EngineConfig()
        engine = SelfRefineEngine(config)
        analysis = await engine.analyze("Test prompt")
        assert "task" in analysis
        assert analysis["task"] == "Test prompt"

    @pytest.mark.asyncio
    async def test_self_refine_generate(self):
        """Test SelfRefineEngine.generate method."""
        config = EngineConfig()
        engine = SelfRefineEngine(config)
        analysis = await engine.analyze("Test")
        candidates = await engine.generate(analysis, 1)
        assert len(candidates) == 1
        assert isinstance(candidates[0], str)

    @pytest.mark.asyncio
    async def test_self_refine_evaluate(self):
        """Test SelfRefineEngine.evaluate method."""
        config = EngineConfig()
        engine = SelfRefineEngine(config)
        analysis = await engine.analyze("Test")
        candidates = ["Test solution 1", "Test solution 2"]
        scores = await engine.evaluate(candidates, analysis)
        assert len(scores) == len(candidates)
        assert all(0.0 <= score <= 1.0 for score in scores)

    @pytest.mark.asyncio
    async def test_tree_of_thoughts_init(self):
        """Test TreeOfThoughtsEngine initialization."""
        config = EngineConfig(
            max_iterations=3,
            extra_params={"branching_factor": 3, "tree_depth": 2}
        )
        engine = TreeOfThoughtsEngine(config)
        assert engine.branching_factor == 3
        assert engine.tree_depth == 2

    @pytest.mark.asyncio
    async def test_tree_of_thoughts_generate(self):
        """Test TreeOfThoughtsEngine.generate creates branches."""
        config = EngineConfig(
            extra_params={"branching_factor": 4}
        )
        engine = TreeOfThoughtsEngine(config)
        analysis = await engine.analyze("Complex problem")
        branches = await engine.generate(analysis, 1)
        assert len(branches) == 4

    @pytest.mark.asyncio
    async def test_mcts_engine(self):
        """Test MCTSEngine initialization."""
        config = EngineConfig(
            extra_params={
                "num_simulations": 50,
                "exploration_constant": 1.414
            }
        )
        engine = MCTSEngine(config)
        assert engine.num_simulations == 50
        assert engine.exploration_constant == 1.414

    @pytest.mark.asyncio
    async def test_multi_agent_debate_init(self):
        """Test MultiAgentDebateEngine initialization."""
        config = EngineConfig(
            extra_params={"num_agents": 4, "debate_rounds": 3}
        )
        engine = MultiAgentDebateEngine(config)
        assert engine.num_agents == 4
        assert engine.debate_rounds == 3

    @pytest.mark.asyncio
    async def test_multi_agent_debate_agents(self):
        """Test MultiAgentDebateEngine creates agents."""
        config = EngineConfig(extra_params={"num_agents": 3})
        engine = MultiAgentDebateEngine(config)
        analysis = await engine.analyze("Test question")
        assert len(analysis["agents"]) == 3
        assert all("Agent_" in agent for agent in analysis["agents"])

    @pytest.mark.asyncio
    async def test_alignment_engine(self):
        """Test AlignmentEngine initialization."""
        engine = AlignmentEngine(EngineConfig())
        assert engine is not None

    @pytest.mark.asyncio
    async def test_alignment_evaluate(self):
        """Test AlignmentEngine.evaluate checks alignment."""
        config = EngineConfig()
        engine = AlignmentEngine(config)
        analysis = await engine.analyze("Test prompt")
        candidates = ["Solution with clarity", "Another solution"]
        scores = await engine.evaluate(candidates, analysis)
        # First candidate mentions "clarity" which is a value
        assert scores[0] > 0.0

    @pytest.mark.asyncio
    async def test_autoformal_engine(self):
        """Test AutoFormalEngine initialization."""
        engine = AutoFormalEngine(EngineConfig())
        assert engine is not None

    @pytest.mark.asyncio
    async def test_autoformal_generate(self):
        """Test AutoFormalEngine.generate creates formalizations."""
        config = EngineConfig()
        engine = AutoFormalEngine(config)
        analysis = await engine.analyze("Mathematical problem")
        candidates = await engine.generate(analysis, 1)
        assert len(candidates) == 3  # FOL, set theory, lambda calculus


class TestEngineExecution:
    """Test full engine execution."""

    @pytest.mark.asyncio
    async def test_self_refine_full_execution(self):
        """Test complete SelfRefineEngine execution."""
        config = EngineConfig(max_iterations=2, quality_threshold=0.8)
        engine = SelfRefineEngine(config)
        result = await engine.execute("Test prompt for refinement")

        assert result.status in [EngineStatus.COMPLETED, EngineStatus.FAILED]
        assert isinstance(result.final_answer, str)
        assert len(result.iterations) > 0
        assert result.total_tokens_used >= 0
        assert result.execution_time_ms > 0

    @pytest.mark.asyncio
    async def test_tree_of_thoughts_full_execution(self):
        """Test complete TreeOfThoughtsEngine execution."""
        config = EngineConfig(
            max_iterations=2,
            extra_params={"branching_factor": 2, "tree_depth": 2}
        )
        engine = TreeOfThoughtsEngine(config)
        result = await engine.execute("Complex problem to explore")

        assert result.status in [EngineStatus.COMPLETED, EngineStatus.FAILED]
        assert len(result.iterations) > 0

    @pytest.mark.asyncio
    async def test_multi_agent_debate_full_execution(self):
        """Test complete MultiAgentDebateEngine execution."""
        config = EngineConfig(
            max_iterations=2,
            extra_params={"num_agents": 3, "debate_rounds": 2}
        )
        engine = MultiAgentDebateEngine(config)
        result = await engine.execute("Question for debate")

        assert result.status in [EngineStatus.COMPLETED, EngineStatus.FAILED]
        assert len(result.iterations) > 0
