import pandas as pd
import os

DATA_DIR = "data"

def load_users():
    """Carga la lista de usuarios desde el archivo."""
    file_path = os.path.join(DATA_DIR, "usuarios.xlsx")
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        # Asegurar que la columna 'Huella' sea de tipo string para evitar incompatibilidades
        if 'Huella' in df.columns:
            df['Huella'] = df['Huella'].astype(str)
        return df
    return pd.DataFrame(columns=["ID", "Nombre", "Rol", "Huella"])


def save_user(df):
    """Guarda la lista de usuarios en el archivo."""
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_excel(os.path.join(DATA_DIR, "usuarios.xlsx"), index=False)

def load_records():
    """Carga los registros desde el archivo."""
    file_path = os.path.join(DATA_DIR, "registros_huellas.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=["RUT", "Nombre", "Fecha", "Hora", "Accion", "Metodo"])

def save_record(df):
    """Guarda los registros en el archivo."""
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(os.path.join(DATA_DIR, "registros_huellas.csv"), index=False)

def add_record(rut, nombre, accion, metodo="Huella"):
    """Agrega un nuevo registro."""
    try:
        current_time = pd.Timestamp.now()
        record = {
            "RUT": rut,
            "Nombre": nombre,
            "Fecha": current_time.date(),
            "Hora": current_time.strftime('%H:%M:%S'),
            "Accion": accion,
            "Metodo": metodo
        }
        
        records_df = load_records()
        new_record = pd.DataFrame([record])
        records_df = pd.concat([records_df, new_record], ignore_index=True)
        save_record(records_df)
        return True, "Registro guardado exitosamente"
    except Exception as e:
        return False, f"Error al guardar registro: {str(e)}"
