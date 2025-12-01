from typing import Dict, List, Optional
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/characters", tags=["characters"])


def ability_modifier(score: int) -> int:
    return (score - 10) // 2


class Character(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    race: Optional[str] = None
    class_name: Optional[str] = None
    level: int = 1
    hit_die: int = 8  # default hit die if not specified by class
    max_hp: int = 8
    current_hp: int = 8
    ac: int = 10
    stats: Dict[str, int] = Field(
        default_factory=lambda: {
            "str": 10,
            "dex": 10,
            "con": 10,
            "int": 10,
            "wis": 10,
            "cha": 10,
        }
    )
    skills: List[str] = Field(default_factory=list)
    inventory: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

    class Config:
        orm_mode = True

    def level_up(self, hp_gain: Optional[int] = None) -> None:
        """
        Increase level by 1 and increase max_hp by hp_gain or by hit_die + con modifier.
        """
        self.level += 1
        con_mod = ability_modifier(self.stats.get("con", 10))
        if hp_gain is None:
            hp_gain = max(1, self.hit_die + con_mod)
        self.max_hp += hp_gain
        self.current_hp += hp_gain

    def take_damage(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Damage amount must be non-negative")
        self.current_hp = max(0, self.current_hp - amount)

    def heal(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Heal amount must be non-negative")
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def add_item(self, item: str) -> None:
        self.inventory.append(item)

    def remove_item(self, item: str) -> bool:
        try:
            self.inventory.remove(item)
            return True
        except ValueError:
            return False

    def set_stat(self, name: str, value: int) -> None:
        if name not in self.stats:
            raise KeyError(f"Unknown stat: {name}")
        self.stats[name] = value


# In-memory store for example purposes
_characters: Dict[str, Character] = {}


@router.post("/", response_model=Character)
def create_character(payload: Character):
    if payload.id in _characters:
        raise HTTPException(
            status_code=400, detail="Character with this ID already exists"
        )
    _characters[payload.id] = payload
    return payload


@router.get("/{character_id}", response_model=List[Character])
def list_characters():
    return list(_characters.values())


@router.get("/{character_id}", response_model=Character)
def get_character(character_id: str):
    c = _characters.get(character_id)
    if not c:
        raise HTTPException(status_code=404, detail="Character not found")
    return c


@router.post("/{character_id}/level-up", response_model=Character)
def level_up_character(character_id: str):
    c = _characters.get(character_id)
    if not c:
        raise HTTPException(status_code=404, detail="Character not found")
    c.level_up()
    return c


@router.post("/{character_id}/damage", response_model=Character)
def damage_character(character_id: str, amount: int):
    c = _characters.get(character_id)
    if not c:
        raise HTTPException(status_code=404, detail="Character not found")
    try:
        c.take_damage(amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return c


@router.post("/{character_id}/heal", response_model=Character)
def heal_character(character_id: str, amount: int):
    c = _characters.get(character_id)
    if not c:
        raise HTTPException(status_code=404, detail="Character not found")
    try:
        c.heal(amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return c


@router.post("/{character_id}/inventory", response_model=Character)
def add_inventory_item(character_id: str, item: str):
    c = _characters.get(character_id)
    if not c:
        raise HTTPException(status_code=404, detail="Character not found")
    c.add_item(item)
    return c


@router.delete("/{character_id}/inventory", response_model=Character)
def remove_inventory_item(character_id: str, item: str):
    c = _characters.get(character_id)
    if not c:
        raise HTTPException(status_code=404, detail="Character not found")
    removed = c.remove_item(item)
    if not removed:
        raise HTTPException(status_code=404, detail="Item not found in inventory")
    return c
