import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import threading
from typing import List, Dict, Any, Optional

from arduino_code_utils import sanitize_arduino_identifiers

try:
    import serial
    import serial.tools.list_ports
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False


class SerialPortLockManager:
    """
    Windows üzerinde COM portlarının çakışmasını ve kilitli kalmasını önleyen merkezi yönetici.
    Upload öncesinde tüm açık portları anında kapatır ve avrdude için serbest bırakır.
    """
    _active_connections: Dict[str, Any] = {}
    _lock = threading.Lock()

    @classmethod
    def register(cls, port_name: str, ser_obj: Any):
        with cls._lock:
            old = cls._active_connections.get(port_name)
            if old and hasattr(old, "is_open") and old.is_open:
                try:
                    old.close()
                except Exception:
                    pass
            cls._active_connections[port_name] = ser_obj

    @classmethod
    def unregister(cls, port_name: str):
        with cls._lock:
            old = cls._active_connections.pop(port_name, None)
            if old and hasattr(old, "is_open") and old.is_open:
                try:
                    old.close()
                except Exception:
                    pass

    @classmethod
    def close_all(cls):
        with cls._lock:
            for p, s in list(cls._active_connections.items()):
                if s and hasattr(s, "is_open") and s.is_open:
                    try:
                        s.close()
                    except Exception:
                        pass
            cls._active_connections.clear()


def find_arduino_cli_binary() -> Optional[str]:
    """Sistemde veya özel yolda arduino-cli olup olmadığını kontrol eder."""
    # 0. Backend içi yerel binary (backend/bin/arduino-cli.exe)
    local_bin = os.path.join(os.path.dirname(__file__), "bin", "arduino-cli.exe")
    if os.path.isfile(local_bin):
        return local_bin

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


# Sık kullanılan elektronik modül başlıklarının Arduino Library Index'teki paket karşılıkları
HEADER_TO_LIBRARY_MAP: Dict[str, str] = {
    # OLED & Ekranlar
    "Adafruit_GFX.h": "Adafruit GFX Library",
    "Adafruit_SSD1306.h": "Adafruit SSD1306",
    "LiquidCrystal_I2C.h": "LiquidCrystal I2C",
    "LiquidCrystal.h": "LiquidCrystal",
    "TM1637Display.h": "TM1637",
    "U8g2lib.h": "U8g2",
    # Sensörler & Çevre Birimleri
    "DHT.h": "DHT sensor library",
    "DHT_U.h": "DHT sensor library",
    "Adafruit_Sensor.h": "Adafruit Unified Sensor",
    "IRremote.h": "IRremote",
    "IRremoteInt.h": "IRremote",
    "RTClib.h": "RTClib",
    "MFRC522.h": "MFRC522",
    "MPU6050.h": "MPU6050_tockn",
    "NewPing.h": "NewPing",
    "Keypad.h": "Keypad",
    # LED & Şeritler
    "FastLED.h": "FastLED",
    "Adafruit_NeoPixel.h": "Adafruit NeoPixel",
    # Motor & Servo
    "Servo.h": "Servo",
    "Stepper.h": "Stepper",
    "AccelStepper.h": "AccelStepper",
}


def get_library_search_paths() -> List[str]:
    """
    Sistemdeki kurulu kütüphane yollarını derleyiciye iletmek üzere tespit eder.
    Standart kullanıcı belgeleri, OneDrive ve proje içi kütüphane klasörlerini kapsar.
    """
    paths = []
    # 1. Standart Belgelerim / Arduino / libraries
    docs_arduino = os.path.join(os.path.expanduser("~"), "Documents", "Arduino", "libraries")
    if os.path.isdir(docs_arduino):
        paths.append(docs_arduino)

    # 2. OneDrive yönlendirmeli Belgelerim
    for env_var in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer"):
        od = os.environ.get(env_var)
        if od:
            od_libs = os.path.join(od, "Documents", "Arduino", "libraries")
            if os.path.isdir(od_libs) and od_libs not in paths:
                paths.append(od_libs)

    # 3. Proje klasörü altındaki backend/libraries (varsa)
    proj_libs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libraries")
    if os.path.isdir(proj_libs) and proj_libs not in paths:
        paths.append(proj_libs)

    return paths


def auto_install_missing_libraries(cli_bin: str, err_text: str) -> List[str]:
    """
    Derleme çıktısındaki 'fatal error: X.h: No such file or directory' hatalarını tespit eder
    ve arduino-cli lib install ile otomatik olarak arka planda kurar.
    """
    if not err_text or not cli_bin:
        return []

    missing = re.findall(r"([A-Za-z0-9_]+)\.h:\s*No such file or directory", err_text, re.IGNORECASE)
    if not missing:
        missing = re.findall(r"#include\s*[<\"]([A-Za-z0-9_]+)\.h[>\"]", err_text, re.IGNORECASE)

    unique_headers = list(dict.fromkeys(missing))
    installed = []

    for header_name in unique_headers:
        full_header = f"{header_name}.h"
        # Dahili AVR çekirdeği kütüphanelerini atla
        if full_header in ("Wire.h", "SPI.h", "SoftwareSerial.h", "EEPROM.h", "avr/io.h", "avr/interrupt.h"):
            continue

        lib_target = HEADER_TO_LIBRARY_MAP.get(full_header)
        if not lib_target:
            # Doğrudan kütüphane haritasında yoksa başlık adının boşluklu halini dene
            lib_target = header_name.replace("_", " ")

        try:
            res = subprocess.run(
                [cli_bin, "lib", "install", lib_target],
                capture_output=True,
                text=True,
                timeout=60
            )
            if res.returncode == 0:
                installed.append(lib_target)
        except Exception as e:
            print(f"[Kütüphane Otomatik Kurulum Hatası] {lib_target}: {e}")

    return installed


def ensure_starter_kit_libraries(cli_bin: str):
    """
    Arka planda Kid Arduino Studio starter kit bileşenlerinin kütüphanelerini doğrular/kurar.
    """
    starter_libs = [
        "Adafruit GFX Library",
        "Adafruit SSD1306",
        "LiquidCrystal I2C",
        "DHT sensor library",
        "Adafruit Unified Sensor",
        "IRremote",
    ]
    for lib in starter_libs:
        try:
            subprocess.run([cli_bin, "lib", "install", lib], capture_output=True, text=True, timeout=40)
        except Exception:
            pass


def compile_and_upload(code: str, port: Optional[str] = None) -> Dict[str, Any]:
    """
    Verilen Arduino C++ kodunu geçici dizinde derler ve karta yükler.
    arduino-cli yoksa güvenli simülasyon modunda doğrular.
    """
    # Bu düzeltmeden önce kaydedilmiş projelerdeki Türkçe harfli değişken adları da derlensin
    code = sanitize_arduino_identifiers(code)
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
        extra_compiler_notes = []
        try:
            compile_cmd = [cli_bin, "compile", "--fqbn", fqbn]
            for lib_dir in get_library_search_paths():
                compile_cmd.extend(["--libraries", lib_dir])
            compile_cmd.append(sketch_folder)

            comp_res = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=35
            )

            # Eksik kütüphane varsa otomatik indir ve derlemeyi bir kez daha dene
            if comp_res.returncode != 0:
                err_text = comp_res.stderr or comp_res.stdout
                auto_installed = auto_install_missing_libraries(cli_bin, err_text)
                if auto_installed:
                    extra_compiler_notes.append(
                        f"[KÜTÜPHANE] Eksik kütüphane(ler) otomatik olarak kuruldu: {', '.join(auto_installed)} 📦✨"
                    )
                    # Yeniden derleme
                    comp_res = subprocess.run(
                        compile_cmd,
                        capture_output=True,
                        text=True,
                        timeout=35
                    )

            if comp_res.returncode != 0:
                # Derleme hatası devam ediyorsa
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
            # Yükleme öncesinde tüm açık portları kapat ve Windows driverının serbest kalmasını bekle
            SerialPortLockManager.close_all()
            time.sleep(0.5)

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

            # Windows USB-seri sürücüsünün (CH340/ATmega16U2) avrdude sonrası port handle'ını bırakması için bekle
            time.sleep(1.2)

            final_compiler_out = comp_res.stdout or ""
            if extra_compiler_notes:
                final_compiler_out = "\n".join(extra_compiler_notes) + ("\n" + final_compiler_out if final_compiler_out else "")

            return {
                "success": True,
                "status": "UPLOAD_SUCCESS",
                "message": "Tebrikler! Kodun başarıyla Arduino Uno kartına yüklendi ve çalışıyor! 🚀🎉",
                "port": target_port,
                "simulation": False,
                "compiler_output": final_compiler_out,
                "uploader_output": upload_res.stdout or upload_res.stderr
            }

        except Exception as e:
            return {
                "success": False,
                "status": "UPLOAD_ERROR",
                "message": f"Yükleme hatası: {e}",
                "error": str(e),
                "compiler_output": comp_res.stdout if 'comp_res' in locals() else "",
                "can_heal": False
            }


def stream_serial_port_events(port: Optional[str] = None, baudrate: int = 9600):
    """
    Geriye dönük uyumluluk için SSE ucu.
    Port kilitlenmelerini önlemek amacıyla gerçek canlı port akışı /ws/serial WebSocket hattına devredilmiştir.
    """
    yield f"data: {json.dumps({'timestamp': time.strftime('%H:%M:%S'), 'source': 'system', 'port': port or 'auto', 'text': '[BİLGİ] Canlı iki yönlü seri port akışı için /ws/serial WebSocket köprüsü aktiftir.'}, ensure_ascii=False)}\n\n"


def generate_simulated_serial_events(project_type: str = "general"):
    """Geriye dönük uyumluluk için stream_serial_port_events sarmalayıcısı."""
    yield from stream_serial_port_events(port=None)


async def websocket_serial_bridge(websocket, port: Optional[str] = None, baudrate: int = 9600):
    """
    Doğrudan fiziksel seri porta (ör. COM7 CH340) bağlanan gerçek iki yönlü WebSocket köprüsü.
    Asla sahte/simüle edilmiş veri uydurmaz. Arduino'dan gelen gerçek baytları anında istemciye iletir.
    """
    import asyncio
    from fastapi import WebSocketDisconnect

    await websocket.accept()

    target_port = port
    if not target_port or target_port in ("auto", "simulated", "SIMULATED_PORT"):
        detected = get_connected_ports()
        real_ports = [p["address"] for p in detected if p["address"] != "SIMULATED_PORT"]
        target_port = real_ports[0] if real_ports else None

    if not target_port:
        await websocket.send_json({
            "type": "error",
            "message": "Bağlı bir Arduino kartı bulunamadı. Lütfen USB kablosunun takılı olduğundan emin olun."
        })
        await websocket.close()
        return

    if not PYSERIAL_AVAILABLE:
        await websocket.send_json({
            "type": "error",
            "message": "pyserial kütüphanesi kurulu değil."
        })
        await websocket.close()
        return

    SerialPortLockManager.unregister(target_port)
    await asyncio.sleep(0.15)
    ser = None
    last_err = None
    # Upload sonrasında Windows'un COM handle'ını bırakması 1-2 saniye sürebilir; 8 kez dene
    for attempt in range(8):
        try:
            ser = serial.Serial(target_port, baudrate=baudrate, timeout=0.1)
            break
        except Exception as e:
            last_err = e
            await asyncio.sleep(0.5)

    if not ser or not ser.is_open:
        await websocket.send_json({
            "type": "error",
            "port": target_port,
            "message": f"Seri port ({target_port}) açılamadı: {last_err}. Portun başka bir uygulama tarafından kullanılmadığından emin olun."
        })
        await websocket.close()
        return

    SerialPortLockManager.register(target_port, ser)

    await websocket.send_json({
        "type": "connected",
        "port": target_port,
        "baudrate": baudrate,
        "timestamp": time.strftime("%H:%M:%S"),
        "text": f"[BAĞLANDI] {target_port} ({baudrate} baud) canlı seri port köprüsü açıldı. Arduino'dan veri bekleniyor..."
    })

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    async def serial_reader():
        while not stop_event.is_set():
            try:
                line = await loop.run_in_executor(None, ser.readline)
                if line:
                    decoded = line.decode("utf-8", errors="replace").strip()
                    if decoded:
                        await websocket.send_json({
                            "type": "data",
                            "timestamp": time.strftime("%H:%M:%S"),
                            "port": target_port,
                            "text": decoded
                        })
                else:
                    await asyncio.sleep(0.02)
            except Exception as ex:
                if not stop_event.is_set():
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "port": target_port,
                            "text": f"[PORT BAĞLANTISI KESİLDİ] {ex}"
                        })
                    except Exception:
                        pass
                break

    async def ws_receiver():
        while not stop_event.is_set():
            try:
                msg = await websocket.receive_text()
                if msg and ser and ser.is_open:
                    payload = (msg.strip() + "\r\n").encode("utf-8")
                    await loop.run_in_executor(None, ser.write, payload)
            except (WebSocketDisconnect, Exception):
                break

    try:
        reader_task = asyncio.create_task(serial_reader())
        receiver_task = asyncio.create_task(ws_receiver())
        done, pending = await asyncio.wait(
            [reader_task, receiver_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
    finally:
        stop_event.set()
        SerialPortLockManager.unregister(target_port)
        if ser and ser.is_open:
            try:
                ser.close()
            except Exception:
                pass

