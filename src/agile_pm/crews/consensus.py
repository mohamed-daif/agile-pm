"""Consensus mechanisms for multi-agent decision making.

Provides strategies for agents to reach agreement on decisions.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4
from enum import Enum

from pydantic import BaseModel, Field


class DecisionStatus(str, Enum):
    """Status of a decision."""
    
    PENDING = "pending"
    VOTING = "voting"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class Vote(BaseModel):
    """A single vote from an agent."""

    voter_id: str
    decision_id: str
    choice: str = Field(description="approve, reject, abstain")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasoning: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Decision(BaseModel):
    """A decision requiring consensus."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    subject: str
    description: str
    options: list[str] = Field(default_factory=lambda: ["approve", "reject"])
    
    proposer: str
    voters: list[str] = Field(default_factory=list)
    votes: list[Vote] = Field(default_factory=list)
    
    status: DecisionStatus = Field(default=DecisionStatus.PENDING)
    result: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConsensusStrategy(ABC):
    """Base class for consensus strategies."""

    @abstractmethod
    def evaluate(self, decision: Decision) -> tuple[DecisionStatus, Optional[str]]:
        """Evaluate current votes and determine outcome.
        
        Args:
            decision: Decision to evaluate
            
        Returns:
            Tuple of (status, result)
        """
        pass
    
    @abstractmethod
    def is_complete(self, decision: Decision) -> bool:
        """Check if voting is complete.
        
        Args:
            decision: Decision to check
            
        Returns:
            True if voting is complete
        """
        pass


class VotingConsensus(ConsensusStrategy):
    """Majority voting consensus strategy.
    
    Requires a majority of voters to approve/reject.
    """

    def __init__(
        self,
        threshold: float = 0.5,
        require_all_votes: bool = False,
    ):
        """Initialize voting consensus.
        
        Args:
            threshold: Approval threshold (0.5 = majority)
            require_all_votes: Whether all voters must vote
        """
        self.threshold = threshold
        self.require_all_votes = require_all_votes
    
    def evaluate(self, decision: Decision) -> tuple[DecisionStatus, Optional[str]]:
        """Evaluate votes using majority rules.
        
        Args:
            decision: Decision to evaluate
            
        Returns:
            Tuple of (status, result)
        """
        if not decision.votes:
            return DecisionStatus.PENDING, None
        
        # Check deadline
        if decision.deadline and datetime.utcnow() > decision.deadline:
            return DecisionStatus.TIMEOUT, None
        
        # Count votes
        approve_count = sum(
            v.confidence for v in decision.votes if v.choice == "approve"
        )
        reject_count = sum(
            v.confidence for v in decision.votes if v.choice == "reject"
        )
        total_voters = len(decision.voters) if decision.voters else len(decision.votes)
        
        # Check if complete
        if not self.is_complete(decision):
            return DecisionStatus.VOTING, None
        
        # Calculate result
        approval_rate = approve_count / total_voters if total_voters > 0 else 0
        
        if approval_rate >= self.threshold:
            return DecisionStatus.APPROVED, "approve"
        else:
            return DecisionStatus.REJECTED, "reject"
    
    def is_complete(self, decision: Decision) -> bool:
        """Check if all required votes are in.
        
        Args:
            decision: Decision to check
            
        Returns:
            True if voting is complete
        """
        if self.require_all_votes:
            if decision.voters:
                voted = {v.voter_id for v in decision.votes}
                return set(decision.voters) == voted
        
        # Check if we have enough votes to determine outcome
        if not decision.voters:
            return len(decision.votes) > 0
        
        return len(decision.votes) >= len(decision.voters)


class LeaderConsensus(ConsensusStrategy):
    """Leader-based consensus strategy.
    
    A designated leader makes the final decision,
    others provide input/recommendations.
    """

    def __init__(self, leader_id: str):
        """Initialize leader consensus.
        
        Args:
            leader_id: ID of the decision-making leader
        """
        self.leader_id = leader_id
    
    def evaluate(self, decision: Decision) -> tuple[DecisionStatus, Optional[str]]:
        """Evaluate based on leader's vote.
        
        Args:
            decision: Decision to evaluate
            
        Returns:
            Tuple of (status, result)
        """
        # Find leader's vote
        leader_vote = next(
            (v for v in decision.votes if v.voter_id == self.leader_id),
            None,
        )
        
        if not leader_vote:
            return DecisionStatus.VOTING, None
        
        if leader_vote.choice == "approve":
            return DecisionStatus.APPROVED, "approve"
        elif leader_vote.choice == "reject":
            return DecisionStatus.REJECTED, "reject"
        else:
            return DecisionStatus.VOTING, None
    
    def is_complete(self, decision: Decision) -> bool:
        """Check if leader has voted.
        
        Args:
            decision: Decision to check
            
        Returns:
            True if leader has voted
        """
        return any(v.voter_id == self.leader_id for v in decision.votes)


class WeightedConsensus(ConsensusStrategy):
    """Weighted voting consensus strategy.
    
    Different voters have different weights based on expertise.
    """

    def __init__(
        self,
        weights: dict[str, float],
        threshold: float = 0.5,
    ):
        """Initialize weighted consensus.
        
        Args:
            weights: Dict of voter_id -> weight
            threshold: Approval threshold
        """
        self.weights = weights
        self.threshold = threshold
    
    def evaluate(self, decision: Decision) -> tuple[DecisionStatus, Optional[str]]:
        """Evaluate using weighted votes.
        
        Args:
            decision: Decision to evaluate
            
        Returns:
            Tuple of (status, result)
        """
        if not decision.votes:
            return DecisionStatus.PENDING, None
        
        # Calculate weighted scores
        approve_score = 0.0
        reject_score = 0.0
        total_weight = sum(
            self.weights.get(voter_id, 1.0)
            for voter_id in (decision.voters or [v.voter_id for v in decision.votes])
        )
        
        for vote in decision.votes:
            weight = self.weights.get(vote.voter_id, 1.0) * vote.confidence
            if vote.choice == "approve":
                approve_score += weight
            elif vote.choice == "reject":
                reject_score += weight
        
        if not self.is_complete(decision):
            return DecisionStatus.VOTING, None
        
        # Calculate weighted approval rate
        approval_rate = approve_score / total_weight if total_weight > 0 else 0
        
        if approval_rate >= self.threshold:
            return DecisionStatus.APPROVED, "approve"
        else:
            return DecisionStatus.REJECTED, "reject"
    
    def is_complete(self, decision: Decision) -> bool:
        """Check if all weighted voters have voted.
        
        Args:
            decision: Decision to check
            
        Returns:
            True if complete
        """
        if decision.voters:
            voted = {v.voter_id for v in decision.votes}
            return set(decision.voters).issubset(voted)
        return len(decision.votes) > 0


class ConsensusManager:
    """Manager for handling consensus decisions."""

    def __init__(self, default_strategy: Optional[ConsensusStrategy] = None):
        """Initialize consensus manager.
        
        Args:
            default_strategy: Default strategy to use
        """
        self.default_strategy = default_strategy or VotingConsensus()
        self._decisions: dict[str, Decision] = {}
        self._strategies: dict[str, ConsensusStrategy] = {}
    
    def create_decision(
        self,
        subject: str,
        description: str,
        proposer: str,
        voters: list[str],
        strategy: Optional[ConsensusStrategy] = None,
        deadline: Optional[datetime] = None,
    ) -> Decision:
        """Create a new decision.
        
        Args:
            subject: Decision subject
            description: Detailed description
            proposer: Agent proposing the decision
            voters: Agents who should vote
            strategy: Consensus strategy to use
            deadline: Optional voting deadline
            
        Returns:
            Created Decision
        """
        decision = Decision(
            subject=subject,
            description=description,
            proposer=proposer,
            voters=voters,
            deadline=deadline,
        )
        
        self._decisions[decision.id] = decision
        if strategy:
            self._strategies[decision.id] = strategy
        
        return decision
    
    def vote(
        self,
        decision_id: str,
        voter_id: str,
        choice: str,
        confidence: float = 1.0,
        reasoning: Optional[str] = None,
    ) -> Vote:
        """Cast a vote on a decision.
        
        Args:
            decision_id: Decision to vote on
            voter_id: Voter agent ID
            choice: Vote choice
            confidence: Confidence level
            reasoning: Optional reasoning
            
        Returns:
            Created Vote
            
        Raises:
            ValueError: If decision not found or voter not authorized
        """
        decision = self._decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision not found: {decision_id}")
        
        if decision.voters and voter_id not in decision.voters:
            raise ValueError(f"Voter not authorized: {voter_id}")
        
        if decision.status not in [DecisionStatus.PENDING, DecisionStatus.VOTING]:
            raise ValueError(f"Decision already finalized: {decision.status}")
        
        # Remove existing vote from same voter
        decision.votes = [v for v in decision.votes if v.voter_id != voter_id]
        
        vote = Vote(
            voter_id=voter_id,
            decision_id=decision_id,
            choice=choice,
            confidence=confidence,
            reasoning=reasoning,
        )
        decision.votes.append(vote)
        decision.status = DecisionStatus.VOTING
        
        # Evaluate decision
        self._evaluate_decision(decision)
        
        return vote
    
    def get_decision(self, decision_id: str) -> Optional[Decision]:
        """Get a decision by ID.
        
        Args:
            decision_id: Decision ID
            
        Returns:
            Decision if found
        """
        return self._decisions.get(decision_id)
    
    def _evaluate_decision(self, decision: Decision) -> None:
        """Evaluate a decision and update status.
        
        Args:
            decision: Decision to evaluate
        """
        strategy = self._strategies.get(decision.id, self.default_strategy)
        status, result = strategy.evaluate(decision)
        
        decision.status = status
        if result:
            decision.result = result
            decision.decided_at = datetime.utcnow()
    
    def get_pending_decisions(self, voter_id: str) -> list[Decision]:
        """Get pending decisions for a voter.
        
        Args:
            voter_id: Voter agent ID
            
        Returns:
            List of pending decisions
        """
        pending = []
        for decision in self._decisions.values():
            if decision.status in [DecisionStatus.PENDING, DecisionStatus.VOTING]:
                if not decision.voters or voter_id in decision.voters:
                    # Check if already voted
                    if not any(v.voter_id == voter_id for v in decision.votes):
                        pending.append(decision)
        return pending
