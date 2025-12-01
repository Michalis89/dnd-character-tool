from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator


class ItemType(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    WONDROUS = "wondrous"
    POTION = "potion"
    RING = "ring"
    ROD = "rod"
    SCROLL = "scroll"
    STAFF = "staff"
    WAND = "wand"
    TOOL = "tool"
    AMMUNITION = "ammunition"
    OTHER = "other"


class Rarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    VARIES = "varies"


class DamageDie(BaseModel):
    dice: str = Field(..., description="Dice expression, e.g., '1d8' or '2d6'")
    damage_type: Optional[str] = Field(
        None, description="Type of damage, e.g., 'slashing'"
    )

    @validator("dice")
    def validate_dice(cls, v: str) -> str:
        if "d" not in v:
            raise ValueError("dice must be a dice expression like '1d8'")
        return v


class Cost(BaseModel):
    cp: int = 0
    sp: int = 0
    ep: int = 0
    gp: int = 0
    pp: int = 0

    def total_cp(self) -> int:
        return self.cp + self.sp * 10 + self.ep * 50 + self.gp * 100 + self.pp * 1000

    @classmethod
    def from_gp(cls, gp: Union[int, float]) -> "Cost":
        gp_int = int(gp)
        return cls(gp=gp_int)


class ItemBase(BaseModel):
    name: str = Field(..., description="Display name of the item")
    description: Optional[str] = Field(
        None, description="Full description / rules text"
    )
    item_type: ItemType = Field(ItemType.OTHER)
    rarity: Optional[Rarity] = Field(None)
    weight: Optional[float] = Field(None, description="Weight in pounds")
    cost: Optional[Cost] = None
    attunement: Optional[bool] = Field(
        False, description="Whether the item requires attunement"
    )
    consumable: Optional[bool] = Field(
        False, description="Whether the item is consumed on use"
    )
    properties: List[str] = Field(
        default_factory=list,
        description="Arbitrary properties, e.g., 'light', 'finesse'",
    )

    def is_magic(self) -> bool:
        return self.rarity is not None and self.rarity != Rarity.COMMON

    def is_consumable(self) -> bool:
        return bool(self.consumable)


class Weapon(ItemBase):
    item_type: ItemType = Field(ItemType.WEAPON, const=True)
    damage: Optional[DamageDie] = None
    damage_two_handed: Optional[DamageDie] = None
    range_normal: Optional[int] = None
    range_long: Optional[int] = None
    versatile_damage: Optional[DamageDie] = None


class Armor(ItemBase):
    item_type: ItemType = Field(ItemType.ARMOR, const=True)
    armor_class: Optional[int] = None
    strength_requirement: Optional[int] = None
    stealth_disadvantage: Optional[bool] = None


class Consumable(ItemBase):
    item_type: ItemType = Field(ItemType.POTION, const=True)
    uses: Optional[int] = Field(1, description="Number of uses before item is consumed")
    effect: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rarity: Optional[Rarity] = None
    weight: Optional[float] = None
    cost: Optional[Cost] = None
    attunement: Optional[bool] = None
    consumable: Optional[bool] = None
    properties: Optional[List[str]] = None


class ItemOut(ItemBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True
