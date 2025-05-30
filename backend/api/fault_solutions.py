from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..services.fault_solution_service import FaultSolutionService
from ..models.fault_solution import FaultSolution, FaultSolutionComment
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/fault-solutions", tags=["fault-solutions"])

# Pydantic models for request/response
class SolutionCreate(BaseModel):
    dtc_code: str
    title: str
    description: str
    steps_to_fix: str
    estimated_cost: Optional[float] = None
    tools_required: Optional[str] = None
    difficulty_level: int
    time_to_fix: Optional[int] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[int] = None

class SolutionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    steps_to_fix: Optional[str] = None
    estimated_cost: Optional[float] = None
    tools_required: Optional[str] = None
    difficulty_level: Optional[int] = None
    time_to_fix: Optional[int] = None

class CommentCreate(BaseModel):
    comment: str

class VoteAction(BaseModel):
    is_upvote: bool

# Routes
@router.get("/dtc/{dtc_code}")
async def get_solutions_for_dtc(
    dtc_code: str,
    vehicle_make: Optional[str] = None,
    vehicle_model: Optional[str] = None,
    vehicle_year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    service = FaultSolutionService(db)
    solutions = service.get_solutions_for_dtc(dtc_code, vehicle_make, vehicle_model, vehicle_year)
    return {"solutions": solutions}

@router.get("/search")
async def search_solutions(
    query: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    service = FaultSolutionService(db)
    solutions = service.search_solutions(query)
    return {"solutions": solutions}

@router.get("/ai-suggestions/{dtc_code}")
async def get_ai_suggestions(dtc_code: str, db: Session = Depends(get_db)):
    service = FaultSolutionService(db)
    suggestions = service.get_ai_suggestions(dtc_code)
    return suggestions

@router.get("/{solution_id}")
async def get_solution(solution_id: int, db: Session = Depends(get_db)):
    service = FaultSolutionService(db)
    solution = service.get_solution_by_id(solution_id)
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    return solution

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_solution(
    solution: SolutionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = FaultSolutionService(db)
    new_solution = service.create_solution(current_user.id, solution.dict())
    return new_solution

@router.put("/{solution_id}")
async def update_solution(
    solution_id: int,
    solution: SolutionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = FaultSolutionService(db)
    updated_solution = service.update_solution(solution_id, current_user.id, solution.dict(exclude_unset=True))
    if not updated_solution:
        raise HTTPException(
            status_code=404,
            detail="Solution not found or you don't have permission to update it"
        )
    return updated_solution

@router.post("/{solution_id}/vote")
async def vote_on_solution(
    solution_id: int,
    vote: VoteAction,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = FaultSolutionService(db)
    solution = service.vote_solution(solution_id, current_user.id, vote.is_upvote)
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    return {"success": True}

@router.post("/{solution_id}/comments")
async def add_comment(
    solution_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = FaultSolutionService(db)
    new_comment = service.add_comment(solution_id, current_user.id, comment.comment)
    if not new_comment:
        raise HTTPException(status_code=404, detail="Solution not found")
    return new_comment

@router.put("/{solution_id}/verify")
async def verify_solution(
    solution_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # This should check for admin role
):
    service = FaultSolutionService(db)
    solution = service.verify_solution(solution_id, current_user.id)
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")
    return {"success": True}
