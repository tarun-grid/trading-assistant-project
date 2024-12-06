from datetime import datetime
import json
import os
from typing import Dict, Optional, List

from datetime import datetime
import json
import os
from typing import Dict, Optional, List
from pathlib import Path

class StrategyManager:
    """Manages trading strategies for Sophie"""
    
    def __init__(self, strategies_dir: Optional[str] = None):
        """
        Initialize the strategy manager
        
        Args:
            strategies_dir: Optional directory for storing strategies
        """
        if strategies_dir is None:
            # Get the directory where this file is located
            base_dir = Path(__file__).parent.parent
            self.strategies_dir = base_dir / 'data' / 'strategies'
        else:
            self.strategies_dir = Path(strategies_dir)
            
        # Create directory if it doesn't exist
        self.strategies_dir.mkdir(parents=True, exist_ok=True)
        
        self.strategy_file = self.strategies_dir / 'strategies.json'
        self.strategies = {}
        self._load_existing_strategies()

    def _load_existing_strategies(self) -> None:
        """Load existing strategies from file"""
        try:
            if self.strategy_file.exists():
                with open(self.strategy_file, 'r') as f:
                    self.strategies = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load existing strategies: {e}")
            self.strategies = {}

    def create_strategy(self, name: str, template: Dict) -> Dict:
        """
        Create a new strategy from template with timestamp and validation
        
        Args:
            name: Name for the new strategy
            template: Strategy configuration template
            
        Returns:
            Dict containing the complete strategy configuration
        """
        try:
            # Validate strategy name
            if not name or not isinstance(name, str):
                raise ValueError("Strategy name must be a non-empty string")
                
            # Check for existing strategy
            if name in self.strategies:
                raise ValueError(f"Strategy '{name}' already exists")
                
            # Add metadata
            strategy = template.copy()
            strategy.update({
                'name': name,
                'created_at': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'version': '1.0'
            })
            
            # Validate strategy structure
            self._validate_strategy(strategy)
            
            # Save strategy
            self.strategies[name] = strategy
            self._save_strategies()
            
            return strategy
            
        except Exception as e:
            raise Exception(f"Strategy creation failed: {str(e)}")

    def _validate_strategy(self, strategy: Dict) -> None:
        """
        Validate strategy configuration has all required components
        
        Args:
            strategy: Strategy configuration to validate
            
        Raises:
            ValueError if strategy is invalid
        """
        required_fields = {
            'name': str,
            'risk_profile': str,
            'growth_criteria': dict,
            'technical_rules': dict,
            'position_sizing': dict
        }
        
        for field, field_type in required_fields.items():
            if field not in strategy:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(strategy[field], field_type):
                raise ValueError(f"Invalid type for {field}: expected {field_type}")

    def _load_existing_strategies(self) -> None:
        """Load existing strategies from file"""
        try:
            if os.path.exists(self.strategy_file):
                with open(self.strategy_file, 'r') as f:
                    self.strategies = json.load(f)
                print(f"Loaded {len(self.strategies)} existing strategies")
        except Exception as e:
            print(f"Warning: Could not load existing strategies: {str(e)}")
            self.strategies = {}

    def _save_strategies(self) -> None:
        """Save strategies to persistent storage"""
        try:
            with open(self.strategy_file, 'w') as f:
                json.dump(self.strategies, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save strategies: {str(e)}")

    def get_strategy(self, name: str) -> Optional[Dict]:
        """
        Retrieve a strategy by name
        
        Args:
            name: Name of strategy to retrieve
            
        Returns:
            Strategy configuration or None if not found
        """
        return self.strategies.get(name)

    def list_strategies(self) -> List[str]:
        """Get list of available strategy names"""
        return list(self.strategies.keys())

    def update_strategy(self, name: str, updates: Dict) -> Dict:
        """
        Update an existing strategy
        
        Args:
            name: Name of strategy to update
            updates: Dictionary of updates to apply
            
        Returns:
            Updated strategy configuration
        """
        if name not in self.strategies:
            raise ValueError(f"Strategy '{name}' not found")
            
        strategy = self.strategies[name]
        strategy.update(updates)
        strategy['last_modified'] = datetime.now().isoformat()
        
        self._validate_strategy(strategy)
        self._save_strategies()
        
        return strategy