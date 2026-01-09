"""Sprint management router with repository integration."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status

from agile_pm.api.dependencies import get_unit_of_work
from agile_pm.storage.repositories.unit_of_work import UnitOfWork
from agile_pm.storage.schemas import (
    SprintCreate, SprintUpdate, SprintResponse, SprintListResponse
)
from agile_pm.observability.tracing import get_tracer

router = APIRouter(prefix="/sprints", tags=["sprints"])
tracer = get_tracer(__name__)


@router.get("", response_model=SprintListResponse)
async def list_sprints(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """List sprints with pagination."""
    with tracer.start_as_current_span("list_sprints"):
        async with uow:
            sprints = await uow.sprints.list(skip=skip, limit=limit)
            total = await uow.sprints.count()
            return SprintListResponse(
                items=sprints,
                total=total,
                skip=skip,
                limit=limit,
            )


@router.post("", response_model=SprintResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    sprint: SprintCreate,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Create a new sprint."""
    with tracer.start_as_current_span("create_sprint"):
        async with uow:
            db_sprint = await uow.sprints.create(sprint.model_dump())
            await uow.commit()
            return SprintResponse.model_validate(db_sprint)


@router.get("/current", response_model=SprintResponse)
async def get_current_sprint(
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Get the current active sprint."""
    with tracer.start_as_current_span("get_current_sprint"):
        async with uow:
            sprint = await uow.sprints.get_current()
            if not sprint:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active sprint found",
                )
            return SprintResponse.model_validate(sprint)


@router.get("/{sprint_id}", response_model=SprintResponse)
async def get_sprint(
    sprint_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Get sprint by ID."""
    with tracer.start_as_current_span("get_sprint"):
        async with uow:
            sprint = await uow.sprints.get(sprint_id)
            if not sprint:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Sprint {sprint_id} not found",
                )
            return SprintResponse.model_validate(sprint)


@router.patch("/{sprint_id}", response_model=SprintResponse)
async def update_sprint(
    sprint_id: UUID,
    sprint: SprintUpdate,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Update a sprint."""
    with tracer.start_as_current_span("update_sprint"):
        async with uow:
            db_sprint = await uow.sprints.update(
                sprint_id, sprint.model_dump(exclude_unset=True)
            )
            if not db_sprint:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Sprint {sprint_id} not found",
                )
            await uow.commit()
            return SprintResponse.model_validate(db_sprint)
