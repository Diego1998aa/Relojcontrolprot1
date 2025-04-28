import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import pandas as pd
import datetime
import time
from PIL import Image, ImageTk
import random

# Configuración inicial
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Archivos de datos
ARCHIVO_USUARIOS = "data/usuarios.xlsx"
ARCHIVO_REGISTROS = "data/registros.xlsx"
ARCHIVO_CONFIG = "data/config.json"

class RelojControlApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("UrbanControl - Reloj Biométrico")
        self.geometry("480x800")
        self.configure_window()
        self.create_widgets()
        self.setup_data()
        
    def configure_window(self):
        """Configura la ventana principal"""
        self.minsize(480, 800)
        self.maxsize(480, 800)
        self.attributes('-alpha', 0.96)
        
    def setup_data(self):
        """Inicializa los archivos de datos necesarios"""
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(ARCHIVO_USUARIOS):
            df = pd.DataFrame(columns=["ID", "Nombre", "Rol", "Huella"])
            df.to_excel(ARCHIVO_USUARIOS, index=False)
            
        if not os.path.exists(ARCHIVO_REGISTROS):
            df = pd.DataFrame(columns=["ID", "Nombre", "Fecha", "Hora", "Tipo", "Metodo"])
            df.to_excel(ARCHIVO_REGISTROS, index=False)
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal con efecto de vidrio
        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color=("gray85", "gray15"))
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Encabezado estilo moderno
        self.header_frame = ctk.CTkFrame(self.main_frame, height=60, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        self.logo_label = ctk.CTkLabel(self.header_frame, text="URBAN CONTROL", 
                                     font=("Arial", 18, "bold"))
        self.logo_label.pack(side="left")
        
        self.time_label = ctk.CTkLabel(self.header_frame, text="", 
                                      font=("Arial", 16))
        self.time_label.pack(side="right")
        self.update_clock()
        
        # Panel de visualización biométrica (simulación de cámara)
        self.camera_frame = ctk.CTkFrame(self.main_frame, height=280, 
                                        corner_radius=15, fg_color="black")
        self.camera_frame.pack(fill="x", padx=20, pady=10)
        
        # Simulación de vista de cámara
        self.camera_display = ctk.CTkLabel(self.camera_frame, text="", 
                                          font=("Arial", 16), text_color="white")
        self.camera_display.pack(expand=True)
        
        # Estado del sistema
        self.status_label = ctk.CTkLabel(self.main_frame, text="Sistema listo", 
                                       font=("Arial", 14), text_color="lightblue")
        self.status_label.pack(pady=5)
        
        # Panel de botones de acción
        self.create_action_buttons()
        
        # Panel de información del usuario
        self.user_frame = ctk.CTkFrame(self.main_frame, height=100, 
                                      corner_radius=10, fg_color=("gray90", "gray10"))
        self.user_frame.pack(fill="x", padx=20, pady=10)
        
        self.user_name = ctk.CTkLabel(self.user_frame, text="No identificado", 
                                     font=("Arial", 16, "bold"))
        self.user_name.pack(pady=5)
        
        self.last_action = ctk.CTkLabel(self.user_frame, text="Última acción: --:--", 
                                       font=("Arial", 12))
        self.last_action.pack()
        
        # Botón de administración
        self.admin_btn = ctk.CTkButton(self.main_frame, text="Modo Admin", 
                                      command=self.open_admin, width=120, 
                                      fg_color="transparent", border_width=1)
        self.admin_btn.pack(pady=10)
        
        # Iniciar animación de la cámara
        self.animate_camera()
    
    def create_action_buttons(self):
        """Crea los botones de acción principales"""
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        # Estilo para los botones
        btn_style = {
            "font": ("Arial", 14, "bold"),
            "height": 50,
            "corner_radius": 12,
            "border_width": 2
        }
        
        # Botón de entrada
        self.entry_btn = ctk.CTkButton(btn_frame, text="ENTRADA", 
                                     command=lambda: self.register_action("Entrada"),
                                     fg_color="#2e7d32", hover_color="#1b5e20",
                                     border_color="#4caf50", **btn_style)
        self.entry_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Botón de colación
        self.break_btn = ctk.CTkButton(btn_frame, text="COLACIÓN", 
                                      command=lambda: self.register_action("Colación"),
                                      fg_color="#ff8f00", hover_color="#ff6f00",
                                      border_color="#ffa000", **btn_style)
        self.break_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Botón de salida
        self.exit_btn = ctk.CTkButton(btn_frame, text="SALIDA", 
                                     command=lambda: self.register_action("Salida"),
                                     fg_color="#c62828", hover_color="#b71c1c",
                                     border_color="#ef5350", **btn_style)
        self.exit_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Botón biométrico
        self.bio_btn = ctk.CTkButton(btn_frame, text="HUELLA", 
                                    command=self.biometric_auth,
                                    fg_color="#1565c0", hover_color="#0d47a1",
                                    border_color="#42a5f5", **btn_style)
        self.bio_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Ajustar columnas
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
    
    def update_clock(self):
        """Actualiza el reloj en tiempo real"""
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=now)
        self.after(1000, self.update_clock)  
    def animate_camera(self):
        """Animación para simular el escaneo biométrico"""
        frames = ["|", "/", "-", "\\"]
        self.camera_frame_index = (self.camera_frame_index + 1) % len(frames) if hasattr(self, 'camera_frame_index') else 0
        self.camera_display.configure(text=f"ESCANEANDO {frames[self.camera_frame_index]}")
        self.after(300, self.animate_camera)
    
    def register_action(self, action_type):
        """Registra una acción de entrada/salida"""
        current_time = datetime.datetime.now()
        
        # Simular usuario (en producción sería el usuario autenticado)
        user_id = "EMP001"
        user_name = "Juan Pérez"
        
        try:
            # Registrar en el archivo
            df = pd.read_excel(ARCHIVO_REGISTROS)
            new_record = pd.DataFrame([[
                user_id,
                user_name,
                current_time.date(),
                current_time.time().strftime('%H:%M:%S'),
                action_type,
                "Manual"
            ]], columns=df.columns)
            
            df = pd.concat([df, new_record], ignore_index=True)
            df.to_excel(ARCHIVO_REGISTROS, index=False)
            
            # Actualizar UI
            self.user_name.configure(text=user_name)
            self.last_action.configure(text=f"Última acción: {action_type} a las {current_time.strftime('%H:%M')}")
            self.status_label.configure(text=f"{action_type} registrada", text_color="lightgreen")
            
            # Mostrar confirmación en la pantalla de cámara
            self.camera_display.configure(text=f"{action_type}\nREGISTRADA", 
                                        font=("Arial", 24, "bold"))
            
            # Resetear después de 3 segundos
            self.after(3000, self.reset_display)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar: {str(e)}")
            self.status_label.configure(text="Error al registrar", text_color="red")
    
    def biometric_auth(self):
        """Simula autenticación biométrica"""
        self.status_label.configure(text="Escaneando huella...", text_color="yellow")
        self.camera_display.configure(text="COLOCA TU DEDO\nEN EL LECTOR", 
                                    font=("Arial", 18))
        
        # Simular tiempo de escaneo
        self.after(2000, self.process_biometric)
    
    def process_biometric(self):
        """Procesa el resultado de la autenticación biométrica"""
        # Simular éxito o fallo aleatorio (en producción sería real)
        if random.random() > 0.2:  # 80% de éxito
            user_id = "EMP001"
            user_name = "Juan Pérez"
            action_type = self.determine_next_action(user_id)
            
            current_time = datetime.datetime.now()
            
            try:
                df = pd.read_excel(ARCHIVO_REGISTROS)
                new_record = pd.DataFrame([[
                    user_id,
                    user_name,
                    current_time.date(),
                    current_time.time().strftime('%H:%M:%S'),
                    action_type,
                    "Huella"
                ]], columns=df.columns)
                
                df = pd.concat([df, new_record], ignore_index=True)
                df.to_excel(ARCHIVO_REGISTROS, index=False)
                
                # Actualizar UI
                self.user_name.configure(text=user_name)
                self.last_action.configure(text=f"Última acción: {action_type} a las {current_time.strftime('%H:%M')}")
                self.status_label.configure(text="Huella verificada", text_color="lightgreen")
                self.camera_display.configure(text=f"{action_type}\nPOR HUELLA", 
                                            font=("Arial", 22, "bold"))
                
            except Exception as e:
                messagebox.showerror("Error", f"Error en registro: {str(e)}")
                self.status_label.configure(text="Error en registro", text_color="red")
        else:
            self.status_label.configure(text="Huella no reconocida", text_color="red")
            self.camera_display.configure(text="HUELLA\nNO RECONOCIDA", 
                                        font=("Arial", 22, "bold"))
        
        # Resetear después de 3 segundos
        self.after(3000, self.reset_display)
    
    def determine_next_action(self, user_id):
        """Determina la siguiente acción basada en el último registro"""
        try:
            df = pd.read_excel(ARCHIVO_REGISTROS)
            user_records = df[df["ID"] == user_id]
            
            if user_records.empty:
                return "Entrada"
                
            last_action = user_records.iloc[-1]["Tipo"]
            
            if last_action == "Entrada":
                return "Colación"
            elif last_action == "Colación":
                return "Salida"
            else:
                return "Entrada"
        except:
            return "Entrada"
    
    def reset_display(self):
        """Restablece la pantalla a su estado inicial"""
        self.camera_display.configure(text="LISTO PARA\nESCANEAR", 
                                    font=("Arial", 18))
        self.status_label.configure(text="Sistema listo", text_color="lightblue")
    
    def open_admin(self):
        """Abre el panel de administración"""
        self.withdraw()
        admin_window = AdminPanel(self)
        admin_window.mainloop()

class AdminPanel(ctk.CTk):
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.title("UrbanControl - Panel de Administración")
        self.geometry("800x600")
        self.create_widgets()
    
    def create_widgets(self):
        """Crea la interfaz del panel de administración"""
        # Frame principal
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Encabezado
        header_frame = ctk.CTkFrame(main_frame, height=60, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(header_frame, text="PANEL DE ADMINISTRACIÓN", 
                    font=("Arial", 20, "bold")).pack(side="left")
        
        back_btn = ctk.CTkButton(header_frame, text="Volver", width=100,
                                command=self.return_to_main)
        back_btn.pack(side="right")
        
        # Panel de pestañas
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña de usuarios
        self.user_tab = self.tabview.add("Usuarios")
        self.setup_user_tab()
        
        # Pestaña de registros
        self.records_tab = self.tabview.add("Registros")
        self.setup_records_tab()
        
        # Pestaña de configuración
        self.config_tab = self.tabview.add("Configuración")
        self.setup_config_tab()
    
    def setup_user_tab(self):
        """Configura la pestaña de gestión de usuarios"""
        # Frame de formulario
        form_frame = ctk.CTkFrame(self.user_tab)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(form_frame, text="Gestión de Usuarios", 
                    font=("Arial", 16)).pack(pady=5)
        
        # Campos del formulario
        self.user_id = ctk.CTkEntry(form_frame, placeholder_text="ID de empleado")
        self.user_id.pack(fill="x", pady=5)
        
        self.user_name = ctk.CTkEntry(form_frame, placeholder_text="Nombre completo")
        self.user_name.pack(fill="x", pady=5)
        
        self.user_role = ctk.CTkOptionMenu(form_frame, values=["Empleado", "Supervisor", "Administrador"])
        self.user_role.pack(fill="x", pady=5)
        
        # Botones de acción
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(btn_frame, text="Agregar", command=self.add_user).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Editar", command=self.edit_user).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Eliminar", command=self.delete_user).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Registrar Huella", command=self.register_fingerprint).pack(side="right", padx=5)
        
        # Tabla de usuarios
        self.user_table_frame = ctk.CTkScrollableFrame(self.user_tab, height=300)
        self.user_table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.load_users()
    
    def setup_records_tab(self):
        """Configura la pestaña de visualización de registros"""
        # Controles de filtrado
        filter_frame = ctk.CTkFrame(self.records_tab)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(filter_frame, text="Filtrar registros:").pack(side="left", padx=5)
        
        self.filter_user = ctk.CTkEntry(filter_frame, placeholder_text="ID o nombre", width=150)
        self.filter_user.pack(side="left", padx=5)
        
        self.filter_date_from = ctk.CTkEntry(filter_frame, placeholder_text="Desde (dd/mm/aaaa)", width=150)
        self.filter_date_from.pack(side="left", padx=5)
        
        self.filter_date_to = ctk.CTkEntry(filter_frame, placeholder_text="Hasta (dd/mm/aaaa)", width=150)
        self.filter_date_to.pack(side="left", padx=5)
        
        filter_btn = ctk.CTkButton(filter_frame, text="Aplicar", width=80, 
                                  command=self.filter_records)
        filter_btn.pack(side="right", padx=5)
        
        # Tabla de registros
        self.records_table_frame = ctk.CTkScrollableFrame(self.records_tab, height=400)
        self.records_table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botones de exportación
        export_frame = ctk.CTkFrame(self.records_tab)
        export_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(export_frame, text="Exportar a Excel", 
                     command=self.export_to_excel).pack(side="left", padx=5)
        ctk.CTkButton(export_frame, text="Generar Reporte", 
                     command=self.generate_report).pack(side="left", padx=5)
        
        self.load_records()
    
    def setup_config_tab(self):
        """Configura la pestaña de configuración del sistema"""
        config_frame = ctk.CTkFrame(self.config_tab)
        config_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(config_frame, text="Configuración del Sistema", 
                    font=("Arial", 16)).pack(pady=10)
        
        # Configuración de horarios
        ctk.CTkLabel(config_frame, text="Horario Laboral:").pack(anchor="w", padx=20)
        
        schedule_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        schedule_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(schedule_frame, text="Entrada:").pack(side="left")
        self.entry_time = ctk.CTkEntry(schedule_frame, placeholder_text="08:00", width=80)
        self.entry_time.pack(side="left", padx=5)
        
        ctk.CTkLabel(schedule_frame, text="Salida:").pack(side="left", padx=10)
        self.exit_time = ctk.CTkEntry(schedule_frame, placeholder_text="17:00", width=80)
        self.exit_time.pack(side="left", padx=5)
        
        ctk.CTkLabel(schedule_frame, text="Duración colación:").pack(side="left", padx=10)
        self.break_duration = ctk.CTkEntry(schedule_frame, placeholder_text="60", width=60)
        self.break_duration.pack(side="left", padx=5)
        ctk.CTkLabel(schedule_frame, text="minutos").pack(side="left")
        
        # Configuración del dispositivo
        ctk.CTkLabel(config_frame, text="Configuración Biométrica:", 
                    font=("Arial", 14)).pack(pady=(15, 5), anchor="w", padx=20)
        
        device_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        device_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(device_frame, text="Puerto:").pack(side="left")
        self.device_port = ctk.CTkEntry(device_frame, placeholder_text="COM3", width=100)
        self.device_port.pack(side="left", padx=5)
        
        test_btn = ctk.CTkButton(device_frame, text="Probar Conexión", width=120)
        test_btn.pack(side="right", padx=5)
        
        # Botón de guardar
        save_btn = ctk.CTkButton(config_frame, text="Guardar Configuración", 
                                command=self.save_config)
        save_btn.pack(pady=20)
    
    def load_users(self):
        """Carga la lista de usuarios desde el archivo"""
        # Implementar carga de usuarios
        pass
    
    def load_records(self):
        """Carga los registros desde el archivo"""
        # Implementar carga de registros
        pass
    
    def add_user(self):
        """Agrega un nuevo usuario"""
        # Implementar lógica para agregar usuario
        pass
    
    def edit_user(self):
        """Edita un usuario existente"""
        # Implementar lógica para editar usuario
        pass
    
    def delete_user(self):
        """Elimina un usuario"""
        # Implementar lógica para eliminar usuario
        pass
    
    def register_fingerprint(self):
        """Registra una huella digital"""
        # Implementar lógica para registrar huella
        pass
    
    def filter_records(self):
        """Filtra los registros según los criterios"""
        # Implementar lógica de filtrado
        pass
    
    def export_to_excel(self):
        """Exporta los registros a Excel"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Guardar registros como"
        )
        
        if file_path:
            try:
                # Implementar lógica de exportación
                messagebox.showinfo("Éxito", "Registros exportados correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")
    
    def generate_report(self):
        """Genera un reporte de asistencia"""
        # Implementar generación de reporte
        pass
    
    def save_config(self):
        """Guarda la configuración del sistema"""
        # Implementar guardado de configuración
        messagebox.showinfo("Configuración", "Configuración guardada correctamente")
    
    def return_to_main(self):
        """Vuelve a la pantalla principal"""
        self.destroy()
        self.parent_app.deiconify()

if __name__ == "__main__":
    app = RelojControlApp()
    app.mainloop()
