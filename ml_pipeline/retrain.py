import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def retrain_model():
    """Pipeline de reentrenamiento con datos frescos.
    
    Regenera el dataset con una semilla aleatoria, reentrena el modelo
    y compara métricas con la versión anterior antes de promover.
    """
    logging.info("Iniciando proceso de reentrenamiento del modelo (Retraining Pipeline)...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    from data.generate_data import generate_traffic_data
    from train import train_and_evaluate, get_latest_metrics
    
    # Obtener métricas del modelo anterior
    models_dir = os.path.join(current_dir, 'models')
    previous_metrics = get_latest_metrics(models_dir)
    
    if previous_metrics:
        logging.info(
            f"Modelo anterior - R2: {previous_metrics['r2']}, "
            f"MAE: {previous_metrics['mae']}, MSE: {previous_metrics['mse']}"
        )
    
    # Regenerar datos con semilla aleatoria para simular datos nuevos
    logging.info("Generando nuevo dataset con datos frescos...")
    generate_traffic_data(seed=None)
    
    # Reentrenar
    new_metrics = train_and_evaluate(data_seed=None)
    
    # Comparar métricas
    if previous_metrics:
        r2_diff = new_metrics['r2'] - previous_metrics['r2']
        mae_diff = new_metrics['mae'] - previous_metrics['mae']
        
        logging.info(f"Comparación de modelos:")
        logging.info(f"  R2:  {previous_metrics['r2']:.4f} -> {new_metrics['r2']:.4f} ({r2_diff:+.4f})")
        logging.info(f"  MAE: {previous_metrics['mae']:.4f} -> {new_metrics['mae']:.4f} ({mae_diff:+.4f})")
        
        if new_metrics['r2'] < previous_metrics['r2'] * 0.95:
            logging.warning(
                "⚠️ El nuevo modelo tiene un R2 significativamente peor. "
                "Considerar revisar los datos o hiperparámetros."
            )
    
    logging.info("Reentrenamiento completado exitosamente. Nuevo modelo guardado y etiquetado como 'latest'.")
    return new_metrics


if __name__ == "__main__":
    retrain_model()