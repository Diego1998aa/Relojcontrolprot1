from sensors.biometric import get_biometric_device, capture_fingerprint
import traceback
import time

def test():
    try:
        print("=== Prueba del Lector de Huellas ===")
        
        # Prueba de inicialización
        print("Inicializando dispositivo...")
        device = get_biometric_device()
        print("Dispositivo listo")
        
        # Prueba de captura
        print("\nColoque su dedo en el lector (5 segundos para captura)...")
        time.sleep(1)  # Pequeña pausa para que el usuario lea
        template = capture_fingerprint()
        
        if template:
            print("\n¡Huella capturada correctamente!")
            print(f"Tamaño del template: {len(template)} bytes")
            
            # Prueba de verificación
            print("\nColoque el mismo dedo nuevamente para verificación...")
            verify_template = capture_fingerprint()
            
            if verify_template:
                print("\nComparando huellas...")
                success, score = device.verify(template, verify_template)
                if success:
                    print(f"\n¡Coincidencia encontrada! (Puntaje: {score:.2f}%)")
                else:
                    print(f"\nLas huellas no coinciden (Puntaje: {score:.2f}%)")
        
    except KeyboardInterrupt:
        print("\nPrueba cancelada por el usuario")
    except Exception as e:
        print(f"\nError en la prueba: {str(e)}")
        traceback.print_exc()
    finally:
        print("\nPrueba finalizada")

if __name__ == "__main__":
    test()