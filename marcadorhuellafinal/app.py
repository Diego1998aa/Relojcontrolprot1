from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import pandas as pd
import datetime
import json

# Switch to light mode and blue theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Data files
ARCHIVO_USUARIOS = "data/usuarios.xlsx"
ARCHIVO_REGISTROS = "data/registros_huellas.csv"
ARCHIVO_DOCENTE = "personal_docente.csv"
ARCHIVO_ASISTENTE = "personal_asistente.csv"
CONFIG_PATH = "data/config.json"

class RelojControlApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Reloj Control")
        self.configure_window()
        self.create_widgets()
        self.setup_data()
        # Inicializar el sistema de detección de huellas
        self.fingerprint_scan_active = False
        self.last_verification_time = None
        self.verification_cooldown = 3  # segundos entre verificaciones

    def configure_window(self):
        """Configure main window"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 900
        window_height = 700
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.resizable(False, False)

    def setup_data(self):
        """Initialize data files"""
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(ARCHIVO_USUARIOS):
            df = pd.DataFrame(columns=["ID", "Nombre", "Rol", "Huella"])
            df.to_excel(ARCHIVO_USUARIOS, index=False)
        if not os.path.exists(ARCHIVO_REGISTROS):
            df = pd.DataFrame(columns=["RUT", "Nombre", "Fecha", "Hora", "Accion", "Metodo"])
            df.to_csv(ARCHIVO_REGISTROS, index=False)
        if not os.path.exists(CONFIG_PATH):
            default_config = {
                "entry_time": "08:00",
                "exit_time": "17:00",
                "break_duration": "60"
            }
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4)

    def create_widgets(self):
        """Create UI widgets"""
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        self.center_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.center_frame.pack(expand=True, fill="both", padx=40, pady=20)

        self.time_label = ctk.CTkLabel(
            self.center_frame,
            text="",
            font=("Arial", 28, "bold"),
            text_color="#2986cc"
        )
        self.time_label.pack(pady=(10, 20))

        self.scanning_label = ctk.CTkLabel(
            self.center_frame,
            text="ESCANEANDO HUELLA DIGITAL",
            font=("Arial", 22, "bold"),
            text_color="#ffa500"
        )
        self.scanning_label.pack(pady=10)

        # Añadir marco para información del usuario
        self.user_info_frame = ctk.CTkFrame(self.center_frame, fg_color="#f0f0f0", corner_radius=10)
        self.user_info_frame.pack(pady=20, fill="x", padx=40)
        self.user_info_frame.pack_forget()  # Ocultar inicialmente

        self.user_name_label = ctk.CTkLabel(
            self.user_info_frame,
            text="",
            font=("Arial", 20, "bold"),
            text_color="#2986cc"
        )
        self.user_name_label.pack(pady=(15, 5))

        self.user_id_label = ctk.CTkLabel(
            self.user_info_frame,
            text="",
            font=("Arial", 16),
            text_color="#333333"
        )
        self.user_id_label.pack(pady=5)

        self.user_role_label = ctk.CTkLabel(
            self.user_info_frame,
            text="",
            font=("Arial", 16),
            text_color="#333333"
        )
        self.user_role_label.pack(pady=5)

        self.record_time_label = ctk.CTkLabel(
            self.user_info_frame,
            text="",
            font=("Arial", 16, "bold"),
            text_color="#009900"
        )
        self.record_time_label.pack(pady=(5, 15))

        self.animate_scanning()

        title_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=10)

        try:
            logo_path = "images/logocoleoscuro.jpg"
            image = Image.open(logo_path)
            logo_size = (50, 50)
            logo_image = ctk.CTkImage(light_image=image, dark_image=image, size=logo_size)
            logo_label = ctk.CTkLabel(title_frame, image=logo_image, text="")
            logo_label.image = logo_image
            logo_label.pack(side="left", padx=(0,10))
        except Exception as e:
            print(f"Error loading logo: {e}")

        self.school_label = ctk.CTkLabel(
            title_frame,
            text="Escuela Olegario Morales Oliva",
            font=("Arial", 18, "bold"),
            text_color="#333333"
        )
        self.school_label.pack(side="left", pady=5)

        self.system_label = ctk.CTkLabel(
            title_frame,
            text="Sistema de Reloj Control",
            font=("Arial", 16),
            text_color="#666666"
        )
        self.system_label.pack(side="left", padx=(10,0))

        self.update_clock()

        self.status_label = ctk.CTkLabel(
            self.center_frame,
            text="Sistema listo - Coloque su dedo en el lector",
            font=("Arial", 16),
            text_color="#2986cc"
        )
        self.status_label.pack(pady=10)

        # Botones de acción
        self.button_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.button_frame.pack(pady=20)

        self.scan_btn = ctk.CTkButton(
            self.button_frame,
            text="Iniciar Escaneo",
            command=self.toggle_fingerprint_scan,
            font=("Arial", 14),
            fg_color="#28a745",
            hover_color="#218838",
            height=35,
            width=150
        )
        self.scan_btn.pack(side="left", padx=10)

        self.admin_btn = ctk.CTkButton(
            self.button_frame,
            text="Modo Admin",
            command=self.open_admin,
            font=("Arial", 14),
            fg_color="#2986cc",
            hover_color="#1a5f96",
            height=35,
            width=150
        )
        self.admin_btn.pack(side="left", padx=10)

        # Iniciar escaneo automáticamente
        self.after(1000, self.start_fingerprint_scan)

    def animate_scanning(self):
        current_text = self.scanning_label.cget("text")
        if current_text.endswith("..."):
            new_text = "ESCANEANDO HUELLA DIGITAL"
        else:
            new_text = current_text + "."
        self.scanning_label.configure(text=new_text)
        self.after(500, self.animate_scanning)

    def update_clock(self):
        now = datetime.datetime.now()
        formatted_time = now.strftime("%d.%m.%Y, %H:%M:%S Hrs.")
        self.time_label.configure(text=formatted_time)
        self.after(1000, self.update_clock)

    def toggle_fingerprint_scan(self):
        if self.fingerprint_scan_active:
            self.stop_fingerprint_scan()
        else:
            self.start_fingerprint_scan()

    def start_fingerprint_scan(self):
        """Inicia el escaneo periódico de huellas digitales."""
        self.fingerprint_scan_active = True
        self.scan_btn.configure(text="Detener Escaneo", fg_color="#dc3545", hover_color="#c82333")
        self.status_label.configure(text="Escaneando... Coloque su dedo en el lector", text_color="#28a745")
        self.check_for_fingerprint()
    
    def stop_fingerprint_scan(self):
        """Detiene el escaneo periódico de huellas digitales."""
        self.fingerprint_scan_active = False
        self.scan_btn.configure(text="Iniciar Escaneo", fg_color="#28a745", hover_color="#218838")
        self.status_label.configure(text="Escaneo detenido", text_color="#dc3545")

    def check_for_fingerprint(self):
        """Verifica periódicamente si hay una huella digital en el lector."""
        if not self.fingerprint_scan_active:
            return
            
        # Verificar si se ha pasado suficiente tiempo desde la última verificación
        now = datetime.datetime.now()
        if self.last_verification_time and (now - self.last_verification_time).total_seconds() < self.verification_cooldown:
            # Todavía en enfriamiento, programar la próxima verificación
            self.after(500, self.check_for_fingerprint)
            return
            
        # Intentar capturar y verificar una huella
        try:
            from sensors.biometric import simulate_fingerprint_scan, verify_fingerprint
            
            # Esta función normalmente se ejecuta en un hilo separado para no bloquear la interfaz,
            # pero para simplificar, aquí se ejecuta en el hilo principal
            fingerprint_data = simulate_fingerprint_scan()
            
            if fingerprint_data:
                self.last_verification_time = now
                success, user_info, message = verify_fingerprint(fingerprint_data)
                
                if success and user_info is not None:
                    self.show_user_verified(user_info)
                else:
                    self.show_verification_failed(message)
        except Exception as e:
            print(f"Error al verificar huella: {str(e)}")
            self.status_label.configure(text=f"Error: {str(e)}", text_color="#dc3545")
            
        # Programar la próxima verificación
        self.after(500, self.check_for_fingerprint)

    def show_user_verified(self, user_info):
        """Muestra la información del usuario verificado."""
        # Actualizar etiquetas con información del usuario
        self.user_name_label.configure(text=user_info['Nombre'])
        self.user_id_label.configure(text=f"ID: {user_info['ID']}")
        self.user_role_label.configure(text=f"Rol: {user_info['Rol']}")
        
        now = datetime.datetime.now()
        self.record_time_label.configure(text=f"Registro: {now.strftime('%H:%M:%S')}")
        
        # Mostrar el marco de información del usuario
        self.user_info_frame.pack(pady=20, fill="x", padx=40)
        
        # Actualizar estado
        self.status_label.configure(text="¡Usuario verificado correctamente!", text_color="#28a745")
        
        # Ocultar la información después de un tiempo
        self.after(5000, self.hide_user_info)
        
    def hide_user_info(self):
        """Oculta la información del usuario después de un tiempo."""
        self.user_info_frame.pack_forget()
        if self.fingerprint_scan_active:
            self.status_label.configure(text="Escaneando... Coloque su dedo en el lector", text_color="#28a745")
        
    def show_verification_failed(self, message):
        """Muestra un mensaje cuando la verificación falla."""
        self.status_label.configure(text=f"Verificación fallida: {message}", text_color="#dc3545")
        self.after(3000, lambda: self.status_label.configure(
            text="Escaneando... Coloque su dedo en el lector" if self.fingerprint_scan_active else "Escaneo detenido",
            text_color="#28a745" if self.fingerprint_scan_active else "#dc3545"
        ))

    def open_admin(self):
        self.withdraw()
        admin_window = AdminPanel(self)
        admin_window.grab_set()
        admin_window.protocol("WM_DELETE_WINDOW", lambda: self.on_admin_close(admin_window))
        admin_window.mainloop()

    def on_admin_close(self, admin_window):
        admin_window.destroy()
        if self.winfo_exists():
            self.deiconify()

class AdminPanel(ctk.CTkToplevel):
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.title("Panel de Administración")
        self.geometry("800x600")
        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        header_frame = ctk.CTkFrame(main_frame, height=60, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(header_frame, text="PANEL DE ADMINISTRACIÓN", font=("Arial", 20, "bold")).pack(side="left")

        back_btn = ctk.CTkButton(header_frame, text="Volver", width=100, command=self.return_to_main)
        back_btn.pack(side="right")

        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.user_tab = self.tabview.add("Usuarios")
        self.setup_user_tab()

        self.records_tab = self.tabview.add("Registros")
        self.setup_records_tab()

        self.config_tab = self.tabview.add("Configuración")
        self.setup_config_tab()

    def setup_user_tab(self):
        form_frame = ctk.CTkFrame(self.user_tab)
        form_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="Gestión de Usuarios", font=("Arial", 16)).pack(pady=5)

        self.user_id = ctk.CTkEntry(form_frame, placeholder_text="ID de empleado")
        self.user_id.pack(fill="x", pady=5)

        self.user_name = ctk.CTkEntry(form_frame, placeholder_text="Nombre completo")
        self.user_name.pack(fill="x", pady=5)

        self.user_role = ctk.CTkOptionMenu(form_frame, values=["Docente", "Asistente", "Administrador"])
        self.user_role.pack(fill="x", pady=5)

        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(btn_frame, text="Agregar", command=self.add_user).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Editar", command=self.edit_user).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Eliminar", command=self.delete_user).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Registrar Huella", command=self.register_fingerprint).pack(side="right", padx=5)

        self.user_table_frame = ctk.CTkScrollableFrame(self.user_tab, height=300)
        self.user_table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_users()

    def setup_records_tab(self):
        filter_frame = ctk.CTkFrame(self.records_tab)
        filter_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(filter_frame, text="Filtrar registros:").pack(side="left", padx=5)

        self.filter_user = ctk.CTkEntry(filter_frame, placeholder_text="ID o nombre", width=150)
        self.filter_user.pack(side="left", padx=5)

        self.filter_date_from = ctk.CTkEntry(filter_frame, placeholder_text="Desde (dd/mm/aaaa)", width=150)
        self.filter_date_from.pack(side="left", padx=5)

        self.filter_date_to = ctk.CTkEntry(filter_frame, placeholder_text="Hasta (dd/mm/aaaa)", width=150)
        self.filter_date_to.pack(side="left", padx=5)

        filter_btn = ctk.CTkButton(filter_frame, text="Aplicar", width=80, command=self.filter_records)
        filter_btn.pack(side="right", padx=5)

        self.records_table_frame = ctk.CTkScrollableFrame(self.records_tab, height=400)
        self.records_table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        export_frame = ctk.CTkFrame(self.records_tab)
        export_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(export_frame, text="Exportar a Excel", command=self.export_to_excel).pack(side="left", padx=5)
        ctk.CTkButton(export_frame, text="Generar Reporte", command=self.generate_report).pack(side="left", padx=5)

        self.load_records()

    def setup_config_tab(self):
        config_frame = ctk.CTkFrame(self.config_tab)
        config_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(config_frame, text="Configuración del Sistema", font=("Arial", 16)).pack(pady=5)

        # Horario de entrada
        entry_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        entry_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(entry_frame, text="Horario de entrada:").pack(side="left", padx=5)
        self.entry_time = ctk.CTkEntry(entry_frame, placeholder_text="HH:MM", width=100)
        self.entry_time.pack(side="left", padx=5)

        # Horario de salida
        exit_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        exit_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(exit_frame, text="Horario de salida:").pack(side="left", padx=5)
        self.exit_time = ctk.CTkEntry(exit_frame, placeholder_text="HH:MM", width=100)
        self.exit_time.pack(side="left", padx=5)

        # Duración del descanso
        break_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        break_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(break_frame, text="Duración del descanso (minutos):").pack(side="left", padx=5)
        self.break_duration = ctk.CTkEntry(break_frame, placeholder_text="60", width=100)
        self.break_duration.pack(side="left", padx=5)

        # Botón guardar
        save_btn = ctk.CTkButton(config_frame, text="Guardar Configuración", command=self.save_config)
        save_btn.pack(pady=20)

    def load_config(self):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.entry_time.insert(0, config.get("entry_time", "08:00"))
                self.exit_time.insert(0, config.get("exit_time", "17:00"))
                self.break_duration.insert(0, config.get("break_duration", "60"))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar configuración: {str(e)}")

    def load_users(self):
        try:
            for widget in self.user_table_frame.winfo_children():
                widget.destroy()

            df_docente = pd.read_csv(ARCHIVO_DOCENTE)
            df_asistente = pd.read_csv(ARCHIVO_ASISTENTE)

            docentes = pd.DataFrame({
                'ID': df_docente['RUN'],
                'Nombre': df_docente['Nombre'],
                'Rol': 'Docente',
                'Huella': ''
            })

            asistentes = pd.DataFrame({
                'ID': df_asistente['RUN'],
                'Nombre': df_asistente['Nombre'],
                'Rol': df_asistente['Estamento'],
                'Huella': ''
            })

            df_combined = pd.concat([docentes, asistentes], ignore_index=True)

            for _, row in df_combined.iterrows():
                user_frame = ctk.CTkFrame(self.user_table_frame, fg_color="transparent")
                user_frame.pack(fill="x", pady=2)

                ctk.CTkLabel(user_frame, text=str(row['ID'])).pack(side="left", expand=True)
                ctk.CTkLabel(user_frame, text=str(row['Nombre'])).pack(side="left", expand=True)
                ctk.CTkLabel(user_frame, text=str(row['Rol'])).pack(side="left", expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los usuarios: {str(e)}")

    def load_records(self):
        try:
            for widget in self.records_table_frame.winfo_children():
                widget.destroy()

            df = pd.read_csv(ARCHIVO_REGISTROS)

            headers = ["RUT", "Nombre", "Fecha", "Hora", "Accion"]
            header_frame = ctk.CTkFrame(self.records_table_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, 5))

            for header in headers:
                ctk.CTkLabel(header_frame, text=header, font=("Arial", 12, "bold")).pack(side="left", expand=True)

            for _, row in df.iterrows():
                record_frame = ctk.CTkFrame(self.records_table_frame, fg_color="transparent")
                record_frame.pack(fill="x", pady=2)

                ctk.CTkLabel(record_frame, text=str(row['RUT'])).pack(side="left", expand=True)
                ctk.CTkLabel(record_frame, text=str(row['Nombre'])).pack(side="left", expand=True)
                ctk.CTkLabel(record_frame, text=str(row['Fecha'])).pack(side="left", expand=True)
                ctk.CTkLabel(record_frame, text=str(row['Hora'])).pack(side="left", expand=True)
                ctk.CTkLabel(record_frame, text=str(row['Accion'])).pack(side="left", expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los registros: {str(e)}")

    def filter_records(self):
        try:
            user_filter = self.filter_user.get()
            date_from = self.filter_date_from.get()
            date_to = self.filter_date_to.get()

            df = pd.read_csv(ARCHIVO_REGISTROS)

            if user_filter:
                mask = df["RUT"].str.contains(user_filter, na=False) | df["Nombre"].str.contains(user_filter, na=False)
                df = df[mask]
            if date_from:
                df = df[pd.to_datetime(df["Fecha"]) >= pd.to_datetime(date_from)]
            if date_to:
                df = df[pd.to_datetime(df["Fecha"]) <= pd.to_datetime(date_to)]

            for widget in self.records_table_frame.winfo_children():
                widget.destroy()

            headers = ["RUT", "Nombre", "Fecha", "Hora", "Accion"]
            header_frame = ctk.CTkFrame(self.records_table_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, 5))

            for header in headers:
                ctk.CTkLabel(header_frame, text=header, font=("Arial", 12, "bold")).pack(side="left", expand=True)

            for _, row in df.iterrows():
                record_frame = ctk.CTkFrame(self.records_table_frame, fg_color="transparent")
                record_frame.pack(fill="x", pady=2)

                ctk.CTkLabel(record_frame, text=str(row['RUT'])).pack(side="left", expand=True)
                ctk.CTkLabel(record_frame, text=str(row['Nombre'])).pack(side="left", expand=True)
                ctk.CTkLabel(record_frame, text=str(row['Fecha'])).pack(side="left", expand=True)
                ctk.CTkLabel(record_frame, text=str(row['Hora'])).pack(side="left", expand=True)
                ctk.CTkLabel(record_frame, text=str(row['Accion'])).pack(side="left", expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar registros: {str(e)}")

    def add_user(self):
        user_id = self.user_id.get()
        user_name = self.user_name.get()
        user_role = self.user_role.get()

        if not all([user_id, user_name, user_role]):
            messagebox.showwarning("Advertencia", "Por favor complete todos los campos")
            return

        valid_roles = ["Docente", "Asistente", "Administrador"]
        if user_role not in valid_roles:
            messagebox.showerror("Error", f"Rol inválido. Debe ser uno de: {', '.join(valid_roles)}")
            return

        try:
            # Verificar si el usuario ya existe en los archivos CSV
            df_docente = pd.read_csv(ARCHIVO_DOCENTE)
            df_asistente = pd.read_csv(ARCHIVO_ASISTENTE)
            
            if user_id in df_docente['RUN'].values or user_id in df_asistente['RUN'].values:
                messagebox.showerror("Error", "El RUT ya existe en la base de datos")
                return

            # Agregar el usuario al archivo correspondiente según su rol
            new_user = pd.DataFrame({
                'RUN': [user_id],
                'Nombre': [user_name],
                'Estamento': [user_role]
            })

            if user_role == "Docente":
                df_docente = pd.concat([df_docente, new_user[['RUN', 'Nombre']]], ignore_index=True)
                df_docente.to_csv(ARCHIVO_DOCENTE, index=False)
            else:
                df_asistente = pd.concat([df_asistente, new_user], ignore_index=True)
                df_asistente.to_csv(ARCHIVO_ASISTENTE, index=False)

            # También agregar al archivo de usuarios para las huellas
            df_usuarios = pd.read_excel(ARCHIVO_USUARIOS)
            new_user_huella = pd.DataFrame([[user_id, user_name, user_role, ""]],
                                         columns=["ID", "Nombre", "Rol", "Huella"])
            df_usuarios = pd.concat([df_usuarios, new_user_huella], ignore_index=True)
            df_usuarios.to_excel(ARCHIVO_USUARIOS, index=False)

            messagebox.showinfo("Éxito", "Usuario agregado correctamente")

            self.user_id.delete(0, 'end')
            self.user_name.delete(0, 'end')
            self.user_role.set("Docente")

            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el usuario: {str(e)}")

    def edit_user(self):
        user_id = self.user_id.get()
        user_name = self.user_name.get()
        user_role = self.user_role.get()

        if not user_id:
            messagebox.showwarning("Advertencia", "Por favor ingrese el ID del usuario a editar")
            return

        try:
            df = pd.read_excel(ARCHIVO_USUARIOS)

            if user_id not in df['ID'].values:
                messagebox.showerror("Error", "Usuario no encontrado")
                return

            mask = df['ID'] == user_id
            if user_name:
                df.loc[mask, 'Nombre'] = user_name
            if user_role:
                df.loc[mask, 'Rol'] = user_role

            df.to_excel(ARCHIVO_USUARIOS, index=False)

            messagebox.showinfo("Éxito", "Usuario actualizado correctamente")

            self.user_id.delete(0, 'end')
            self.user_name.delete(0, 'end')
            self.user_role.set("Docente")

            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el usuario: {str(e)}")

    def delete_user(self):
        user_id = self.user_id.get()

        if not user_id:
            messagebox.showwarning("Advertencia", "Por favor ingrese el ID del usuario a eliminar")
            return

        if not messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este usuario?"):
            return

        try:
            df = pd.read_excel(ARCHIVO_USUARIOS)

            if user_id not in df['ID'].values:
                messagebox.showerror("Error", "Usuario no encontrado")
                return

            df = df[df['ID'] != user_id]

            df.to_excel(ARCHIVO_USUARIOS, index=False)

            messagebox.showinfo("Éxito", "Usuario eliminado correctamente")

            self.user_id.delete(0, 'end')
            self.user_name.delete(0, 'end')
            self.user_role.set("Docente")
        
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el usuario: {str(e)}")

    def register_fingerprint(self):
        from sensors.biometric import register_fingerprint, simulate_fingerprint_scan
        
        user_id = self.user_id.get()
        if not user_id:
            messagebox.showwarning("Advertencia", "Por favor ingrese el RUT del usuario para registrar huella")
            return

        try:
            df = pd.read_excel(ARCHIVO_USUARIOS)
            if user_id not in df['ID'].values:
                messagebox.showerror("Error", "Usuario no encontrado")
                return

            # Mostrar mensaje de instrucción
            messagebox.showinfo("Registro de Huella", 
                              "Por favor, coloque su dedo en el lector de huellas cuando esté listo.")
            
            # Simular escaneo de huella (en un sistema real, esto se conectaría con el hardware)
            fingerprint_data = simulate_fingerprint_scan()
            
            # Registrar la huella
            success, message = register_fingerprint(user_id, fingerprint_data)
            
            if success:
                messagebox.showinfo("Éxito", "Huella registrada correctamente")
                self.load_users()
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar huella: {str(e)}")

    def export_to_excel(self):
        try:
            df = pd.read_csv(ARCHIVO_REGISTROS)
            export_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            if export_path:
                df.to_excel(export_path, index=False)
                messagebox.showinfo("Éxito", f"Registros exportados a {export_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel: {str(e)}")

    def generate_report(self):
        try:
            df = pd.read_csv(ARCHIVO_REGISTROS)
            report_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if report_path:
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write("Reporte de Asistencia\n")
                    f.write("=====================\n\n")
                    total_records = len(df)
                    f.write(f"Total de registros: {total_records}\n\n")
                    roles = df['Accion'].value_counts()
                    f.write("Resumen de acciones:\n")
                    for accion, count in roles.items():
                        f.write(f"  {accion}: {count}\n")
                messagebox.showinfo("Reporte", f"Reporte generado y guardado en:\n{report_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")

    def save_config(self):
        try:
            config = {
                "entry_time": self.entry_time.get(),
                "exit_time": self.exit_time.get(),
                "break_duration": self.break_duration.get()
            }
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Configuración", "Configuración guardada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar configuración: {str(e)}")

    def return_to_main(self):
        self.destroy()
        self.parent_app.deiconify()

if __name__ == "__main__":
    app = RelojControlApp()
    app.mainloop()
