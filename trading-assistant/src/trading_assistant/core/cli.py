import cmd
import sys
import os
import json

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
from commands.sophie_agent import SophieAgent
from core.llm_handler import LLMHandler

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
/sophie   : Use Sophie (The Growth Accelerator)
/help     : Show this help message
/exit     : Exit the program

Type any command to get started!
"""
    prompt = '🤖 trading> '

    def __init__(self):
        super().__init__()
        # Initialize market data
        self.market_data = MarketData()
        
        # Initialize LLM handler
        self.llm_handler = LLMHandler(self.market_data)
        
        # Initialize commands
        self.scan_cmd = ScanCommand(self.market_data)
        self.analyze_cmd = AnalyzeCommand(self.market_data)
        self.strategy_cmd = StrategyCommand(self.market_data)
        self.backtest_cmd = BacktestCommand(self.market_data)
        self.build_cmd = BuildCommand(self.market_data)
        self.persona_cmd = PersonaCommand()
        self.agent = AITradingAgent(self.market_data)
        # Updated Sophie initialization with llm_handler
        self.sophie = SophieAgent(self.market_data, self.llm_handler)  # Pass both parameters    

    def do_sophie(self, arg):
        """Sophie - The Growth Accelerator commands"""
        try:
            if not arg:
                self.sophie.execute()
                return
                
            # Get LLM insights with Sophie's persona
            (raw_llm_response, structured_params) = self.llm_handler.process_command(f"/sophie {arg}", persona="sophie")
            
            # Execute command with LLM insights
            response = self.sophie.execute(arg, structured_params)
            print(json.dumps(response, indent=2))
                
        except Exception as e:
            print(f"🚫 Sophie Command Error: {str(e)}")     

    def _show_sophie_help(self):
        """Show Sophie's help message"""
        print("""
🌟 Sophie - The Growth Accelerator
================================
A dynamic portfolio strategist focusing on high-growth opportunities.

Commands:
---------
/sophie analyze <symbol>     : Get Sophie's growth-focused analysis
/sophie scan                : Find growth opportunities
/sophie build <strategy>    : Create growth-oriented strategy
/sophie backtest <params>   : Test strategy with Sophie's parameters

Examples:
---------
/sophie analyze AAPL        : Analyze Apple's growth potential
/sophie scan growth-tech    : Find high-growth tech opportunities
/sophie build aggressive    : Create aggressive growth strategy
/sophie backtest growth TSLA: Test growth strategy on Tesla
        """)

    def do_agent(self, arg):
        """AI Trading Agent commands"""
        self.agent.execute(arg)
    
    def do_persona(self, arg):
        """Switch between trading personas"""
        self.persona_cmd.execute(arg)

    def precmd(self, line):
        """Pre-process the command to handle natural language through LLM"""
        print(f"Debug: Processing command: {line}")
        if line.startswith('/'):
            try:
                cmd_parts = line.split()
                cmd_type = cmd_parts[0][1:]
                print(f"Debug: Command type: {cmd_type}")
                
                # Special handling for Sophie commands
                if cmd_type == 'sophie':
                    print("Debug: Sophie command detected")
                    # Remove the leading slash for cmd processing
                    return line[1:]
                
                # Process through LLM for other commands
                (raw_llm_response, structured_params) = self.llm_handler.process_command(line)
                
                if structured_params:
                    # Route to appropriate command with structured parameters
                    if cmd_type == 'scan':
                        self.scan_cmd.execute(structured_params)
                    elif cmd_type == 'build':
                        self.build_cmd.execute(structured_params)
                    elif cmd_type == 'analyze':
                        self.analyze_cmd.execute(structured_params)
                    elif cmd_type == 'strategy':
                        self.strategy_cmd.execute(structured_params)
                    elif cmd_type == 'backtest':
                        self.backtest_cmd.execute(structured_params)
                    
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
        # Get active persona for personalized goodbye
        persona_message = ""
        if hasattr(self, 'persona_cmd') and self.persona_cmd.persona_manager.get_active_persona():
            active_persona = self.persona_cmd.persona_manager.get_active_persona()
            persona_message = f"\n{active_persona.emoji} {active_persona.get_response('greeting').replace('ready to', 'done')}"
        
        # Add Sophie's goodbye if she was last used
        if hasattr(self, 'sophie') and self.sophie.was_last_used():
            persona_message += "\n👩‍💼 Sophie: Keep growing and stay strategic! See you next time!"
        
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
            # Clean up resources
            if hasattr(self, 'market_data'):
                self.market_data = None
            if hasattr(self, 'persona_cmd'):
                self.persona_cmd = None
            if hasattr(self, 'sophie'):
                self.sophie = None
                
            print(exit_message)
            
        except Exception as e:
            print("\n👋 Thanks for using Trading Assistant! See you soon!")
            
        return True    

    def default(self, line):
        """Handle unknown commands"""
        print(f"Debug: Reached default with line: {line}")  # Add this debug line
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
    main()