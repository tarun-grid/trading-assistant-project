# src/trading_assistant/commands/persona.py

from typing import Optional
from core.personas import PersonaManager

class PersonaCommand:
    def __init__(self):
        self.persona_manager = PersonaManager()
        
    def execute(self, arg: str = '') -> None:
        """Execute persona command"""
        args = arg.split()
        
        if not args:
            self._show_help()
            return
            
        subcommand = args[0].lower()
        
        if subcommand == 'list':
            self._list_personas()
        elif subcommand == 'set' and len(args) > 1:
            self._set_persona(args[1])
        elif subcommand == 'info' and len(args) > 1:
            self._show_persona_info(args[1])
        elif subcommand == 'active':
            self._show_active_persona()
        else:
            self._show_help()
            
    def _list_personas(self) -> None:
        """Display available trading personas"""
        personas = self.persona_manager.list_personas()
        
        print("\n🎭 Available Trading Personas:")
        print("=" * 40)
        
        for p in personas:
            print(f"\n{p['emoji']} {p['name']}")
            print(f"Risk Tolerance: {p['risk_tolerance']}")
            print(f"Time Horizon: {p['time_horizon']}")
            
    def _set_persona(self, persona_name: str) -> None:
        """Set active trading persona"""
        if self.persona_manager.set_active_persona(persona_name):
            persona = self.persona_manager.get_active_persona()
            print(f"\n{persona.emoji} {persona.get_response('greeting')}")
            print(f"Switched to: {persona.name}")
        else:
            print(f"\n❌ Persona '{persona_name}' not found")
            self._list_personas()
            
    def _show_persona_info(self, persona_name: str) -> None:
        """Show detailed information about a persona"""
        persona = self.persona_manager.get_persona(persona_name)
        
        if not persona:
            print(f"\n❌ Persona '{persona_name}' not found")
            return
            
        print(f"\n{persona.emoji} {persona.name}")
        print("=" * 40)
        
        # Traits
        print("\n💡 Personality Traits:")
        print(f"Risk Tolerance: {persona.traits.risk_tolerance.value}")
        print(f"Time Horizon: {persona.traits.time_horizon.value}")
        print(f"Preferred Sectors: {', '.join(persona.traits.preferred_sectors)}")
        print(f"Sectors to Avoid: {', '.join(persona.traits.avoid_sectors)}")
        print(f"Max Drawdown Tolerance: {persona.traits.max_drawdown_tolerance}%")
        
        # Preferences
        print("\n⚙️ Trading Preferences:")
        print(f"Position Size: {persona.preferences.min_position_size}% - {persona.preferences.max_position_size}%")