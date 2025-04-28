import os
import sys
import ctypes
from ctypes import *
import platform

# Configuración de rutas para las DLLs
LOCAL_DLL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dll")
DPFP_DD_DLL = os.path.join(LOCAL_DLL_PATH, "dpfpdd.dll")
DPFP_AD_DLL = os.path.join(LOCAL_DLL_PATH, "dpfpad.dll")

def load_dlls():
    """Carga las DLLs necesarias con manejo de errores mejorado"""
    try:
        # Añadir la ruta de las DLLs al PATH del sistema
        os.environ['PATH'] = LOCAL_DLL_PATH + ';' + os.environ['PATH']
        
        # Verificar existencia de archivos
        if not all(os.path.exists(dll) for dll in [DPFP_DD_DLL, DPFP_AD_DLL]):
            missing = [dll for dll in [DPFP_DD_DLL, DPFP_AD_DLL] if not os.path.exists(dll)]
            raise FileNotFoundError(f"No se encontraron las siguientes DLLs: {', '.join(missing)}")

        # Cargar las DLLs
        global dpfpdd, dpfpad
        dpfpdd = ctypes.WinDLL(DPFP_DD_DLL)
        dpfpad = ctypes.WinDLL(DPFP_AD_DLL)
        
        print(f"[SUCCESS] DLLs cargadas correctamente desde:\n{DPFP_DD_DLL}\n{DPFP_AD_DLL}")
        return True
    
    except Exception as e:
        print(f"[ERROR] Fallo al cargar DLLs: {str(e)}", file=sys.stderr)
        show_troubleshooting_guide()
        return False

def show_troubleshooting_guide():
    """Muestra guía de solución de problemas"""
    print("\nGUÍA DE SOLUCIÓN DE PROBLEMAS:")
    print("1. Verifica que las DLLs existen en las rutas:")
    print(f"   - {DPFP_DD_DLL}")
    print(f"   - {DPFP_AD_DLL}")
    
    print("\n2. Instala los requisitos del sistema:")
    print("   - Microsoft Visual C++ 2013 Redistributable (x64)")
    print("   - Microsoft Visual C++ 2015-2022 Redistributable (x64)")
    
    print("\n3. Prueba estas soluciones alternativas:")
    print("   a) Copia dpfpdd.dll y dpfpad.dll a la carpeta de tu proyecto")
    print("   b) Ejecuta Python como administrador")
    print("   c) Verifica que el servicio 'DigitalPersona Service' esté en ejecución")
    
    print("\n4. Información del sistema:")
    print(f"   - OS: {platform.system()} {platform.release()}")
    print(f"   - Arquitectura: {platform.architecture()[0]}")
    print(f"   - Python: {platform.python_version()}")

# Carga las DLLs al importar el módulo
if not load_dlls():
    sys.exit(1)

# Definiciones de tipos y estructuras necesarias
DPFPDD_VERSION = ctypes.c_ushort * 3
DPFPDD_DEV_INFO = ctypes.c_void_p
DPFPDD_DEV_CAPS = ctypes.c_uint

# Constantes
DPFPDD_SUCCESS = 0x0000

# Prototipos de funciones
dpfpdd_init = dpfpdd.dpfpdd_init
dpfpdd_init.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint]
dpfpdd_init.restype = ctypes.c_int

dpfpdd_exit = dpfpdd.dpfpdd_exit
dpfpdd_exit.argtypes = [ctypes.c_void_p]
dpfpdd_exit.restype = ctypes.c_int

# Definiciones para la captura de huellas
class DPFP_FEATURE_TYPE:
    DPFP_FT_FINGERPRINT = 1

class DPFP_SAMPLE_FORMAT:
    DPFP_SF_STANDARD = 0

class DPFP_CAPTURE_RESULT(Structure):
    _fields_ = [("sample", c_void_p),
                ("quality", c_int),
                ("status", c_int)]

# Funciones para captura de huellas
dpfpad_create = dpfpad.dpfpad_create
dpfpad_create.argtypes = [c_int, c_int, c_void_p]
dpfpad_create.restype = c_void_p

dpfpad_capture = dpfpad.dpfpad_capture
dpfpad_capture.argtypes = [c_void_p, c_int, POINTER(DPFP_CAPTURE_RESULT)]
dpfpad_capture.restype = c_int

dpfpad_destroy = dpfpad.dpfpad_destroy
dpfpad_destroy.argtypes = [c_void_p]
dpfpad_destroy.restype = None

class FingerprintReader:
    def __init__(self):
        self.handle = ctypes.c_void_p()
        self.ad_handle = None
        self.initialize_reader()
    
    def initialize_reader(self):
        """Inicializa el lector biométrico"""
        try:
            result = dpfpdd_init(ctypes.byref(self.handle), 0)
            if result != DPFPDD_SUCCESS:
                raise RuntimeError(f"Error al inicializar el lector. Código: {result}")
            
            # Inicializar el capturador
            self.ad_handle = dpfpad_create(DPFP_FEATURE_TYPE.DPFP_FT_FINGERPRINT, 
                                         DPFP_SAMPLE_FORMAT.DPFP_SF_STANDARD, 
                                         None)
            if not self.ad_handle:
                raise RuntimeError("No se pudo crear el capturador de huellas")
            
            print("Lector biométrico inicializado correctamente")
        except Exception as e:
            print(f"Error en initialize_reader: {str(e)}", file=sys.stderr)
            raise
    
    def capture_fingerprint(self, timeout=10000):
        """Captura una huella digital"""
        try:
            result = DPFP_CAPTURE_RESULT()
            ret = dpfpad_capture(self.ad_handle, timeout, byref(result))
            
            if ret != DPFPDD_SUCCESS:
                raise RuntimeError(f"Error en captura: {ret}")
            
            if result.status != DPFPDD_SUCCESS:
                raise RuntimeError(f"Calidad de huella insuficiente: {result.quality}")
            
            # Convertir el sample a bytes (esto puede variar según tu SDK)
            sample_size = 2048  # Ajusta según tu dispositivo
            sample_data = string_at(result.sample, sample_size)
            
            return sample_data
        except Exception as e:
            print(f"Error en capture_fingerprint: {str(e)}", file=sys.stderr)
            raise
    
    def verify(self, template1, template2, threshold=80):
        """Verifica si dos templates coinciden"""
        # Esta es una implementación básica. Deberías usar las funciones de tu SDK para verificación real
        similarity = self._calculate_similarity(template1, template2)
        return similarity >= threshold, similarity
    
    def _calculate_similarity(self, template1, template2):
        """Calcula similitud entre templates (implementación simplificada)"""
        # En una implementación real, usarías las funciones del SDK
        from difflib import SequenceMatcher
        return SequenceMatcher(None, template1, template2).ratio() * 100
    
    def __del__(self):
        """Libera recursos al destruir el objeto"""
        if self.ad_handle:
            dpfpad_destroy(self.ad_handle)
        if hasattr(self, 'handle') and self.handle:
            dpfpdd_exit(self.handle)

# Funciones de interfaz para tu test
_device_instance = None

def get_biometric_device():
    """Obtiene la instancia del dispositivo biométrico"""
    global _device_instance
    if _device_instance is None:
        _device_instance = FingerprintReader()
    return _device_instance

def capture_fingerprint():
    """Captura una huella digital"""
    device = get_biometric_device()
    return device.capture_fingerprint()