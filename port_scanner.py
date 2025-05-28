import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

def servis_banner_oku(hedef_ip, port, timeout=1):
    """
    Belirtilen portta çalışan servisin banner bilgisini okur.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((hedef_ip, port))
        
        try:
            banner = sock.recv(1024)
            if banner:
                return banner.decode('utf-8', errors='ignore').strip()
        except:
            pass
        
        if port == 21:
            sock.send(b"USER anonymous\r\n")
            banner = sock.recv(1024)
            return banner.decode('utf-8', errors='ignore').strip()
        elif port == 25:
            sock.send(b"HELO test\r\n")
            banner = sock.recv(1024)
            return banner.decode('utf-8', errors='ignore').strip()
        elif port == 80 or port == 443:
            sock.send(b"GET / HTTP/1.1\r\nHost: " + hedef_ip.encode() + b"\r\n\r\n")
            banner = sock.recv(1024)
            return banner.decode('utf-8', errors='ignore').strip()
        elif port == 22:
            banner = sock.recv(1024)
            return banner.decode('utf-8', errors='ignore').strip()
        elif port == 3306:
            sock.send(b"\x0a")
            banner = sock.recv(1024)
            return banner.decode('utf-8', errors='ignore').strip()
        else:
            try:
                banner = sock.recv(1024)
                if banner:
                    return banner.decode('utf-8', errors='ignore').strip()
            except:
                pass
            
            sock.send(b"\r\n")
            try:
                banner = sock.recv(1024)
                if banner:
                    return banner.decode('utf-8', errors='ignore').strip()
            except:
                pass
        
        return None
    except:
        return None
    finally:
        sock.close()

def port_tara(hedef_ip, port, servisler):
    """
    Belirtilen portu tarar ve servis bilgisini döndürür.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        if sock.connect_ex((hedef_ip, port)) == 0:
            banner = servis_banner_oku(hedef_ip, port)
            servis = servisler.get(port, "Bilinmeyen Servis")
            
            return port, servis, banner
        sock.close()
    except:
        pass
    return None

def port_taramasi(hedef_ip, ports_to_scan, servisler, callback=None):
    """
    Belirtilen portları tarar ve sonuçları callback fonksiyonu ile bildirir.
    """
    acik_portlar = []
    total_ports = len(ports_to_scan)
    processed_ports = 0
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_port = {
            executor.submit(port_tara, hedef_ip, port, servisler): port
            for port in ports_to_scan
        }
        
        for future in as_completed(future_to_port):
            port = future_to_port[future]
            try:
                sonuc = future.result()
                if sonuc:
                    port, servis, banner = sonuc
                    acik_portlar.append((port, servis, banner))
                    if callback:
                        callback(message=f"[+] Port {port}: {servis}")
                        if banner:
                            callback(message=f"    Banner: {banner[:100]}...")
                processed_ports += 1
                
                # İlerleme durumunu güncelle
                if callback:
                    progress = (processed_ports / total_ports) * 100
                    callback(message=None, progress=progress)

            except Exception:
                processed_ports += 1
                if callback:
                    progress = (processed_ports / total_ports) * 100
                    callback(message=None, progress=progress)
                continue
    
    return acik_portlar 