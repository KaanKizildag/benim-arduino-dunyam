/**
 * Kid Arduino Studio - Doğrudan Tarayıcıdan Arduino Uno (STK500v1 / Optiboot) Yükleyicisi
 * 
 * Sunucuda derlenen Intel HEX ikili kodunu Web Serial API üzerinden doğrudan
 * kullanıcının bilgisayarına bağlı Arduino Uno (ATmega328P / CH340 / 16U2) kartına yazar.
 * Sunucuda USB bağlantısı gerekmez; istemci tarayıcısı kartı doğrudan programlar.
 */

export interface ParsedHex {
  data: Uint8Array;
  startAddress: number;
  endAddress: number;
}

export type FlashProgressCallback = (current: number, total: number, percent: number) => void;

/**
 * Intel HEX formatındaki metni bayt dizisine dönüştürür.
 */
export function parseIntelHex(hexString: string): ParsedHex {
  const maxFlashSize = 32768; // Arduino Uno (ATmega328P) 32KB
  const buffer = new Uint8Array(maxFlashSize);
  buffer.fill(0xff); // Silinmiş flash varsayılanı 0xFF

  let startAddress = maxFlashSize;
  let endAddress = 0;
  let baseAddress = 0;

  const lines = hexString.split(/\r?\n/);
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed.startsWith(':')) continue;

    const byteCount = parseInt(trimmed.substr(1, 2), 16);
    const address = parseInt(trimmed.substr(3, 4), 16) + baseAddress;
    const recordType = parseInt(trimmed.substr(7, 2), 16);

    if (recordType === 0) {
      // Veri satırı
      for (let i = 0; i < byteCount; i++) {
        const byteVal = parseInt(trimmed.substr(9 + i * 2, 2), 16);
        const targetAddr = address + i;
        if (targetAddr < maxFlashSize) {
          buffer[targetAddr] = byteVal;
          if (targetAddr < startAddress) startAddress = targetAddr;
          if (targetAddr + 1 > endAddress) endAddress = targetAddr + 1;
        }
      }
    } else if (recordType === 1) {
      // Dosya Sonu (EOF)
      break;
    } else if (recordType === 2) {
      // Genişletilmiş Segment Adresi
      baseAddress = parseInt(trimmed.substr(9, 4), 16) << 4;
    } else if (recordType === 4) {
      // Genişletilmiş Doğrusal Adres
      baseAddress = parseInt(trimmed.substr(9, 4), 16) << 16;
    }
  }

  if (startAddress > endAddress) {
    startAddress = 0;
    endAddress = 0;
  }

  return { data: buffer, startAddress, endAddress };
}

/**
 * STK500v1 Protokol İletişim Yöneticisi
 * Gelen baytları dahili bir kuyrukta biriktirir, bayt kaybını ve senkronizasyon kopmasını önler.
 */
class Stk500Communicator {
  private reader: ReadableStreamDefaultReader<Uint8Array>;
  private writer: WritableStreamDefaultWriter<Uint8Array>;
  private buffer: number[] = [];

  constructor(port: any) {
    this.writer = port.writable.getWriter();
    this.reader = port.readable.getReader();
  }

  async send(bytes: number[] | Uint8Array): Promise<void> {
    const data = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
    await this.writer.write(data);
  }

  async readByte(timeoutMs = 1200): Promise<number> {
    if (this.buffer.length > 0) {
      return this.buffer.shift()!;
    }
    const startTime = Date.now();
    while (Date.now() - startTime < timeoutMs) {
      const remaining = Math.max(30, timeoutMs - (Date.now() - startTime));
      let timer: any;
      const timerPromise = new Promise<{ value: undefined; done: boolean }>((res) => {
        timer = setTimeout(() => res({ value: undefined, done: false }), remaining);
      });
      try {
        const { value, done } = await Promise.race([this.reader.read(), timerPromise]);
        clearTimeout(timer);
        if (done && !value) break;
        if (value && value.length > 0) {
          for (let i = 0; i < value.length; i++) {
            this.buffer.push(value[i]);
          }
          if (this.buffer.length > 0) {
            return this.buffer.shift()!;
          }
        }
      } catch {
        clearTimeout(timer);
        break;
      }
    }
    throw new Error('Zaman aşımı: Arduino bootloader yanıt vermedi.');
  }

  /**
   * STK500 senkronizasyon onay baytlarını ([0x14, 0x10] -> STK_INSYNC, STK_OK) bekler.
   */
  async expectSync(timeoutMs = 1000): Promise<boolean> {
    const startTime = Date.now();
    let last = -1;
    while (Date.now() - startTime < timeoutMs) {
      try {
        const b = await this.readByte(250);
        if (last === 0x14 && b === 0x10) {
          return true;
        }
        last = b;
      } catch {
        return false;
      }
    }
    return false;
  }

  async release(): Promise<void> {
    try {
      this.writer.releaseLock();
    } catch {}
    try {
      await this.reader.cancel();
    } catch {}
    try {
      this.reader.releaseLock();
    } catch {}
  }
}

/**
 * Arduino Uno donanımsal RESET darbesi (avrdude standardı: DTR/RTS tetiklemesi)
 */
async function pulseReset(port: any): Promise<void> {
  // 1. DTR'yi çek (LOW seviye ile 100nF kondansatör üzerinden RESET pinini sıfırlar)
  await port.setSignals({ dataTerminalReady: true, requestToSend: true });
  await new Promise((r) => setTimeout(r, 100));
  // 2. DTR'yi bırak (10k pullup pini tekrar HIGH yapar, Optiboot çalışmaya başlar)
  await port.setSignals({ dataTerminalReady: false, requestToSend: false });
  // 3. Optiboot bootloader'ın dinlemeye geçmesi için 50ms bekle (avrdude standardı)
  await new Promise((r) => setTimeout(r, 50));
}

/**
 * Tek bir baud rate hızında STK500 yüklemesini dener.
 */
async function tryFlashAtBaudRate(
  port: any,
  baudRate: number,
  parsed: ParsedHex,
  onProgress?: FlashProgressCallback
): Promise<boolean> {
  // 1. Port açıksa kapat
  if (port.readable || port.writable) {
    try {
      await port.close();
    } catch (e) {
      console.warn(`[Flasher] Önceden açık portu kapatma (${baudRate}):`, e);
    }
    await new Promise((r) => setTimeout(r, 80));
  }

  // 2. Portu belirtilen baud hızında aç
  try {
    await port.open({ baudRate });
  } catch (err: any) {
    console.warn(`[Flasher] Port ${baudRate} hızında açılamadı:`, err);
    return false;
  }

  await pulseReset(port);
  const comm = new Stk500Communicator(port);

  try {
    // 3. Senkronizasyon dene (0x30 = STK_GET_SYNC, 0x20 = CRC_EOP)
    let synced = false;
    for (let attempt = 0; attempt < 14; attempt++) {
      await comm.send([0x30, 0x20]);
      synced = await comm.expectSync(200);
      if (synced) break;
      await new Promise((r) => setTimeout(r, 25));
    }

    if (!synced) {
      return false;
    }

    // 4. Programlama Moduna Gir (0x50 = STK_ENTER_PROGMODE, 0x20 = CRC_EOP)
    await comm.send([0x50, 0x20]);
    const progOk = await comm.expectSync(600);
    if (!progOk) {
      return false;
    }

    // 5. Flash Sayfalarını Yaz (Optiboot ATmega328P sayfa boyutu = 128 bayt)
    const pageSize = 128;
    const totalPages = Math.ceil(parsed.endAddress / pageSize);

    for (let page = 0; page < totalPages; page++) {
      const pageAddr = page * pageSize;
      const wordAddr = Math.floor(pageAddr / 2); // STK500 kelime adresi kullanır

      // A. Adres Yükle (0x55 = STK_LOAD_ADDRESS, low, high, 0x20)
      const addrLow = wordAddr & 0xff;
      const addrHigh = (wordAddr >> 8) & 0xff;
      await comm.send([0x55, addrLow, addrHigh, 0x20]);
      const addrOk = await comm.expectSync(500);
      if (!addrOk) {
        throw new Error(`Flash adresi yüklenemedi (Sayfa: ${page + 1})`);
      }

      // B. 128 Baytlık Sayfayı Yaz (0x64 = STK_PROG_PAGE, sizeH, sizeL, 'F', ...veri..., 0x20)
      const packet = new Uint8Array(4 + pageSize + 1);
      packet[0] = 0x64; // STK_PROG_PAGE
      packet[1] = 0x00; // size High
      packet[2] = 0x80; // size Low (128 bayt)
      packet[3] = 0x46; // 'F' = Flash
      packet.set(parsed.data.subarray(pageAddr, pageAddr + pageSize), 4);
      packet[4 + pageSize] = 0x20; // CRC_EOP

      await comm.send(packet);
      const writeOk = await comm.expectSync(1200);
      if (!writeOk) {
        throw new Error(`Sayfa yazma hatası (Sayfa: ${page + 1}/${totalPages})`);
      }

      if (onProgress) {
        const pct = Math.round(((page + 1) / totalPages) * 100);
        onProgress(page + 1, totalPages, pct);
      }
    }

    // 6. Programlama Modundan Çık (0x51 = STK_LEAVE_PROGMODE, 0x20 = CRC_EOP)
    await comm.send([0x51, 0x20]);
    await comm.expectSync(400);

    return true;
  } finally {
    await comm.release();
    try {
      await port.close();
    } catch {}
  }
}

/**
 * Web Serial portu üzerinden Arduino Uno kartına HEX yüklemesi yapar.
 * Önce standart Optiboot hızı olan 115200 baud ile dener, başarısız olursa 57600 baud ile dener.
 */
export async function flashArduinoUnoWebSerial(
  port: any,
  hexString: string,
  onProgress?: FlashProgressCallback
): Promise<void> {
  const parsed = parseIntelHex(hexString);
  if (parsed.endAddress === 0) {
    throw new Error('Geçerli bir Arduino ikili kodu (HEX) bulunamadı.');
  }

  // 1. Önce standart 115200 baud ile dene
  const success115k = await tryFlashAtBaudRate(port, 115200, parsed, onProgress);
  if (success115k) {
    return;
  }

  // 2. 115200 başarısız olduysa 57600 baud ile dene (eski / bazı klon CH340 bootloader'lar için)
  await new Promise((r) => setTimeout(r, 120));
  const success57k = await tryFlashAtBaudRate(port, 57600, parsed, onProgress);
  if (success57k) {
    return;
  }

  throw new Error("Arduino Uno bootloader senkronizasyonu sağlanamadı. USB kablosunu çıkarıp takmayı veya karta RESET atmayı deneyebilirsiniz.");
}
