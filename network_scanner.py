import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

def cihaz_tara_paralel(ip, timeout=0.2):
    """
    Belirtilen IP adresindeki cihazı hızlı bir şekilde tarar.
    """
    try:
        # Önce hızlı ping kontrolü
        sonuc = subprocess.run(
            ["ping", "-n", "1", "-w", str(int(timeout*1000)), ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW  # Windows'ta ping penceresini gizle
        )
        if sonuc.returncode == 0:
            return True
            
        # Ping başarısız olursa TCP kontrolü yap
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return any(s.connect_ex((ip, port)) == 0 for port in [80, 443, 8080])
            
    except Exception:
        return False

def yerel_ag_bilgisi():
    """
    Yerel ağ bilgisini tespit eder.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("8.8.8.8", 80))
        yerel_ip = s.getsockname()[0]
        s.close()
        return '.'.join(yerel_ip.split('.')[:-1])
    except Exception:
        return None

def yerel_agdaki_ipler(subnet, callback=None):
    """
    Yerel ağdaki aktif cihazları tarar.
    callback fonksiyonu ilerleme durumunu güncellemek için kullanılır.
    """
    ipler = []
    
    # Önce yaygın IP'leri paralel tara
    yaygin_ipler = [1, 100, 101, 254]  # Router, telefon, bilgisayar IP'leri
    
    total_ips = len(yaygin_ipler) + len([i for i in range(1, 255) if i not in yaygin_ipler])
    processed_ips = 0
    
    if callback:
        callback(message=f"\n{subnet}.0/24 ağında cihazlar aranıyor...")
        callback(message="Yaygın IP'ler taranıyor...")
    
    with ThreadPoolExecutor(max_workers=len(yaygin_ipler)) as executor:
        future_to_ip = {executor.submit(cihaz_tara_paralel, f"{subnet}.{i}"): i for i in yaygin_ipler}
        for future in as_completed(future_to_ip):
            ip = f"{subnet}.{future_to_ip[future]}"
            try:
                if future.result():
                    ipler.append(ip)
                    if callback:
                        callback(message=f"[+] Aktif cihaz bulundu: {ip}")
            except Exception:
                continue
            finally:
                processed_ips += 1
                if callback:
                    progress = (processed_ips / total_ips) * 100
                    callback(message=None, progress=progress)
    
    # Sonra diğer IP'leri daha büyük gruplar halinde tara
    if callback:
        callback(message="Diğer IP'ler taranıyor...")
    
    kalan_ipler = [i for i in range(1, 255) if i not in yaygin_ipler]
    
    # IP'leri daha büyük gruplara böl (her grup 25 IP içersin)
    ip_gruplari = [kalan_ipler[i:i + 25] for i in range(0, len(kalan_ipler), 25)]
    
    for grup in ip_gruplari:
        with ThreadPoolExecutor(max_workers=25) as executor:
            future_to_ip = {executor.submit(cihaz_tara_paralel, f"{subnet}.{i}"): i for i in grup}
            for future in as_completed(future_to_ip):
                ip = f"{subnet}.{future_to_ip[future]}"
                try:
                    if future.result():
                        ipler.append(ip)
                        if callback:
                            callback(message=f"[+] Aktif cihaz bulundu: {ip}")
                except Exception:
                    continue
                finally:
                    processed_ips += 1
                    if callback:
                        progress = (processed_ips / total_ips) * 100
                        callback(message=None, progress=progress)
    
    if not ipler and callback:
        callback(message="\nYerel ağda tespit edilen cihaz yok.")
        callback(message="Öneriler:")
        callback(message="1. Telefonunuzun IP adresini kontrol edin")
        callback(message="2. Farklı bir alt ağ deneyin")
        callback(message="3. Güvenlik duvarı ayarlarınızı kontrol edin")
    
    return ipler 