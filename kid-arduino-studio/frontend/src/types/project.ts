export interface ConnectionEndpoint {
  parca: string;
  pin: string;
}

export interface BaglantiAdimi {
  adim_no: number;
  talimat: string;
  ipucu: string;
  kaynak: ConnectionEndpoint;
  hedef: ConnectionEndpoint;
  kablo_rengi: string;
}

export type DusunmeTipi = 'BASLANGIC' | 'DONGU' | 'EGER' | 'YAP';

export interface DusunmeAdimi {
  tip: DusunmeTipi;
  baslik: string;
  aciklama: string;
}

export interface ProjectResponse {
  proje_adi: string;
  karsilama_mesaji: string;
  gerekli_parcalar: string[];
  baglanti_adimlari: BaglantiAdimi[];
  dusunme_adimlari: DusunmeAdimi[];
  arduino_kodu: string;
  guvenlik_notu: string;
}

export interface InventoryItem {
  id: string;
  name: string;
  icon: string;
  description: string;
  color: string;
  category: 'board' | 'output' | 'sensor' | 'passive';
  defaultSelected?: boolean;
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
