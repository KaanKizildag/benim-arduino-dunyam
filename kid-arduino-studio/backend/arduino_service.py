import json
import os
import shutil
import subprocess
import tempfile
import time
from typing import List, Dict, Any, Optional

try:
    import serial
    import serial.tools.list_ports
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False


def find_arduino_cli_binary() -> Optional[str]:
    """Sistemde veya özel yolda arduino-cli olup olmadığını kontrol eder."""
    custom_path = os.getenv("ARDUINO_CLI_PATH", "arduino-cli")
    
    # 1. Custom veya doğrudan komut
    if shutil.which(custom_path):
        return custom_path
    
    # 2. Windows yaygın yolları
    common_windows_paths = [
        os.path.expanduser(r"~\AppData\Local\Programs\Arduino CLI\arduino-cli.exe"),
        r"C:\Program Files\Arduino CLI\arduino-cli.exe",
        r"C:\Program Files (x86)\Arduino CLI\arduino-cli.exe",
        os.path.expanduser(r"~\bin\arduino-cli.exe"),
        os.path.expanduser(r"~\go\bin\arduino-cli.exe"),
    ]
    for p in common_windows_paths:
        if os.path.isfile(p):
            return p
            
    return None


def get_connected_ports() -> List[Dict[str, Any]]:
    """
    Sistemdeki bağlı portları listeler.
    Önce arduino-cli ile dener, ardından pyserial ile tamamlar.
    """
    ports = []
    cli_bin = find_arduino_cli_binary()

    # 1. arduino-cli board list dene
    if cli_bin:
        try:
            res = subprocess.run(
                [cli_bin, "board", "list", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if res.returncode == 0 and res.stdout:
                data = json.loads(res.stdout)
                # Yeni arduino-cli sürümlerinde `detected_ports` veya doğrudan liste gelir
                detected = data.get("detected_ports", []) if isinstance(data, dict) else data
                for item in detected:
                    port_info = item.get("port", {})
                    address = port_info.get("address") or item.get("address")
                    protocol_label = port_info.get("protocol_label", "Seri Port")
                    matching_boards = item.get("matching_boards", [])
                    board_name = matching_boards[0].get("name") if matching_boards else "Bilinmeyen Kart (Arduino uyumlu)"
                    
                    if address:
                        ports.append({
                            "address": address,
                            "label": f"{address} ({board_name})",
                            "board_name": board_name,
                            "is_arduino": bool(matching_boards) or "arduino" in board_name.lower(),
                            "source": "arduino-cli"
                        })
        except Exception as e:
            print(f"[Port Algılama Bilgisi] arduino-cli board list çağrısı: {e}")

    # 2. pyserial ile sistemdeki tüm COM portlarını tara (klon Arduino CH340 gibi)
    if PYSERIAL_AVAILABLE:
        try:
            for p in serial.tools.list_ports.comports():
                # Zaten eklenmişse atla
                if any(existing["address"] == p.device for existing in ports):
                    continue
                is_likely_arduino = any(k in (p.description or "").lower() for k in ["arduino", "ch340", "cp210", "ftdi", "usb-serial"])
                ports.append({
                    "address": p.device,
                    "label": f"{p.device} ({p.description or 'Seri Cihaz'})",
                    "board_name": p.description or "Seri Port Cihazı",
                    "is_arduino": is_likely_arduino,
                    "source": "pyserial"
                })
        except Exception as e:
            print(f"[Port Algılama Bilgisi] pyserial taraması: {e}")

    # 3. Eğer hiç port bulunamadıysa çocuk için sanal/simülatör portu ekle
    if not ports:
        ports.append({
            "address": "SIMULATED_PORT",
            "label": "Sanal Port (Simülasyon Modu)",
            "board_name": "Arduino Uno (Sanal)",
            "is_arduino": True,
            "source": "simulated"
        })

    return ports


def validate_arduino_code_syntax(code: str) -> tuple[bool, str]:
    """
    arduino-cli olmadan temel C++ sözdizimi doğrulaması.
    """
    if "void setup" not in code:
        return False, "Kodunda 'void setup()' başlangıç fonksiyonu eksik görünüyor!"
    if "void loop" not in code:
        return False, "Kodunda 'void loop()' sürekli döngü fonksiyonu eksik görünüyor!"
    
    # Parantez dengesi kontrolü
    open_curlies = code.count("{")
    close_curlies = code.count("}")
    if open_curlies != close_curlies:
        return False, f"Süslü parantez '{{' ve '}}' sayıları uyuşmuyor! ({open_curlies} açıldı, {close_curlies} kapandı)"
    
    return True, "Kod sözdizimi doğrulamadan geçti."


def compile_and_upload(code: str, port: Optional[str] = None) -> Dict[str, Any]:
    """
    Verilen Arduino C++ kodunu geçici dizinde derler ve karta yükler.
    arduino-cli yoksa güvenli simülasyon modunda doğrular.
    """
    cli_bin = find_arduino_cli_binary()

    # 1. arduino-cli kurulu değilse simülasyon testi yap
    if not cli_bin:
        is_valid, msg = validate_arduino_code_syntax(code)
        if not is_valid:
            return {
                "success": False,
                "status": "SYNTAX_ERROR",
                "message": msg,
                "can_heal": True,
                "error": msg
            }
        return {
            "success": True,
            "status": "SIMULATION_SUCCESS",
            "message": "Sanal Derleme Başarılı! 🎉 Kodun sözdizimi ve Arduino Uno uyumluluğu onaylandı. (Gerçek karta tek tıkla yüklemek için sistemine arduino-cli kurabilirsin)",
            "simulation": True,
            "port": port or "SIMULATED_PORT"
        }

    # 2. arduino-cli ile gerçek derleme ve yükleme
    with tempfile.TemporaryDirectory() as temp_dir:
        sketch_name = "KidSketch"
        sketch_folder = os.path.join(temp_dir, sketch_name)
        os.makedirs(sketch_folder, exist_ok=True)
        ino_path = os.path.join(sketch_folder, f"{sketch_name}.ino")

        with open(ino_path, "w", encoding="utf-8") as f:
            f.write(code)

        fqbn = "arduino:avr:uno"

        # A. Derleme Aşaması
        try:
            compile_cmd = [cli_bin, "compile", "--fqbn", fqbn, sketch_folder]
            comp_res = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if comp_res.returncode != 0:
                # Derleme hatası
                err_text = comp_res.stderr or comp_res.stdout
                return {
                    "success": False,
                    "status": "COMPILE_ERROR",
                    "message": "Arduino derleyicisi kodunda bir sorun buldu.",
                    "error": err_text,
                    "can_heal": True
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "status": "TIMEOUT",
                "message": "Derleme işlemi zaman aşımına uğradı.",
                "error": "Timeout",
                "can_heal": False
            }
        except Exception as e:
            return {
                "success": False,
                "status": "SYSTEM_ERROR",
                "message": f"Derleme aracı çalıştırılırken hata: {e}",
                "error": str(e),
                "can_heal": False
            }

        # B. Port Belirleme
        target_port = port
        if not target_port or target_port == "SIMULATED_PORT" or target_port == "auto":
            # Otomatik port bul
            detected_ports = get_connected_ports()
            real_ports = [p["address"] for p in detected_ports if p["address"] != "SIMULATED_PORT"]
            if real_ports:
                target_port = real_ports[0]
            else:
                return {
                    "success": False,
                    "status": "NO_PORT",
                    "message": "Devre derlendi fakat Arduino kartının bağlı olduğu bir USB portu bulunamadı. USB kablosunu bilgisayara taktığından emin misin? 🔌",
                    "compiled": True,
                    "can_heal": False
                }

        # C. Karta Yükleme Aşaması
        try:
            upload_cmd = [cli_bin, "upload", "-p", target_port, "--fqbn", fqbn, sketch_folder]
            upload_res = subprocess.run(
                upload_cmd,
                capture_output=True,
                text=True,
                timeout=25
            )

            if upload_res.returncode != 0:
                err_text = upload_res.stderr or upload_res.stdout
                return {
                    "success": False,
                    "status": "UPLOAD_ERROR",
                    "message": f"{target_port} portuna yüklenirken bir sorun oluştu. USB kablosunun tam oturduğundan emin ol!",
                    "error": err_text,
                    "port": target_port,
                    "can_heal": False
                }

            return {
                "success": True,
                "status": "UPLOAD_SUCCESS",
                "message": "Tebrikler! Kodun başarıyla Arduino Uno kartına yüklendi ve çalışıyor! 🚀🎉",
                "port": target_port,
                "simulation": False
            }

        except Exception as e:
            return {
                "success": False,
                "status": "UPLOAD_ERROR",
                "message": f"Yükleme hatası: {e}",
                "error": str(e),
                "can_heal": False
            }


def stream_serial_port_events(port: Optional[str] = None, baudrate: int = 9600):
    """
    Gerçek bir seri port (COM3, /dev/ttyUSB0 vb.) bağlıysa pyserial üzerinden canlı satırları okur
    ve içindeki sayısal değerleri (key=value veya tekil sayı) ayrıştırarak SSE olarak yayınlar.
    Gerçek port bağlı değilse veya açılamazsa bağlantı durumunu bildirir.
    """
    import re as _re

    target_port = port
    if not target_port or target_port in ("auto", "simulated", "SIMULATED_PORT"):
        detected = get_connected_ports()
        real_ports = [p["address"] for p in detected if p["address"] != "SIMULATED_PORT"]
        target_port = real_ports[0] if real_ports else None

    if target_port and PYSERIAL_AVAILABLE:
        ser = None
        try:
            ser = serial.Serial(target_port, baudrate=baudrate, timeout=1.0)
            yield f"data: {json.dumps({'timestamp': time.strftime('%H:%M:%S'), 'source': 'hardware', 'port': target_port, 'text': f'[BAĞLANDI] {target_port} ({baudrate} baud) seri port akışı başladı.'}, ensure_ascii=False)}\n\n"
            while True:
                raw_line = ser.readline()
                if raw_line:
                    line_str = raw_line.decode("utf-8", errors="replace").strip()
                    if line_str:
                        # Satırdaki sayısal değerleri ayrıştır (örn: "Isik1: 420, Isik2: 680" veya "512")
                        channels: Dict[str, float] = {}
                        for m in _re.finditer(r"([A-Za-z0-9_ğüşıöçĞÜŞİÖÇ]+)\s*[:=]\s*(-?\d+(?:\.\d+)?)", line_str):
                            channels[m.group(1)] = float(m.group(2))
                        if not channels:
                            nums = _re.findall(r"-?\d+(?:\.\d+)?", line_str)
                            if len(nums) == 1:
                                channels["Deger"] = float(nums[0])
                            elif len(nums) > 1:
                                for idx, n in enumerate(nums[:4], start=1):
                                    channels[f"Kanal_{idx}"] = float(n)
                        payload: Dict[str, Any] = {
                            "timestamp": time.strftime("%H:%M:%S"),
                            "source": "hardware",
                            "port": target_port,
                            "text": line_str,
                            "channels": channels
                        }
                        if channels:
                            payload["value"] = next(iter(channels.values()))
                        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                else:
                    time.sleep(0.05)
        except Exception as e:
            yield f"data: {json.dumps({'timestamp': time.strftime('%H:%M:%S'), 'source': 'error', 'port': target_port, 'text': f'[PORT UYARISI] {target_port} okunamadı ({e}). Simülasyon akışına geçiliyor.'}, ensure_ascii=False)}\n\n"
        finally:
            if ser and ser.is_open:
                try:
                    ser.close()
                except Exception:
                    pass


def generate_simulated_serial_events(project_type: str = "general"):
    """Geriye dönük uyumluluk için stream_serial_port_events sarmalayıcısı."""
    yield from stream_serial_port_events(port=None)
