"""The Hollow Pact — AI subsystem."""
from .companion_persona import CompanionPersona, PersonalityVector, HiddenAgenda, LoyaltyStance
from .trust_engine import TrustEngine, TrustState, TrustBand
from .memory_store import MemoryStore
from .orchestrator import ConversationOrchestrator, OrchestratorInput, OrchestratorOutput
from .injection_guard import InjectionGuard
from .summariser import MemorySummariser

__all__ = [
    "CompanionPersona", "PersonalityVector", "HiddenAgenda", "LoyaltyStance",
    "TrustEngine", "TrustState", "TrustBand",
    "MemoryStore",
    "ConversationOrchestrator", "OrchestratorInput", "OrchestratorOutput",
    "InjectionGuard",
    "MemorySummariser",
]
