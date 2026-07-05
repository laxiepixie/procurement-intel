from pydantic import BaseModel
from typing import List, Dict, Any

class LeakageReport(BaseModel):
    status: str
    total_leaks_found: int
    data: List[Dict[str, Any]]