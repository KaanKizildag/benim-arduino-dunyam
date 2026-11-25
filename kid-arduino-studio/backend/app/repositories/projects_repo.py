"""
Repository for managing user-saved Arduino projects.
"""

import json
import os
import time
import uuid
from typing import List, Optional

from schemas import SavedProjectEntry, ProjeTasarimi
from flow_service import legacy_akis_to_diyagram

SAVED_PROJECTS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "saved_projects.json"
)
PRESET_IDS_TO_EXCLUDE = {"gece_lambasi", "park_sensoru", "trafik_isiklari", "buton_servo"}


def get_saved_projects() -> List[SavedProjectEntry]:
    """Returns saved projects created by the user."""
    user_entries: List[SavedProjectEntry] = []

    if os.path.isfile(SAVED_PROJECTS_FILE):
        try:
            with open(SAVED_PROJECTS_FILE, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
            if isinstance(raw_list, list):
                for item in raw_list:
                    try:
                        entry = SavedProjectEntry(**item)
                        if entry.project.akis_diyagrami is None and entry.project.akis_adimlari is not None:
                            comps = (
                                [c.model_dump() for c in entry.project.netlist.components]
                                if entry.project.netlist
                                else []
                            )
                            entry.project.akis_diyagrami = legacy_akis_to_diyagram(
                                entry.project.akis_adimlari.model_dump(), comps
                            )
                        if not entry.is_preset and entry.id not in PRESET_IDS_TO_EXCLUDE:
                            user_entries.append(entry)
                    except Exception:
                        continue
        except Exception as e:
            print(f"[Projelerim] Kayıtlı projeler okunamadı: {e}")

    return user_entries


def save_project_entry(
    project: ProjeTasarimi,
    prompt: str = "",
    project_id: Optional[str] = None,
    badge: str = "AI Tasarımım ✨"
) -> SavedProjectEntry:
    """Saves or updates a project entry."""
    existing = get_saved_projects()
    pid = project_id or f"proj_{int(time.time() * 1000)}_{uuid.uuid4().hex[:4]}"

    new_entry = SavedProjectEntry(
        id=pid,
        created_at=time.strftime("%d.%m.%Y %H:%M"),
        prompt=prompt or project.proje_adi,
        is_preset=False,
        badge=badge,
        difficulty="Özel Kurgu",
        project=project
    )

    updated_user_list = [new_entry] + [e for e in existing if e.id != pid]
    try:
        with open(SAVED_PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump([e.model_dump(by_alias=True) for e in updated_user_list[:50]], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Projelerim] Proje kaydedilemedi: {e}")

    return new_entry


def delete_saved_project(project_id: str) -> bool:
    """Deletes a saved project by ID."""
    existing = get_saved_projects()
    filtered = [e for e in existing if e.id != project_id]
    if len(filtered) == len(existing):
        return False
    try:
        with open(SAVED_PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump([e.model_dump(by_alias=True) for e in filtered], f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
