from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import List, Optional, Dict, Any

from ..models.fault_solution import FaultSolution, FaultSolutionComment
from ..models.user import User

class FaultSolutionService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_solutions_for_dtc(self, dtc_code: str, vehicle_make: Optional[str] = None, 
                             vehicle_model: Optional[str] = None, vehicle_year: Optional[int] = None):
        """Get fault solutions for a specific DTC code with optional vehicle filters"""
        query = self.db.query(FaultSolution).filter(FaultSolution.dtc_code == dtc_code)
        
        # Apply vehicle filters if provided
        if vehicle_make:
            query = query.filter(FaultSolution.vehicle_make == vehicle_make)
        if vehicle_model:
            query = query.filter(FaultSolution.vehicle_model == vehicle_model)
        if vehicle_year:
            query = query.filter(FaultSolution.vehicle_year == vehicle_year)
            
        # Order by verified status and votes
        return query.order_by(desc(FaultSolution.is_verified), 
                             desc(FaultSolution.upvotes - FaultSolution.downvotes)).all()
    
    def get_solution_by_id(self, solution_id: int):
        """Get a specific fault solution by ID"""
        return self.db.query(FaultSolution).filter(FaultSolution.id == solution_id).first()
    
    def create_solution(self, user_id: int, data: Dict[str, Any]):
        """Create a new fault solution"""
        solution = FaultSolution(
            user_id=user_id,
            dtc_code=data['dtc_code'],
            title=data['title'],
            description=data['description'],
            steps_to_fix=data['steps_to_fix'],
            estimated_cost=data.get('estimated_cost'),
            tools_required=data.get('tools_required'),
            difficulty_level=data['difficulty_level'],
            time_to_fix=data.get('time_to_fix'),
            vehicle_make=data.get('vehicle_make'),
            vehicle_model=data.get('vehicle_model'),
            vehicle_year=data.get('vehicle_year')
        )
        
        self.db.add(solution)
        self.db.commit()
        self.db.refresh(solution)
        return solution
    
    def update_solution(self, solution_id: int, user_id: int, data: Dict[str, Any]):
        """Update an existing fault solution if user is the owner"""
        solution = self.get_solution_by_id(solution_id)
        if not solution or solution.user_id != user_id:
            return None
            
        for key, value in data.items():
            if hasattr(solution, key):
                setattr(solution, key, value)
                
        self.db.commit()
        self.db.refresh(solution)
        return solution
    
    def vote_solution(self, solution_id: int, user_id: int, is_upvote: bool):
        """Vote on a fault solution"""
        solution = self.get_solution_by_id(solution_id)
        if not solution:
            return None
            
        # In a real app, you'd track user votes to prevent duplicate voting
        if is_upvote:
            solution.upvotes += 1
        else:
            solution.downvotes += 1
            
        self.db.commit()
        return solution
    
    def add_comment(self, solution_id: int, user_id: int, comment_text: str):
        """Add a comment to a fault solution"""
        solution = self.get_solution_by_id(solution_id)
        if not solution:
            return None
            
        comment = FaultSolutionComment(
            solution_id=solution_id,
            user_id=user_id,
            comment=comment_text
        )
        
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment
    
    def search_solutions(self, query: str, limit: int = 20):
        """Search for solutions based on DTC code or title/description"""
        return self.db.query(FaultSolution).filter(
            or_(
                FaultSolution.dtc_code.ilike(f"%{query}%"),
                FaultSolution.title.ilike(f"%{query}%"),
                FaultSolution.description.ilike(f"%{query}%")
            )
        ).order_by(desc(FaultSolution.is_verified)).limit(limit).all()
    
    def verify_solution(self, solution_id: int, admin_id: int):
        """Mark a solution as verified by an admin"""
        solution = self.get_solution_by_id(solution_id)
        if not solution:
            return None
            
        # Check if admin_id is actually an admin (in real app)
        solution.is_verified = True
        self.db.commit()
        self.db.refresh(solution)
        return solution
    
    def get_ai_suggestions(self, dtc_code: str):
        """Get AI-based suggestions from historical repairs"""
        # This would connect to an AI service in a real implementation
        # For now, just return placeholder data
        return {
            "possible_causes": [
                "Faulty oxygen sensor",
                "Loose gas cap",
                "Catalytic converter issue"
            ],
            "common_fixes": [
                "Replace oxygen sensor",
                "Tighten or replace gas cap",
                "Inspect catalytic converter"
            ],
            "average_repair_cost": 150.00,
            "difficulty": 2
        }
