"""Tests for crew collaboration and consensus modules."""

import pytest
from datetime import datetime, timedelta
import asyncio

from agile_pm.crews.collaboration import (
    AgentMessage,
    MessageType,
    MessagePriority,
    CollaborationHub,
)
from agile_pm.crews.consensus import (
    Decision,
    DecisionStatus,
    Vote,
    VotingConsensus,
    LeaderConsensus,
    WeightedConsensus,
    ConsensusManager,
)


class TestAgentMessage:
    """Tests for AgentMessage."""

    def test_create_basic_message(self):
        """Test creating a basic message."""
        message = AgentMessage(
            type=MessageType.REQUEST,
            sender="agent-1",
            recipient="agent-2",
            subject="Test Request",
            content={"action": "test"},
        )
        
        assert message.type == MessageType.REQUEST
        assert message.sender == "agent-1"
        assert message.recipient == "agent-2"
        assert message.priority == MessagePriority.NORMAL
        assert message.id is not None
        assert message.created_at is not None
    
    def test_message_with_correlation(self):
        """Test message with correlation ID."""
        message = AgentMessage(
            type=MessageType.RESPONSE,
            sender="agent-2",
            recipient="agent-1",
            subject="Test Response",
            content={"result": "success"},
            correlation_id="req-123",
            in_reply_to="msg-456",
        )
        
        assert message.correlation_id == "req-123"
        assert message.in_reply_to == "msg-456"
    
    def test_high_priority_message(self):
        """Test high priority message."""
        message = AgentMessage(
            type=MessageType.DELEGATION,
            priority=MessagePriority.URGENT,
            sender="pm-agent",
            recipient="backend-agent",
            subject="Urgent Task",
            content={"task": "fix_critical_bug"},
        )
        
        assert message.priority == MessagePriority.URGENT


class TestCollaborationHub:
    """Tests for CollaborationHub."""

    @pytest.fixture
    def hub(self):
        """Create hub fixture."""
        return CollaborationHub()
    
    def test_register_agent(self, hub):
        """Test registering an agent."""
        async def handler(msg: AgentMessage) -> None:
            pass
        
        hub.register_agent(
            agent_id="test-agent",
            handler=handler,
            message_types=[MessageType.REQUEST],
        )
        
        assert "test-agent" in hub._agents
        assert hub._agents["test-agent"].message_types == [MessageType.REQUEST]
    
    def test_unregister_agent(self, hub):
        """Test unregistering an agent."""
        async def handler(msg: AgentMessage) -> None:
            pass
        
        hub.register_agent("test-agent", handler)
        assert "test-agent" in hub._agents
        
        hub.unregister_agent("test-agent")
        assert "test-agent" not in hub._agents
    
    def test_get_stats(self, hub):
        """Test getting hub statistics."""
        stats = hub.get_stats()
        
        assert "registered_agents" in stats
        assert "total_messages" in stats
        assert "pending_requests" in stats
        assert "queue_size" in stats
        assert stats["registered_agents"] == 0
    
    @pytest.mark.asyncio
    async def test_send_message(self, hub):
        """Test sending a message."""
        message = AgentMessage(
            type=MessageType.NOTIFICATION,
            sender="agent-1",
            recipient="agent-2",
            subject="Test",
            content="Hello",
        )
        
        await hub.send(message)
        
        assert len(hub._message_history) == 1
        assert hub._message_queue.qsize() == 1
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self, hub):
        """Test broadcasting a message."""
        await hub.broadcast(
            sender="agent-1",
            subject="Announcement",
            content="Team meeting at 3pm",
        )
        
        assert len(hub._message_history) == 1
        assert hub._message_history[0].recipient == "broadcast"
    
    def test_get_history(self, hub):
        """Test getting message history."""
        # Empty history
        history = hub.get_history()
        assert len(history) == 0
        
        # Add message to history
        message = AgentMessage(
            type=MessageType.NOTIFICATION,
            sender="agent-1",
            recipient="agent-2",
            subject="Test",
            content="Hello",
        )
        hub._message_history.append(message)
        
        history = hub.get_history()
        assert len(history) == 1
    
    def test_get_history_with_filter(self, hub):
        """Test getting filtered history."""
        # Add messages
        msg1 = AgentMessage(
            type=MessageType.REQUEST,
            sender="agent-1",
            recipient="agent-2",
            subject="Request",
            content="test",
        )
        msg2 = AgentMessage(
            type=MessageType.NOTIFICATION,
            sender="agent-2",
            recipient="agent-1",
            subject="Notify",
            content="test",
        )
        hub._message_history.extend([msg1, msg2])
        
        # Filter by agent
        history = hub.get_history(agent_id="agent-1")
        assert len(history) == 2
        
        # Filter by type
        history = hub.get_history(message_type=MessageType.REQUEST)
        assert len(history) == 1


class TestVotingConsensus:
    """Tests for VotingConsensus."""

    def test_majority_approval(self):
        """Test majority voting approval."""
        strategy = VotingConsensus(threshold=0.5)
        
        decision = Decision(
            subject="Test Decision",
            description="Test",
            proposer="agent-1",
            voters=["agent-1", "agent-2", "agent-3"],
            votes=[
                Vote(voter_id="agent-1", decision_id="test", choice="approve"),
                Vote(voter_id="agent-2", decision_id="test", choice="approve"),
                Vote(voter_id="agent-3", decision_id="test", choice="reject"),
            ],
        )
        
        status, result = strategy.evaluate(decision)
        
        assert status == DecisionStatus.APPROVED
        assert result == "approve"
    
    def test_majority_rejection(self):
        """Test majority voting rejection."""
        strategy = VotingConsensus(threshold=0.5)
        
        decision = Decision(
            subject="Test Decision",
            description="Test",
            proposer="agent-1",
            voters=["agent-1", "agent-2", "agent-3"],
            votes=[
                Vote(voter_id="agent-1", decision_id="test", choice="approve"),
                Vote(voter_id="agent-2", decision_id="test", choice="reject"),
                Vote(voter_id="agent-3", decision_id="test", choice="reject"),
            ],
        )
        
        status, result = strategy.evaluate(decision)
        
        assert status == DecisionStatus.REJECTED
        assert result == "reject"
    
    def test_pending_no_votes(self):
        """Test pending when no votes."""
        strategy = VotingConsensus()
        
        decision = Decision(
            subject="Test",
            description="Test",
            proposer="agent-1",
        )
        
        status, result = strategy.evaluate(decision)
        
        assert status == DecisionStatus.PENDING
        assert result is None
    
    def test_is_complete_all_votes(self):
        """Test is_complete when all votes in."""
        strategy = VotingConsensus(require_all_votes=True)
        
        decision = Decision(
            subject="Test",
            description="Test",
            proposer="agent-1",
            voters=["agent-1", "agent-2"],
            votes=[
                Vote(voter_id="agent-1", decision_id="test", choice="approve"),
                Vote(voter_id="agent-2", decision_id="test", choice="approve"),
            ],
        )
        
        assert strategy.is_complete(decision) is True
    
    def test_is_not_complete_missing_votes(self):
        """Test is_complete when votes missing."""
        strategy = VotingConsensus(require_all_votes=True)
        
        decision = Decision(
            subject="Test",
            description="Test",
            proposer="agent-1",
            voters=["agent-1", "agent-2"],
            votes=[
                Vote(voter_id="agent-1", decision_id="test", choice="approve"),
            ],
        )
        
        assert strategy.is_complete(decision) is False


class TestLeaderConsensus:
    """Tests for LeaderConsensus."""

    def test_leader_approval(self):
        """Test leader approves."""
        strategy = LeaderConsensus(leader_id="leader")
        
        decision = Decision(
            subject="Test",
            description="Test",
            proposer="agent-1",
            voters=["leader", "agent-2"],
            votes=[
                Vote(voter_id="agent-2", decision_id="test", choice="reject"),
                Vote(voter_id="leader", decision_id="test", choice="approve"),
            ],
        )
        
        status, result = strategy.evaluate(decision)
        
        assert status == DecisionStatus.APPROVED
        assert result == "approve"
    
    def test_leader_rejection(self):
        """Test leader rejects."""
        strategy = LeaderConsensus(leader_id="leader")
        
        decision = Decision(
            subject="Test",
            description="Test",
            proposer="agent-1",
            votes=[
                Vote(voter_id="leader", decision_id="test", choice="reject"),
            ],
        )
        
        status, result = strategy.evaluate(decision)
        
        assert status == DecisionStatus.REJECTED
        assert result == "reject"
    
    def test_waiting_for_leader(self):
        """Test waiting for leader vote."""
        strategy = LeaderConsensus(leader_id="leader")
        
        decision = Decision(
            subject="Test",
            description="Test",
            proposer="agent-1",
            votes=[
                Vote(voter_id="agent-2", decision_id="test", choice="approve"),
            ],
        )
        
        status, result = strategy.evaluate(decision)
        
        assert status == DecisionStatus.VOTING
        assert result is None


class TestWeightedConsensus:
    """Tests for WeightedConsensus."""

    def test_weighted_approval(self):
        """Test weighted voting approval."""
        weights = {"senior": 2.0, "junior": 1.0}
        strategy = WeightedConsensus(weights=weights, threshold=0.5)
        
        decision = Decision(
            subject="Test",
            description="Test",
            proposer="agent",
            voters=["senior", "junior"],
            votes=[
                Vote(voter_id="senior", decision_id="test", choice="approve"),
                Vote(voter_id="junior", decision_id="test", choice="reject"),
            ],
        )
        
        status, result = strategy.evaluate(decision)
        
        # Senior (2.0) > Junior (1.0), approval rate = 2/3 = 0.67
        assert status == DecisionStatus.APPROVED
        assert result == "approve"
    
    def test_weighted_rejection(self):
        """Test weighted voting rejection."""
        weights = {"senior": 2.0, "junior": 1.0}
        strategy = WeightedConsensus(weights=weights, threshold=0.5)
        
        decision = Decision(
            subject="Test",
            description="Test",
            proposer="agent",
            voters=["senior", "junior"],
            votes=[
                Vote(voter_id="senior", decision_id="test", choice="reject"),
                Vote(voter_id="junior", decision_id="test", choice="approve"),
            ],
        )
        
        status, result = strategy.evaluate(decision)
        
        # Senior reject (2.0) vs Junior approve (1.0), approval rate = 1/3 = 0.33
        assert status == DecisionStatus.REJECTED
        assert result == "reject"


class TestConsensusManager:
    """Tests for ConsensusManager."""

    @pytest.fixture
    def manager(self):
        """Create manager fixture."""
        return ConsensusManager()
    
    def test_create_decision(self, manager):
        """Test creating a decision."""
        decision = manager.create_decision(
            subject="Feature X",
            description="Should we implement Feature X?",
            proposer="pm-agent",
            voters=["architect", "backend", "frontend"],
        )
        
        assert decision.subject == "Feature X"
        assert decision.proposer == "pm-agent"
        assert len(decision.voters) == 3
        assert decision.status == DecisionStatus.PENDING
    
    def test_vote_on_decision(self, manager):
        """Test voting on a decision."""
        decision = manager.create_decision(
            subject="Test",
            description="Test decision",
            proposer="agent-1",
            voters=["agent-1", "agent-2"],
        )
        
        vote = manager.vote(
            decision_id=decision.id,
            voter_id="agent-1",
            choice="approve",
            reasoning="Looks good",
        )
        
        assert vote.choice == "approve"
        assert vote.reasoning == "Looks good"
        assert len(decision.votes) == 1
    
    def test_vote_unauthorized(self, manager):
        """Test voting when not authorized."""
        decision = manager.create_decision(
            subject="Test",
            description="Test",
            proposer="agent-1",
            voters=["agent-1", "agent-2"],
        )
        
        with pytest.raises(ValueError, match="not authorized"):
            manager.vote(
                decision_id=decision.id,
                voter_id="unauthorized-agent",
                choice="approve",
            )
    
    def test_vote_decision_not_found(self, manager):
        """Test voting on non-existent decision."""
        with pytest.raises(ValueError, match="not found"):
            manager.vote(
                decision_id="non-existent",
                voter_id="agent-1",
                choice="approve",
            )
    
    def test_get_pending_decisions(self, manager):
        """Test getting pending decisions."""
        # Create two decisions
        decision1 = manager.create_decision(
            subject="Decision 1",
            description="Test",
            proposer="agent-1",
            voters=["agent-1", "agent-2"],
        )
        decision2 = manager.create_decision(
            subject="Decision 2",
            description="Test",
            proposer="agent-1",
            voters=["agent-1", "agent-2"],
        )
        
        # Vote on decision 1 as agent-1
        manager.vote(decision1.id, "agent-1", "approve")
        
        # Get pending for agent-1 (should only be decision 2)
        pending = manager.get_pending_decisions("agent-1")
        assert len(pending) == 1
        assert pending[0].id == decision2.id
        
        # Get pending for agent-2 (should be both)
        pending = manager.get_pending_decisions("agent-2")
        assert len(pending) == 2
    
    def test_full_consensus_flow(self, manager):
        """Test complete consensus flow."""
        decision = manager.create_decision(
            subject="Deploy to Production",
            description="Ready for production deployment?",
            proposer="pm",
            voters=["architect", "backend", "qa"],
        )
        
        # All approve
        manager.vote(decision.id, "architect", "approve")
        manager.vote(decision.id, "backend", "approve")
        manager.vote(decision.id, "qa", "approve")
        
        # Check final status
        final = manager.get_decision(decision.id)
        assert final.status == DecisionStatus.APPROVED
        assert final.result == "approve"
        assert final.decided_at is not None
