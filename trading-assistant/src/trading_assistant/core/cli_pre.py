
import cmd
import sys
import os
import sys
import asyncio

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_data import MarketData
from commands.scan import ScanCommand
from commands.analyze import AnalyzeCommand
from commands.strategy import StrategyCommand
from commands.backtest import BacktestCommand
from commands.build import BuildCommand
from commands.persona import PersonaCommand
from commands.ai_agent import AITradingAgent
from core.llm_handler import LLMHandler

class AsyncCmd(cmd.Cmd):
    """Base class for async command processing"""
    async def cmdloop(self):
        self.preloop()
        try:
            while not self.stop:
                try:
                    line = await self._input('🤖 trading> ')
                    line = await self.precmd(line)
                    stop = await self.onecmd(line)
                    stop = await self.postcmd(stop, line)
                except KeyboardInterrupt:
                    print('^C')
                except Exception as e:
                    print(f'Error: {str(e)}')
        finally:
            self.postloop()

    async def _input(self, prompt):
        return input(prompt)

    async def onecmd(self, line):
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if line == 'EOF':
            self.lastcmd = ''
        if cmd == '':
            return self.default(line)
        else:
            try:
                func = getattr(self, 'do_' + cmd)
            except AttributeError:
                return self.default(line)
            return await func(arg) if asyncio.iscoroutinefunction(func) else func(arg)

class TradingCLI(cmd.Cmd):
    intro = """
🚀 Welcome to Gen-Z Trading Assistant! 🚀

Available Commands:
------------------
/persona  : Switch between trading personas
/scan     : Scan markets with conditions (volume, RSI, MA)
/strategy : Load and customize strategies
/build    : Create new strategies
/analyze  : Get AI analysis
/backtest : Test strategy performance
/agent    : Use AI trading agent
/help     : Show this help message
/exit     : Exit the program

Type any command to get started!
"""
    prompt = '🤖 trading> '

    def __init__(self):
        super().__init__()
        # Initialize market data
        self.market_data = MarketData()
        
        # Initialize commands
        self.scan_cmd = ScanCommand(self.market_data)
        self.analyze_cmd = AnalyzeCommand(self.market_data)
        self.strategy_cmd = StrategyCommand(self.market_data)
        self.backtest_cmd = BacktestCommand(self.market_data)
        self.build_cmd = BuildCommand(self.market_data)
        self.persona_cmd = PersonaCommand()
        self.agent = AITradingAgent(self.market_data)
        

    def do_agent(self, arg):
        """AI Trading Agent commands"""
        self.agent.execute(arg)
    
    def do_persona(self, arg):
        """Switch between trading personas"""
        self.persona_cmd.execute(arg)    

    async def precmd(self, line: str) -> str:
            """Pre-process the command to handle natural language through LLM"""
            if line.startswith('/'):
                try:
                    # Process through LLM
                    structured_params = await self.llm_handler.process_command(line)
                    
                    if structured_params:
                        # Extract command type and remove leading slash
                        cmd_type = line.split()[0][1:]
                        
                        # Route to appropriate command with structured parameters
                        if cmd_type == 'scan':
                            self.scan_cmd.execute(structured_params)
                        elif cmd_type == 'build':
                            self.build_cmd.execute(structured_params)
                        elif cmd_type == 'analyze':
                            self.analyze_cmd.execute(structured_params)
                        # Add other command types as needed
                        
                    return ""  # Prevent default command processing
                except Exception as e:
                    print(f"🚫 Command Processing Error: {str(e)}")
                    return ""
                    
            return line 

    def do_scan(self, arg):
        """Scan markets with conditions"""
        self.scan_cmd.execute(arg)

    def do_analyze(self, arg):
        """Get AI analysis for a stock"""
        self.analyze_cmd.execute(arg)

    def do_strategy(self, arg):
        """Load and customize strategy templates"""
        self.strategy_cmd.execute(arg)

    def do_build(self, arg):
        """Create and manage trading strategies"""
        self.build_cmd.execute(arg)

    def do_backtest(self, arg):
        """Test strategy performance"""
        self.backtest_cmd.execute(arg)

    def do_exit(self, arg):
        """Exit the trading assistant"""
        # Get active persona for personalized goodbye if one is set
        persona_message = ""
        if hasattr(self, 'persona_cmd') and self.persona_cmd.persona_manager.get_active_persona():
            active_persona = self.persona_cmd.persona_manager.get_active_persona()
            persona_message = f"\n{active_persona.emoji} {active_persona.get_response('greeting').replace('ready to', 'done')}"
        
        # Create a styled exit message
        exit_message = f"""
    ╭{'─' * 50}╮
    │{'Goodbye from Trading Assistant!':^50}│
    │{'Thanks for hanging out!':^50}│
    │{'See you on the moon! 🚀':^50}│
    ╰{'─' * 50}╯
    {persona_message}
        """
        
        try:
            # Clean up any resources
            if hasattr(self, 'market_data'):
                self.market_data = None
                
            # Clear any cached data
            if hasattr(self, 'persona_cmd'):
                self.persona_cmd = None
                
            print(exit_message)
            
        except Exception as e:
            # Ensure we exit even if cleanup fails
            print("\n👋 Thanks for using Trading Assistant! See you soon!")
            
        return True    

    def default(self, line):
        """Handle unknown commands"""
        print(f"❌ Unknown command: {line}")
        print("Type '/help' to see available commands")

    def emptyline(self):
        """Handle empty lines"""
        pass

def main():
    try:
        TradingCLI().cmdloop()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using Trading Assistant! See you soon!")
        sys.exit(0)

if __name__ == "__main__":
    try:
        TradingCLI().cmdloop()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using Trading Assistant! See you soon!")
        sys.exit(0)