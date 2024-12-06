# command: uvicorn api:app --host localhost --port 8000

import cmd
import sys
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your existing modules
from market_data import MarketData
from commands.scan import ScanCommand
from commands.analyze import AnalyzeCommand
from commands.strategy import StrategyCommand
from commands.backtest import BacktestCommand
from commands.build import BuildCommand
from commands.persona import PersonaCommand
from commands.ai_agent import AITradingAgent
from commands.sophie_agent import SophieAgent
from core.llm_handler import LLMHandler

# Initialize FastAPI app
app = FastAPI(title="Gen-Z Trading Assistant API")

# Initialize dependencies
market_data = MarketData()
llm_handler = LLMHandler(market_data)
scan_cmd = ScanCommand(market_data)
analyze_cmd = AnalyzeCommand(market_data)
strategy_cmd = StrategyCommand(market_data)
backtest_cmd = BacktestCommand(market_data)
build_cmd = BuildCommand(market_data)
persona_cmd = PersonaCommand()
ai_agent = AITradingAgent(market_data)
sophie_agent = SophieAgent(market_data, llm_handler)
        
# Request models
class CommandRequest(BaseModel):
    raw_input: str = None


# Endpoints

@app.get("/")
def home():
    return {"message": "🚀 Welcome to Gen-Z Trading Assistant API!"}

@app.post("/persona")
def switch_persona(request: CommandRequest):
    try:
        # Process through LLM
        response = {"raw_llm_response": "", "structured_params": "", "result": {}}
        
        (raw_llm_response, structured_params) =  llm_handler.process_command(request.raw_input)
        response["raw_llm_response"] = raw_llm_response
        response["structured_params"] = structured_params
        
        persona_cmd.execute(structured_params)
        response["result"] = {"message": "Persona switched successfully."}
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/scan")
def scan_market(request: CommandRequest):
    try:
        # Process through LLM
        response = {"raw_llm_response": "", "structured_params": "", "result": {}}
        
        (raw_llm_response, structured_params) =  llm_handler.process_command(request.raw_input)
        response["raw_llm_response"] = raw_llm_response
        response["structured_params"] = structured_params
        
        result = scan_cmd.execute(structured_params)
        response["result"] = result
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze")
def analyze_stock(request: CommandRequest):
    try:
        # Process through LLM
        response = {"raw_llm_response": "", "structured_params": "", "result": {}}
        
        (raw_llm_response, structured_params) =  llm_handler.process_command(request.raw_input)
        response["raw_llm_response"] = raw_llm_response
        response["structured_params"] = structured_params
        
        result = analyze_cmd.execute(structured_params)
        response["result"] = result
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/strategy")
def load_strategy(request: CommandRequest):
    try:
        # Process through LLM
        response = {"raw_llm_response": "", "structured_params": "", "result": {}}
        
        (raw_llm_response, structured_params) =  llm_handler.process_command(request.raw_input)
        response["raw_llm_response"] = raw_llm_response
        response["structured_params"] = structured_params
        
        result = strategy_cmd.execute(structured_params)
        response["result"] = result
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/build")
def build_strategy(request: CommandRequest):
    try:
        # Process through LLM
        response = {"raw_llm_response": "", "structured_params": "", "result": {}}
        
        (raw_llm_response, structured_params) =  llm_handler.process_command(request.raw_input)
        response["raw_llm_response"] = raw_llm_response
        response["structured_params"] = structured_params
        
        result = build_cmd.execute(structured_params)
        response["result"] = result
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/backtest")
def backtest_strategy(request: CommandRequest):
    try:
        # Process through LLM
        response = {"raw_llm_response": "", "structured_params": "", "result": {}}
        
        (raw_llm_response, structured_params) =  llm_handler.process_command(request.raw_input)
        response["raw_llm_response"] = raw_llm_response
        response["structured_params"] = structured_params
        
        result = backtest_cmd.execute(structured_params)
        response["result"] = result
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/agent")
def ai_trading_agent(request: CommandRequest):
    try:
        # Process through LLM
        response = {"raw_llm_response": "", "structured_params": "", "result": {}}
        
        (raw_llm_response, structured_params) = llm_handler.process_command(request.raw_input)
        response["raw_llm_response"] = raw_llm_response
        response["structured_params"] = structured_params
        
        result = ai_agent.execute(structured_params)
        response["result"] = result
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/sophie")
def sophie(request: CommandRequest):
    try:
        # Process through LLM
        response = {"raw_llm_response": "", "structured_params": "", "result": {}}
        
        (raw_llm_response, structured_params) = llm_handler.process_command(f"/sophie {request.raw_input}", persona="sophie")
        response["raw_llm_response"] = raw_llm_response
        response["structured_params"] = structured_params
        
        result = sophie_agent.execute(request.raw_input, structured_params)
        response["result"] = result
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
