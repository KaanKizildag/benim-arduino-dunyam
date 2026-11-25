import type { CircuitNetlist, NetlistComponent, NetlistConnection } from '../circuit/types';
export type { CircuitNetlist, NetlistComponent, NetlistConnection };

export interface BaglantiAdimi {
  adim_no: number;
  talimat: string;
  ipucu: string;
  kaynak_parca: string;
  kaynak_pin: string;
  hedef_parca: string;
  hedef_pin: string;
  kablo_rengi: string;
  kaynak?: { parca: string; pin: string };
  hedef?: { parca: string; pin: string };
}

export type DusunmeTipi = 'gozlemle' | 'karar_ver' | 'eylem' | string;

export interface DusunmeAdimi {
  adim_no?: number;
  tip: DusunmeTipi;
  baslik: string;
  aciklama: string;
  ikon?: string;
}

export interface AkisAdimi {
  gozlemle: string;
  karar_ver: string;
  evet_sonucu: string;
  hayir_sonucu: string;
}

export type AkisDugumTipi =
  | 'baslangic'
  | 'kurulum'
  | 'oku'
  | 'karar'
  | 'eylem'
  | 'bekle'
  | 'dongu'
  | 'bitis'
  | string;

export interface AkisDugumu {
  id: string;
  tip: AkisDugumTipi;
  metin: string;
  parcalar: string[];
}

export interface AkisBaglantisi {
  kaynak: string;
  hedef: string;
  etiket?: string | null;
}

export interface AkisDiyagrami {
  dugumler: AkisDugumu[];
  baglantilar: AkisBaglantisi[];
}

export interface PinBindingInfo {
  uno_pin: string;
  component_id: string;
  component_label: string;
  component_type: string;
  pin_name: string;
  via_component?: string | null;
  role: 'INPUT' | 'OUTPUT' | string;
}

export interface LogicVerificationReport {
  is_valid: boolean;
  syntax_ok: boolean;
  pins_matched: boolean;
  flow_complete: boolean;
  auto_repaired?: boolean;
  pin_bindings: PinBindingInfo[];
  checks: string[];
  warnings?: string[];
}

export interface WiringDesignResponse {
  proje_adi: string;
  karsilama_mesaji: string;
  gerekli_parcalar: string[];
  netlist: CircuitNetlist;
  baglanti_adimlari?: BaglantiAdimi[];
  guvenlik_notu?: string;
  pin_bindings?: PinBindingInfo[];
  uyarilar?: string[];
}

export interface LogicDesignResponse {
  akis_adimlari?: AkisAdimi | null;
  akis_diyagrami?: AkisDiyagrami | null;
  arduino_kodu: string;
  verification: LogicVerificationReport;
}

export interface ProjeTasarimi {
  proje_adi: string;
  karsilama_mesaji: string;
  gerekli_parcalar: string[];
  netlist?: CircuitNetlist;
  baglanti_adimlari?: BaglantiAdimi[];
  akis_adimlari?: AkisAdimi | null;
  akis_diyagrami?: AkisDiyagrami | null;
  arduino_kodu: string;
  guvenlik_notu?: string;
  uyarilar?: string[];
  verification?: LogicVerificationReport;
}

export interface SavedProjectEntry {
  id: string;
  created_at: string;
  prompt: string;
  is_preset: boolean;
  badge?: string;
  difficulty?: string;
  project: ProjeTasarimi;
}

export interface AILogEntry {
  id: string;
  timestamp: string;
  stage: string;
  model: string;
  provider: string;
  duration_ms: number;
  status: 'SUCCESS' | 'REPAIRED' | 'FALLBACK' | 'ERROR' | string;
  user_goal: string;
  system_prompt: string;
  user_prompt: string;
  raw_response: string;
  processed_output?: Record<string, any> | null;
  notes: string[];
  prompt_tokens?: number | null;
  completion_tokens?: number | null;
  total_tokens?: number | null;
}

// Geriye dönük uyumluluk takma adı (alias)
export type ProjectResponse = ProjeTasarimi;

export interface InventoryItem {
  id: string;
  name: string;
  icon: string;
  tag: string;
  imageSrc?: string;
  color?: string;
  category?: 'board' | 'light_display' | 'sensor' | 'actuator_sound' | 'passive' | 'custom' | string;
  description?: string;
  isCustom?: boolean;
}

export interface PortInfo {
  address: string;
  label: string;
  board_name: string;
  is_arduino: boolean;
  source: string;
}

export interface UploadResult {
  success: boolean;
  status: string;
  message: string;
  port?: string;
  simulation?: boolean;
  error?: string;
  can_heal?: boolean;
}

export interface ModelOption {
  id: string;
  name: string;
  raw_name?: string;
  provider: 'local' | 'gemini' | 'openai' | 'anthropic';
  category: string;
  badge: string;
}

export type ModelInfo = ModelOption;

export interface ModelsResponse {
  ollama_active: boolean;
  default_model: string;
  local_models: ModelOption[];
  cloud_models: ModelOption[];
  configured_keys: Record<string, boolean>;
}
