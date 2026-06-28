from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Action:
    action: str = "none"
    service: str = ""
    target: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    navigation_path: str = ""
    url_path: str = ""


@dataclass
class GridLayout:
    x: int = 0
    y: int = 0
    width: int = 1
    height: int = 1


@dataclass
class FixedGrid:
    rows: int
    columns: int


@dataclass
class Card:
    type: str
    config: Dict[str, Any] = field(default_factory=dict)
    grid_layout: Optional[GridLayout] = None

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)


@dataclass
class Section:
    type: str = "grid"
    columns: int = 3
    cards: List[Card] = field(default_factory=list)


@dataclass
class View:
    title: str
    path: str
    icon: str = ""
    badges: List[Dict[str, Any]] = field(default_factory=list)
    cards: List[Card] = field(default_factory=list)
    sections: List[Section] = field(default_factory=list)
    type: str = "sections"
    bg_color: str = ""
    bg_image: str = ""
    max_columns: int = 1
    grid: Optional[FixedGrid] = None


@dataclass
class LightdashConfig:
    container_width: str = ""
    container_height: str = ""
    theme: str = "ha-dark"
    auto_revert_seconds: int = 0
    auto_close_modal_seconds: int = 0


@dataclass
class Dashboard:
    title: str = "LightDash"
    views: List[View] = field(default_factory=list)
    lightdash: LightdashConfig = field(default_factory=LightdashConfig)
