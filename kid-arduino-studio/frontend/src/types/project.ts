export interface BaglantiAdimi {
  adim_no: number;
  talimat: string;
  ipucu: string;
  kaynak_parca: string;
  kaynak_pin: string;
  hedef_parca: string;
  hedef_pin: string;
  kablo_rengi: string;
}

export interface AkisAdimi {
  gozlemle: string;
  karar_ver: string;
  evet_sonucu: string;
  hayir_sonucu: string;
}

export interface ProjeTasarimi {
  proje_adi: string;
  karsilama_mesaji: string;
  gerekli_parcalar: string[];
  baglanti_adimlari: BaglantiAdimi[];
  akis_adimlari: AkisAdimi;
  arduino_kodu: string;
  guvenlik_notu?: string;
}

// Geriye dönük uyumluluk takma adı (alias)
export type ProjectResponse = ProjeTasarimi;

export interface InventoryItem {
  id: string;
  name: string;
  icon: string;
  tag: string;
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

export interface ModelsResponse {
  ollama_active: boolean;
  default_model: string;
  local_models: ModelOption[];
  cloud_models: ModelOption[];
  configured_keys: Record<string, boolean>;
}
