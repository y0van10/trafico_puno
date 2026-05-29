import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta


def generate_traffic_data(num_records=5000, seed=None):
    """Genera datos sintéticos de tráfico vehicular en Puno.
    
    Args:
        num_records: Número de registros a generar.
        seed: Semilla para reproducibilidad. None = aleatorio.
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Parámetros base
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(hours=i) for i in range(num_records)]
    
    zones = ['Centro', 'Bellavista', 'Salcedo', 'Huaje', 'Terminal']
    weather_conditions = ['Soleado', 'Lluvioso', 'Nublado', 'Nevada']
    
    data = []
    for dt in dates:
        hour = dt.hour
        day_of_week = dt.weekday()  # 0 = Monday, 6 = Sunday
        
        zone = np.random.choice(zones)
        weather = np.random.choice(weather_conditions, p=[0.5, 0.25, 0.2, 0.05])
        
        # Lógica para simular nivel de tráfico
        traffic_base = 20
        
        # Hora punta (7-9 AM, 12-2 PM, 6-8 PM)
        if hour in [7, 8, 9, 12, 13, 18, 19, 20]:
            traffic_base += 40
        elif hour < 6 or hour > 22:
            traffic_base -= 10
            
        # Día de semana
        if day_of_week >= 5:  # Fin de semana
            traffic_base -= 15
            
        # Clima
        if weather == 'Lluvioso':
            traffic_base += 15
        elif weather == 'Nevada':
            traffic_base += 30
            
        # Zona
        if zone == 'Centro':
            traffic_base += 20
        elif zone == 'Terminal':
            traffic_base += 15
            
        # Ruido aleatorio
        traffic_level = traffic_base + np.random.normal(0, 10)
        traffic_level = max(0, min(100, traffic_level))  # Limitar entre 0 y 100
        
        data.append({
            'timestamp': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'hour': hour,
            'day_of_week': day_of_week,
            'weather': weather,
            'zone': zone,
            'traffic_level': round(traffic_level, 2)
        })
        
    df = pd.DataFrame(data)
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    file_path = os.path.join(os.path.dirname(__file__), 'puno_traffic.csv')
    df.to_csv(file_path, index=False)
    print(f"Dataset generado en {file_path} ({num_records} registros, seed={seed})")


if __name__ == "__main__":
    generate_traffic_data(seed=42)
