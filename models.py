from dataclasses import dataclass
from datetime import datetime

@dataclass
class Match:
    match_id: str  # or int
    team1: str
    team2: str
    start_time: datetime
    sport: str

@dataclass
class Odd:
    odd_id: str  # or int
    match_id: str  # or int, foreign key to Match
    market_name: str
    outcome: str
    value: float
    is_active: bool
    last_updated: datetime

@dataclass
class Bet:
    bet_id: str  # or int
    user_id: str  # or int
    match_id: str  # or int, foreign key to Match
    odd_id: str  # or int, foreign key to Odd
    stake_amount: float
    potential_winnings: float
    timestamp: datetime
    status: str
