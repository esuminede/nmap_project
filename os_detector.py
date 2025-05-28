import os
import platform

def ttl_al(ip):
    """
    Hedef IP'nin TTL değerini alır.
    """
    sistem = platform.system().lower()

    if sistem == "windows":
        komut = f"ping -n 1 {ip}"
    else:
        komut = f"ping -c 1 {ip}"

    try:
        sonuc = os.popen(komut).read()
    except Exception:
        return None

    for satir in sonuc.split("\n"):
        if "ttl=" in satir.lower():
            try:
                ttl = int(satir.lower().split("ttl=")[1].split()[0])
                return ttl
            except:
                return None
    return None

def os_tahmin(ttl):
    """
    TTL değerine göre işletim sistemini tahmin eder.
    """
    if ttl is None:
        return "İşletim sistemi tespit edilemedi."
    elif ttl >= 100 and ttl <= 130:
        return "Windows"
    elif ttl >= 50 and ttl <= 70:
        return "Linux/Unix"
    elif ttl >= 200:
        return "Ağ Cihazı (Cisco, Router, vs)"
    else:
        return "Bilinmeyen sistem"

def os_tespit(ip, callback=None):
    """
    Hedef IP'nin işletim sistemini tespit eder.
    callback fonksiyonu ilerleme durumunu güncellemek için kullanılır.
    """
    if callback:
        callback(message="TTL değeri alınıyor...")
    
    ttl = ttl_al(ip)
    
    if callback:
        callback(message="İşletim sistemi analiz ediliyor...")
    
    if ttl is not None:
        if callback:
            callback(message=f"TTL değeri: {ttl}")
        os_type = os_tahmin(ttl)
        if callback:
            callback(message=f"Tahmini İşletim Sistemi: {os_type}")
        return os_type
    else:
        if callback:
            callback(message="İşletim sistemi tespit edilemedi.")
        return None 