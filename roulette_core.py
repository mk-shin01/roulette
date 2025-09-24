# -*- coding: utf-8 -*-
import json, os, random
from typing import Dict, List, Optional

def _data_dir() -> str:
    # 사용자별 저장 위치 (Windows/Linux/Mac 공통)
    base = os.path.join(os.path.expanduser("~"), ".roulette")  # 예: C:\Users\YOU\.roulette
    os.makedirs(base, exist_ok=True)
    return base

DATA_FILE = os.path.join(_data_dir(), "roulette_data.json")

DEFAULT_DATA = {
    "menus": [],
    "places": [],
    "menu_weights": {},
    "place_weights": {},
}

class RouletteStore:
    def __init__(self, path: str = DATA_FILE):
        self.path = path
        self._data = None
        self._ensure()

    def _ensure(self):
        if not os.path.exists(self.path):
            self._data = {
                "menus": [],
                "places": [],
                "menu_weights": {},
                "place_weights": {},
            }
            self._save()
        else:
            with open(self.path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        # 키 보정
        for k in DEFAULT_DATA:
            self._data.setdefault(k, DEFAULT_DATA[k] if k.endswith("weights")==False else {})

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def list_menus(self) -> List[str]:
        return list(self._data["menus"])

    def list_places(self) -> List[str]:
        return list(self._data["places"])

    def get_weights(self) -> Dict[str, Dict[str, float]]:
        return {
            "menu_weights": dict(self._data["menu_weights"]),
            "place_weights": dict(self._data["place_weights"]),
        }

    def add_menu(self, name: str, weight: Optional[float] = None):
        name = name.strip()
        if name and name not in self._data["menus"]:
            self._data["menus"].append(name)
        if weight is not None:
            self._data["menu_weights"][name] = float(weight)
        self._save()

    def remove_menu(self, name: str):
        if name in self._data["menus"]:
            self._data["menus"].remove(name)
            self._data["menu_weights"].pop(name, None)
            self._save()

    def add_place(self, name: str, weight: Optional[float] = None):
        name = name.strip()
        if name and name not in self._data["places"]:
            self._data["places"].append(name)
        if weight is not None:
            self._data["place_weights"][name] = float(weight)
        self._save()

    def remove_place(self, name: str):
        if name in self._data["places"]:
            self._data["places"].remove(name)
            self._data["place_weights"].pop(name, None)
            self._save()

    def set_menu_weight(self, name: str, w: float):
        if name not in self._data["menus"]:
            raise ValueError("메뉴가 없습니다. 먼저 추가하세요.")
        self._data["menu_weights"][name] = float(w)
        self._save()

    def set_place_weight(self, name: str, w: float):
        if name not in self._data["places"]:
            raise ValueError("장소가 없습니다. 먼저 추가하세요.")
        self._data["place_weights"][name] = float(w)
        self._save()

    @staticmethod
    def _weighted_choice(items: List[str], weights_map: Dict[str, float]) -> str:
        if not items:
            raise ValueError("항목이 비었습니다.")
        weights = [float(weights_map.get(x, 1.0)) for x in items]
        total = sum(weights)
        if total <= 0:
            weights = [1.0] * len(items)
        return random.choices(items, weights=weights, k=1)[0]

    def spin(self) -> Dict[str, str]:
        menu = self._weighted_choice(self._data["menus"], self._data["menu_weights"])
        place = self._weighted_choice(self._data["places"], self._data["place_weights"])
        return {"menu": menu, "place": place}
