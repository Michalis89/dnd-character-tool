from typing import List, Dict, Optional, Any, Callable
from pydantic import BaseModel, Field
import logging

# /Users/dimitrisl/Projects/dnd-character-tool/backend/routers/class_archetypes.py

logger = logging.getLogger(__name__)


class ArchetypeFeature(BaseModel):
    name: str
    level: int = Field(1, description="Character level when the feature is gained")
    description: Optional[str] = None


class ClassArchetype(BaseModel):
    """
    Data container for a class archetype (subclass). Designed to be imported
    and used by a Character class. The Character class is expected to expose
    simple methods (checked dynamically) to accept added features, proficiencies,
    and spells. If those methods do not exist the archetype will attempt to set
    attributes directly.

    Typical expected character API (not required, presence checked at runtime):
      - add_feature(name: str, description: str, level: int)
      - add_proficiency(proficiency: str)
      - add_spell(spell_name: str, spell_level: int)
      - set_archetype(archetype_name: str)
    """

    id: Optional[str] = None
    name: str
    class_name: str
    description: Optional[str] = None
    features: List[ArchetypeFeature] = Field(default_factory=list)
    proficiencies: List[str] = Field(default_factory=list)
    # spells keyed by character level (or spellcaster level)
    spells: Dict[int, List[str]] = Field(default_factory=dict)
    # choices that require user resolution, e.g. {"skill": ["stealth", "athletics"]}
    choices: Dict[str, List[str]] = Field(default_factory=dict)
    # arbitrary requirements e.g. {"min_level": 3}
    requirements: Optional[Dict[str, Any]] = None

    def meets_requirements(self, character: Any) -> bool:
        if not self.requirements:
            return True
        # Minimal, common requirement checks:
        min_level = self.requirements.get("min_level")
        if min_level is not None:
            char_level = getattr(character, "level", None)
            if char_level is None:
                # try method
                char_level = (
                    character.level()
                    if callable(getattr(character, "level", None))
                    else None
                )
            if char_level is None or char_level < min_level:
                return False
        # Additional checks can be added as needed
        return True

    def apply_to(
        self,
        character: Any,
        up_to_level: Optional[int] = None,
        choices_resolver: Optional[Callable[[str, List[str]], str]] = None,
    ) -> Dict[str, Any]:
        """
        Apply archetype to a character object.
        - character: any object representing a character
        - up_to_level: include features whose feature.level <= up_to_level. If None, applies all features.
        - choices_resolver: optional callable(choice_key, options) -> selected_option
        Returns a dict with keys:
          - applied_features: list of feature names applied
          - missing_choices: dict of choice_key -> options (if resolver not provided or didn't return)
        """
        if not self.meets_requirements(character):
            raise ValueError("Character does not meet archetype requirements")

        result = {"applied_features": [], "missing_choices": {}}

        # mark archetype on character
        if hasattr(character, "set_archetype") and callable(
            getattr(character, "set_archetype")
        ):
            character.set_archetype(self.name)
        else:
            # fallback: set attribute
            setattr(character, "archetype", self.name)

        # add proficiencies
        for prof in self.proficiencies:
            if hasattr(character, "add_proficiency") and callable(
                getattr(character, "add_proficiency")
            ):
                character.add_proficiency(prof)
            else:
                if not hasattr(character, "proficiencies"):
                    setattr(character, "proficiencies", [])
                profs = getattr(character, "proficiencies")
                if prof not in profs:
                    profs.append(prof)

        # add spells
        for spell_level, spells in self.spells.items():
            for spell in spells:
                if hasattr(character, "add_spell") and callable(
                    getattr(character, "add_spell")
                ):
                    character.add_spell(spell, spell_level)
                else:
                    if not hasattr(character, "spells"):
                        setattr(character, "spells", {})
                    spells_dict = getattr(character, "spells")
                    spells_dict.setdefault(spell_level, [])
                    if spell not in spells_dict[spell_level]:
                        spells_dict[spell_level].append(spell)

        # apply features up to level
        for feat in sorted(self.features, key=lambda f: f.level):
            if up_to_level is not None and feat.level > up_to_level:
                continue
            # call preferred character method
            if hasattr(character, "add_feature") and callable(
                getattr(character, "add_feature")
            ):
                character.add_feature(feat.name, feat.description or "", feat.level)
            else:
                # fallback: attach to features list
                if not hasattr(character, "features"):
                    setattr(character, "features", [])
                ch_feats = getattr(character, "features")
                ch_feats.append(
                    {
                        "name": feat.name,
                        "description": feat.description or "",
                        "level": feat.level,
                    }
                )
            result["applied_features"].append(feat.name)

        # resolve choices
        for key, options in self.choices.items():
            selected = None
            if choices_resolver:
                try:
                    selected = choices_resolver(key, options)
                except Exception as e:
                    logger.warning("choices_resolver raised: %s", e)
                    selected = None
            if selected is None:
                # leave the required choices in result for caller to resolve
                result["missing_choices"][key] = options
            else:
                # apply the selected choice as a proficiency or feature depending on key
                # simple heuristics:
                if key.startswith("skill") or key == "skill":
                    if hasattr(character, "add_proficiency") and callable(
                        getattr(character, "add_proficiency")
                    ):
                        character.add_proficiency(selected)
                    else:
                        if not hasattr(character, "proficiencies"):
                            setattr(character, "proficiencies", [])
                        profs = getattr(character, "proficiencies")
                        if selected not in profs:
                            profs.append(selected)
                else:
                    # generic: attach to attributes
                    setattr(character, key, selected)

        return result


class ArchetypeRegistry:
    """
    Simple in-memory registry for archetypes. Useful for lookups in the characters
    module/router.
    """

    def __init__(self):
        self._by_id: Dict[str, ClassArchetype] = {}
        self._by_class: Dict[str, List[ClassArchetype]] = {}

    def register(self, archetype: ClassArchetype) -> None:
        if archetype.id:
            self._by_id[archetype.id] = archetype
        self._by_class.setdefault(archetype.class_name.lower(), []).append(archetype)

    def get_by_id(self, id: str) -> Optional[ClassArchetype]:
        return self._by_id.get(id)

    def list_for_class(self, class_name: str) -> List[ClassArchetype]:
        return list(self._by_class.get(class_name.lower(), []))


# Example archetype registrations (can be removed or extended)
_registry = ArchetypeRegistry()

rogue_thief = ClassArchetype(
    id="rogue_thief",
    name="Thief",
    class_name="Rogue",
    description="Rogues who rely on quick wits and agility, specializing in stealth and sleight of hand.",
    features=[
        ArchetypeFeature(
            name="Fast Hands",
            level=3,
            description="Use the bonus action to make sleight of hand checks.",
        ),
        ArchetypeFeature(
            name="Second-Story Work",
            level=3,
            description="Climbing no longer costs extra movement and adds to jump distance.",
        ),
    ],
    proficiencies=["Thieves' Tools"],
    choices={"skill": ["Sleight of Hand", "Stealth", "Acrobatics"]},
)
_registry.register(rogue_thief)

# Exported items for other modules to import
__all__ = ["ClassArchetype", "ArchetypeFeature", "ArchetypeRegistry", "_registry"]
