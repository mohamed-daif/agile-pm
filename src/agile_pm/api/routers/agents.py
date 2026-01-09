"""Agent management router with repository integration."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status

from agile_pm.api.dependencies import get_unit_of_work
from agile_pm.storage.repositories.unit_of_work import UnitOfWork
from agile_pm.storage.schemas import (
    AgentCreate, AgentUpdate, AgentResponse, AgentListResponse
)
from agile_pm.observability.tracing import get_tracer

router = APIRouter(prefix="/agents", tags=["agents"])
tracer = get_tracer(__name__)


@router.get("", response_model=AgentListResponse)
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """List all agents with pagination."""
    with tracer.start_as_current_span("list_agents"):
        async with uow:
            if status:
                agents = await uow.agents.find_by_status(status, skip=skip, limit=limit)
            else:
                agents = await uow.agents.list(skip=skip, limit=limit)
            total = await uow.agents.count()
            return AgentListResponse(
                items=agents,
                total=total,
                skip=skip,
                limit=limit,
            )


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent: AgentCreate,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Create a new agent."""
    with tracer.start_as_current_span("create_agent"):
        async with uow:
            db_agent = await uow.agents.create(agent.model_dump())
            await uow.commit()
            return AgentResponse.model_validate(db_agent)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Get agent by ID."""
    with tracer.start_as_current_span("get_agent"):
        async with uow:
            agent = await uow.agents.get(agent_id)
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent {agent_id} not found",
                )
            return AgentResponse.model_validate(agent)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    agent: AgentUpdate,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Update an agent."""
    with tracer.start_as_current_span("update_agent"):
        async with uow:
            db_agent = await uow.agents.update(
                agent_id, agent.model_dump(exclude_unset=True)
            )
            if not db_agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent {agent_id} not found",
                )
            await uow.commit()
            return AgentResponse.model_validate(db_agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Delete an agent."""
    with tracer.start_as_current_span("delete_agent"):
        async with uow:
            deleted = await uow.agents.delete(agent_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent {agent_id} not found",
                )
            await uow.commit()
