import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import json
from network_scanner import yerel_ag_bilgisi, yerel_agdaki_ipler
from port_scanner import port_taramasi
from os_detector import os_tespit

class NetworkScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ağ Tarama Aracı")
        self.root.geometry("800x600")
        
        # Servis bilgilerini JSON dosyasından yükle
        try:
            with open('services.json', 'r', encoding='utf-8') as f:
                self.services_data = json.load(f)
                self.servisler = {int(k): v for k, v in self.services_data['services'].items()}
                self.common_ports = self.services_data['common_ports']
        except Exception as e:
            print(f"Servis bilgileri yüklenirken hata: {e}")
            # Varsayılan servis listesi JSON dosyasından al
            try:
                self.servisler = {int(k): v for k, v in self.services_data['fallback']['services'].items()}
                self.common_ports = self.services_data['fallback']['common_ports']
            except:
                # JSON dosyası bile yüklenemezse en temel servisleri kullan
                self.servisler = {80: "HTTP", 443: "HTTPS"}
                self.common_ports = {"web": [80, 443]}
                self.log_message("Kritik hata: Servis bilgileri yüklenemedi!")
        
        # Ana frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Notebook (Tab) oluştur
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Cihaz Tarama Tab'ı
        self.device_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.device_tab, text="Cihaz Tarama")
        self.setup_device_tab()
        
        # Port Tarama Tab'ı
        self.port_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.port_tab, text="Port Tarama")
        self.setup_port_tab()
        
        # İşletim Sistemi Tespiti Tab'ı
        self.os_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.os_tab, text="İşletim Sistemi Tespiti")
        self.setup_os_tab()
        
        # Sonuç alanı
        self.result_text = scrolledtext.ScrolledText(self.main_frame, height=15, width=80)
        self.result_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Çıkış butonu
        self.exit_button = ttk.Button(self.main_frame, text="Çıkış", command=root.quit)
        self.exit_button.grid(row=2, column=0, pady=5)
        
        # Grid yapılandırması
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
    def setup_device_tab(self):
        # IP alt ağı girişi
        ttk.Label(self.device_tab, text="IP Alt Ağı (örn: 192.168.1):").grid(row=0, column=0, padx=5, pady=5)
        self.subnet_entry = ttk.Entry(self.device_tab, width=30)
        self.subnet_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Tarama butonu
        self.scan_device_button = ttk.Button(self.device_tab, text="Cihazları Tara", 
                                           command=self.start_device_scan)
        self.scan_device_button.grid(row=0, column=2, padx=5, pady=5)
        
    def setup_port_tab(self):
        # IP girişi
        ttk.Label(self.port_tab, text="Hedef IP:").grid(row=0, column=0, padx=5, pady=5)
        self.port_ip_entry = ttk.Entry(self.port_tab, width=30)
        self.port_ip_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Port tarama tipi seçimi
        ttk.Label(self.port_tab, text="Tarama Tipi:").grid(row=1, column=0, padx=5, pady=5)
        self.scan_type = tk.StringVar(value="custom")
        scan_frame = ttk.Frame(self.port_tab)
        scan_frame.grid(row=1, column=1, sticky=tk.W)
        
        # Özel port aralığı seçeneği
        ttk.Radiobutton(scan_frame, text="Özel Port Aralığı", 
                       variable=self.scan_type, value="custom",
                       command=self.toggle_port_range).grid(row=0, column=0, padx=5)
        
        # Yaygın port grupları seçeneği
        ttk.Radiobutton(scan_frame, text="Yaygın Port Grupları", 
                       variable=self.scan_type, value="common",
                       command=self.toggle_port_range).grid(row=0, column=1, padx=5)
        
        # Port aralığı frame'i
        self.port_range_frame = ttk.Frame(self.port_tab)
        self.port_range_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Özel port aralığı girişi
        ttk.Label(self.port_range_frame, text="Port Aralığı:").grid(row=0, column=0, padx=5)
        self.start_port_entry = ttk.Entry(self.port_range_frame, width=8)
        self.start_port_entry.insert(0, "1")
        self.start_port_entry.grid(row=0, column=1, padx=2)
        
        ttk.Label(self.port_range_frame, text="-").grid(row=0, column=2)
        
        self.end_port_entry = ttk.Entry(self.port_range_frame, width=8)
        self.end_port_entry.insert(0, "1024")
        self.end_port_entry.grid(row=0, column=3, padx=2)
        
        # Yaygın port grupları seçimi
        self.common_ports_frame = ttk.Frame(self.port_tab)
        self.common_ports_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.common_ports_frame.grid_remove()  # Başlangıçta gizli
        
        ttk.Label(self.common_ports_frame, text="Port Grupları:").grid(row=0, column=0, padx=5)
        self.port_groups = {}
        for i, (group_name, ports) in enumerate(self.common_ports.items()):
            var = tk.BooleanVar()
            self.port_groups[group_name] = (var, ports)
            ttk.Checkbutton(self.common_ports_frame, text=f"{group_name.title()} ({len(ports)} port)",
                           variable=var).grid(row=0, column=i+1, padx=5)
        
        # Tarama butonu
        self.scan_port_button = ttk.Button(self.port_tab, text="Portları Tara", 
                                         command=self.start_port_scan)
        self.scan_port_button.grid(row=3, column=0, columnspan=2, pady=10)
        
    def setup_os_tab(self):
        # IP girişi
        ttk.Label(self.os_tab, text="Hedef IP:").grid(row=0, column=0, padx=5, pady=5)
        self.os_ip_entry = ttk.Entry(self.os_tab, width=30)
        self.os_ip_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Tarama butonu
        self.scan_os_button = ttk.Button(self.os_tab, text="İşletim Sistemini Tespit Et", 
                                       command=self.start_os_scan)
        self.scan_os_button.grid(row=0, column=2, padx=5, pady=5)
    
    def log_message(self, message=None, progress=None):
        """
        Mesajları ve ilerleme durumunu GUI'de gösterir.
        Hem positional hem de keyword argument olarak çağrılabilir.
        """
        if message is not None:
            self.result_text.insert(tk.END, str(message) + "\n")
            self.result_text.see(tk.END)
        
        if progress is not None:
            # Progress bar güncelleme
            if hasattr(self, 'progress_var'):
                self.progress_var.set(progress)
            if hasattr(self, 'progress_label'):
                self.progress_label.config(text=f"%{progress:.1f}")
            self.root.update_idletasks()
    
    def toggle_port_range(self):
        if self.scan_type.get() == "custom":
            self.port_range_frame.grid()
            self.common_ports_frame.grid_remove()
        else:
            self.port_range_frame.grid_remove()
            self.common_ports_frame.grid()

    def get_ports_to_scan(self):
        if self.scan_type.get() == "custom":
            try:
                start_port = int(self.start_port_entry.get())
                end_port = int(self.end_port_entry.get())
                if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
                    raise ValueError("Port numaraları 1-65535 arasında olmalıdır!")
                if start_port > end_port:
                    raise ValueError("Başlangıç portu bitiş portundan büyük olamaz!")
                return list(range(start_port, end_port + 1))
            except ValueError as e:
                self.log_message(f"\nHata: {str(e)}")
                return None
        else:
            # Seçili port gruplarındaki portları topla
            ports_to_scan = set()
            for var, ports in self.port_groups.values():
                if var.get():
                    ports_to_scan.update(ports)
            return sorted(list(ports_to_scan)) if ports_to_scan else None

    def start_device_scan(self):
        def scan():
            self.scan_device_button.state(['disabled'])
            subnet = self.subnet_entry.get()
            self.result_text.delete('1.0', tk.END) # Önceki sonuçları temizle
            
            try:
                # Progress bar için frame oluştur
                progress_frame = ttk.Frame(self.device_tab)
                progress_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
                
                # Progress bar ve yüzde etiketi
                self.progress_var = tk.DoubleVar()
                progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
                progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
                
                self.progress_label = ttk.Label(progress_frame, text="0%")
                self.progress_label.grid(row=0, column=1, padx=5)

                devices = yerel_agdaki_ipler(subnet, callback=self.log_message)
                
                # Progress bar'ı kaldır
                progress_frame.destroy()
                
                if devices:
                    self.log_message(f"\nYerel ağda {len(devices)} aktif cihaz tespit edildi:")
                    for ip in devices:
                        self.log_message(f"- {ip}")
                else:
                    self.log_message("\nYerel ağda tespit edilen cihaz yok.")
                    self.log_message("Öneriler:")
                    self.log_message("1. Telefonunuzun IP adresini kontrol edin")
                    self.log_message("2. Farklı bir alt ağ deneyin")
                    self.log_message("3. Güvenlik duvarı ayarlarınızı kontrol edin")
            except Exception as e:
                self.log_message(f"\nHata: {str(e)}")
            finally:
                self.scan_device_button.state(['!disabled'])
        
        threading.Thread(target=scan, daemon=True).start()

    def start_port_scan(self):
        def scan():
            self.scan_port_button.state(['disabled'])
            ip = self.port_ip_entry.get()
            self.result_text.delete('1.0', tk.END) # Önceki sonuçları temizle
            
            try:
                ports_to_scan = self.get_ports_to_scan()
                if not ports_to_scan:
                    self.log_message("\nLütfen tarama yapılacak portları seçin!")
                    return
                
                # Progress bar için frame oluştur
                progress_frame = ttk.Frame(self.port_tab)
                progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
                
                # Progress bar ve yüzde etiketi
                self.progress_var = tk.DoubleVar()
                progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
                progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
                
                self.progress_label = ttk.Label(progress_frame, text="0%")
                self.progress_label.grid(row=0, column=1, padx=5)
                
                self.log_message(f"\nTarama başlatılıyor: {ip}")
                acik_portlar = port_taramasi(ip, ports_to_scan, self.servisler, callback=self.log_message)
                
                # Progress bar'ı kaldır
                progress_frame.destroy()
                
                self.log_message("\n") # İmleci yeni satıra al
                self.log_message(f"\nTarama tamamlandı: {ip}")
                if acik_portlar:
                    self.log_message("\nAçık Portlar:")
                    for port, servis, banner in acik_portlar:
                        self.log_message(f"Port {port}: {servis}")
                        if banner:
                            self.log_message(f"    Banner: {banner[:100]}...")
                else:
                    self.log_message("Açık port bulunamadı.")
                    
            except Exception as e:
                self.log_message(f"\nHata: {str(e)}")
            finally:
                self.scan_port_button.state(['!disabled'])
        
        threading.Thread(target=scan, daemon=True).start()

    def start_os_scan(self):
        def scan():
            self.scan_os_button.state(['disabled'])
            ip = self.os_ip_entry.get()
            self.result_text.delete('1.0', tk.END) # Önceki sonuçları temizle
            
            try:
                # Progress bar için frame oluştur
                progress_frame = ttk.Frame(self.os_tab)
                progress_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
                
                # Progress bar ve yüzde etiketi
                self.progress_var = tk.DoubleVar()
                progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
                progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
                
                self.progress_label = ttk.Label(progress_frame, text="0%")
                self.progress_label.grid(row=0, column=1, padx=5)
                
                self.log_message(f"\n{ip} adresinin işletim sistemi tespit ediliyor...")
                
                # İlerleme simülasyonu için adımlar
                steps = ["TTL değeri alınıyor...", "İşletim sistemi analiz ediliyor...", "Sonuçlar değerlendiriliyor..."]
                for i, step in enumerate(steps, 1):
                    progress = (i / len(steps)) * 100
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"%{progress:.1f}")
                    self.root.update_idletasks()
                    self.root.after(500)
                
                os_tespit(ip, callback=self.log_message)
                
                # Progress bar'ı kaldır
                progress_frame.destroy()
                
            except Exception as e:
                self.log_message(f"\nHata: {str(e)}")
            finally:
                self.scan_os_button.state(['!disabled'])
        
        threading.Thread(target=scan, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkScannerGUI(root)
    root.mainloop() 