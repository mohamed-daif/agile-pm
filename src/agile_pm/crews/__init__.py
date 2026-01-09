"""Crews module for multi-agent collaboration.

Implements P4-002: Multi-agent collaboration workflows.
"""

from .planning_crew import PlanningCrew
from .execution_crew import ExecutionCrew
from .review_crew import ReviewCrew
from .collaboration import AgentMessage, CollaborationHub
from .consensus import ConsensusStrategy, VotingConsensus, LeaderConsensus

__all__ = [
    "PlanningCrew",
    "ExecutionCrew",
    "ReviewCrew",
    "AgentMessage",
    "CollaborationHub",
    "ConsensusStrategy",
    "VotingConsensus",
    "LeaderConsensus",
]
