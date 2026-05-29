import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import os
import json
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_data(data_path):
    logging.info("Cargando datos...")
    df = pd.read_csv(data_path)
    return df


def create_pipeline():
    """Crea el pipeline de preprocesamiento + modelo XGBoost."""
    # Variables numéricas y categóricas
    numeric_features = ['hour', 'day_of_week']
    categorical_features = ['weather', 'zone']
    
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
        
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', XGBRegressor(random_state=42, objective='reg:squarederror'))
    ])
    
    return pipeline


def save_metrics(metrics: dict, models_dir: str):
    """Guarda las métricas del modelo en un archivo JSON histórico."""
    metrics_file = os.path.join(models_dir, 'metrics_history.json')
    
    history = []
    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []
    
    history.append(metrics)
    
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    logging.info(f"Métricas guardadas en {metrics_file}")


def get_latest_metrics(models_dir: str) -> dict | None:
    """Obtiene las métricas del último modelo entrenado."""
    metrics_file = os.path.join(models_dir, 'metrics_history.json')
    
    if not os.path.exists(metrics_file):
        return None
    
    try:
        with open(metrics_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        return history[-1] if history else None
    except (json.JSONDecodeError, IOError):
        return None


def train_and_evaluate(data_seed=42):
    """Pipeline completo de entrenamiento y evaluación.
    
    Args:
        data_seed: Semilla para generación de datos. None = aleatorio.
    
    Returns:
        dict: Métricas del modelo entrenado (mse, mae, r2, version, best_params).
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, 'data', 'puno_traffic.csv')
    
    # Generar datos si no existen
    if not os.path.exists(data_path):
        import sys
        sys.path.append(current_dir)
        from data.generate_data import generate_traffic_data
        generate_traffic_data(seed=data_seed)
        
    df = load_data(data_path)
    
    X = df[['hour', 'day_of_week', 'weather', 'zone']]
    y = df['traffic_level']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    pipeline = create_pipeline()
    
    # Optimización de hiperparámetros (grid expandido)
    param_grid = {
        'regressor__n_estimators': [50, 100, 200],
        'regressor__max_depth': [3, 5, 7],
        'regressor__learning_rate': [0.01, 0.05, 0.1],
        'regressor__subsample': [0.8, 1.0],
        'regressor__colsample_bytree': [0.8, 1.0],
    }
    
    logging.info(f"Iniciando Grid Search ({np.prod([len(v) for v in param_grid.values()])} combinaciones)...")
    grid_search = GridSearchCV(
        pipeline, param_grid, cv=3,
        scoring='neg_mean_squared_error',
        n_jobs=-1, verbose=1
    )
    grid_search.fit(X_train, y_train)
    
    best_model = grid_search.best_estimator_
    logging.info(f"Mejores parámetros: {grid_search.best_params_}")
    
    # Evaluación
    logging.info("Evaluando modelo...")
    y_pred = best_model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    logging.info(f"Métricas del modelo - MSE: {mse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}")
    
    # Guardar modelo
    models_dir = os.path.join(current_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_filename = os.path.join(models_dir, f'traffic_model_v{version}.joblib')
    latest_model_filename = os.path.join(models_dir, 'traffic_model_latest.joblib')
    
    joblib.dump(best_model, model_filename)
    joblib.dump(best_model, latest_model_filename)
    logging.info(f"Modelo guardado en {model_filename}")
    
    # Persistir métricas
    metrics = {
        'version': version,
        'mse': round(mse, 4),
        'mae': round(mae, 4),
        'r2': round(r2, 4),
        'best_params': {k: str(v) for k, v in grid_search.best_params_.items()},
        'trained_at': datetime.now().isoformat(),
        'data_records': len(df),
        'data_seed': data_seed
    }
    save_metrics(metrics, models_dir)
    
    return metrics


if __name__ == "__main__":
    metrics = train_and_evaluate(data_seed=42)
    print(f"\nEntrenamiento completado. R2: {metrics['r2']}, MAE: {metrics['mae']}")
