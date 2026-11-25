/**
 * Composable for managing user saved projects and localStorage offline fallback.
 */

import { ref, type Ref } from 'vue';
import type { SavedProjectEntry, ProjeTasarimi } from '../types/project';
import { api } from '../api/client';

export function useSavedProjects(
  currentProject: Ref<ProjeTasarimi>,
  currentProjectId: Ref<string | null>,
  currentPromptText: Ref<string>,
  currentStep: Ref<number>,
  isProjectsOpen: Ref<boolean>
) {
  const savedProjects = ref<SavedProjectEntry[]>([]);

  async function fetchSavedProjects() {
    try {
      const data = await api.getSavedProjects();
      savedProjects.value = data.filter((p) => !p.is_preset);
      localStorage.setItem('kid_arduino_saved_projects', JSON.stringify(savedProjects.value));
      return;
    } catch {
      // Backend ulaşılamazsa localStorage yedeğinden oku
    }

    try {
      const cached = localStorage.getItem('kid_arduino_saved_projects');
      if (cached) {
        const parsed: SavedProjectEntry[] = JSON.parse(cached);
        savedProjects.value = parsed.filter((p) => !p.is_preset);
        return;
      }
    } catch {
      // ignore
    }

    savedProjects.value = [];
  }

  async function saveCurrentProjectToHistory(promptStr?: string, badgeStr = 'AI Tasarımım ✨') {
    if (!currentProject.value.netlist || currentProject.value.netlist.components.length === 0) {
      return;
    }
    const finalPrompt = promptStr || currentPromptText.value || currentProject.value.proje_adi;
    try {
      const savedEntry = await api.saveProject({
        prompt: finalPrompt,
        badge: badgeStr,
        project: currentProject.value,
      });
      currentProjectId.value = savedEntry.id;
      await fetchSavedProjects();
      return;
    } catch {
      // Offline fallback
    }

    const localEntry: SavedProjectEntry = {
      id: `local_${Date.now()}`,
      created_at: new Date().toLocaleString('tr-TR'),
      prompt: finalPrompt,
      is_preset: false,
      badge: badgeStr,
      difficulty: 'Özel Kurgu',
      project: JSON.parse(JSON.stringify(currentProject.value)),
    };
    savedProjects.value = [localEntry, ...savedProjects.value];
    currentProjectId.value = localEntry.id;
    localStorage.setItem('kid_arduino_saved_projects', JSON.stringify(savedProjects.value));
  }

  async function handleDeleteSavedProject(projectId: string) {
    try {
      await api.deleteProject(projectId);
    } catch {
      // ignore
    }
    savedProjects.value = savedProjects.value.filter((p) => p.id !== projectId);
    localStorage.setItem('kid_arduino_saved_projects', JSON.stringify(savedProjects.value));
  }

  function handleSelectSavedProject(payload: { entry: SavedProjectEntry; targetStep: number }) {
    currentProject.value = JSON.parse(JSON.stringify(payload.entry.project));
    currentProjectId.value = payload.entry.id;
    currentPromptText.value = payload.entry.prompt || payload.entry.project.proje_adi;
    isProjectsOpen.value = false;
    currentStep.value = payload.targetStep;
  }

  return {
    savedProjects,
    fetchSavedProjects,
    saveCurrentProjectToHistory,
    handleDeleteSavedProject,
    handleSelectSavedProject,
  };
}
