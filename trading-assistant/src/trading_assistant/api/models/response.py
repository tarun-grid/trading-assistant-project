class ScanResponse(BaseModel):
    results: List[StockResult]
    metadata: Dict[str, Any]