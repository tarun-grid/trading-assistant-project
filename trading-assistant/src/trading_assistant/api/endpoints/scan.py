@router.post("/scan")
async def scan_markets(request: ScanRequest):
    llm_handler = LLMHandler(market_data)
    params = llm_handler.process_command(request.command)
    results = scan_command.execute(params)
    return ScanResponse(results=results)