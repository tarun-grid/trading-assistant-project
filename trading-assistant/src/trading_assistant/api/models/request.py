from pydantic import BaseModel

class ScanRequest(BaseModel):
    command: str