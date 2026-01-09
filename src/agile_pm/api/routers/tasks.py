"""Task management router with repository integration."""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status

from agile_pm.api.dependencies import get_unit_of_work
from agile_pm.storage.repositories.unit_of_work import UnitOfWork
from agile_pm.storage.schemas import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
)
from agile_pm.observability.tracing import get_tracer

router = APIRouter(prefix="/tasks", tags=["tasks"])
tracer = get_tracer(__name__)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = None,
    sprint_id: Optional[UUID] = None,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """List tasks with filters."""
    with tracer.start_as_current_span("list_tasks"):
        async with uow:
            tasks = await uow.tasks.list(skip=skip, limit=limit)
            total = await uow.tasks.count()
            return TaskListResponse(
                items=tasks,
                total=total,
                skip=skip,
                limit=limit,
            )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Create a new task."""
    with tracer.start_as_current_span("create_task"):
        async with uow:
            db_task = await uow.tasks.create(task.model_dump())
            await uow.commit()
            return TaskResponse.model_validate(db_task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Get task by ID."""
    with tracer.start_as_current_span("get_task"):
        async with uow:
            task = await uow.tasks.get(task_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task {task_id} not found",
                )
            return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task: TaskUpdate,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Update a task."""
    with tracer.start_as_current_span("update_task"):
        async with uow:
            db_task = await uow.tasks.update(
                task_id, task.model_dump(exclude_unset=True)
            )
            if not db_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task {task_id} not found",
                )
            await uow.commit()
            return TaskResponse.model_validate(db_task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """Delete a task."""
    with tracer.start_as_current_span("delete_task"):
        async with uow:
            deleted = await uow.tasks.delete(task_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task {task_id} not found",
                )
            await uow.commit()
