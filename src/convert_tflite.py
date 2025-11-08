# convert_tflite.py
import tensorflow as tf
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import traceback

BASE = Path(__file__).resolve().parent

def find_model_file(base: Path):
    """Return a path to a .h5 file or a SavedModel directory, or None if not found."""
    # preferred explicit name
    h5 = base / "model_keras.h5"
    if h5.exists():
        return str(h5)

    # any .h5 in the folder
    h5_candidates = list(base.glob("*.h5"))
    if h5_candidates:
        return str(h5_candidates[0])

    # SavedModel directory detection (contains saved_model.pb)
    for child in base.iterdir():
        if child.is_dir() and (child / "saved_model.pb").exists():
            return str(child)

    return None

def load_keras_model(path: str):
    """Try to load the Keras model in a resilient way. Prefer compile=False for inference."""
    try:
        print(f"Attempting to load model at: {path} (compile=False)...")
        model = tf.keras.models.load_model(path, compile=False)
        print("Model loaded with compile=False.")
        return model
    except Exception as e:
        print("First load attempt failed:", e)
        # Try to provide common metric mappings as custom_objects
        try:
            print("Retrying with common metric mappings (custom_objects)...")
            custom_objects = {
                "mse": tf.keras.metrics.MeanSquaredError(),
                "mean_squared_error": tf.keras.metrics.MeanSquaredError(),
                # add other common mappings here if you know them
            }
            model = tf.keras.models.load_model(path, custom_objects=custom_objects, compile=False)
            print("Model loaded with custom_objects.")
            return model
        except Exception as e2:
            print("Retry with custom_objects also failed:")
            traceback.print_exc()
            raise

def load_scaler_params(base: Path):
    f = base / "scaler_params.npz"
    if not f.exists():
        raise FileNotFoundError(f"Scaler file not found: {f}")
    params = np.load(f)
    mean = float(params['mean'])
    std = float(params['std'])
    N_STEPS = int(params['N_STEPS'])
    return mean, std, N_STEPS

def load_values(base: Path):
    csv = base / "thingspeak_data.csv"
    if not csv.exists():
        raise FileNotFoundError(f"Data CSV not found: {csv}")
    df = pd.read_csv(csv)
    if 'temp' not in df.columns:
        raise KeyError("CSV does not contain 'temp' column")
    vals = pd.to_numeric(df['temp'], errors='coerce').interpolate().ffill().bfill().values.astype(np.float32)
    return vals

def representative_dataset_generator(vals, mean, std, N_STEPS):
    """Yield representative samples for INT8 quantization calibration."""
    # yield overlapping windows to provide more calibration data if possible
    step = max(1, N_STEPS // 2)
    for i in range(0, len(vals) - N_STEPS + 1, step):
        sample = vals[i:i+N_STEPS].astype(np.float32)
        sample = (sample - mean) / std
        sample = sample.reshape(1, N_STEPS)
        # TFLite converter expects a list of input arrays if model has multiple inputs.
        yield [sample]

def convert_model_to_tflite(model, vals, mean, std, N_STEPS, base: Path):
    try:
        # Build converter from keras model object
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

        # attach representative dataset generator only if we have enough data
        if len(vals) >= N_STEPS:
            converter.representative_dataset = lambda: representative_dataset_generator(vals, mean, std, N_STEPS)
            print("Representative dataset attached for post-training quantization.")
        else:
            print(f"Not enough samples for representative dataset: {len(vals)} < N_STEPS ({N_STEPS})")
            # Keep going without representative dataset (will fallback to float or limited quant)
        
        # Request full-int8 if calibration data provided
        try:
            converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
            converter.inference_input_type = tf.int8
            converter.inference_output_type = tf.int8
            print("Configured converter for full INT8 inference (if supported).")
        except Exception as e:
            print("Could not set INT8 config on converter:", e)

        tflite_model = converter.convert()
        out_path = base / "model.tflite"
        with open(out_path, "wb") as f:
            f.write(tflite_model)
        print(f"Saved TFLite model to: {out_path}")
        return out_path
    except Exception as e:
        print("Conversion to TFLite failed:")
        traceback.print_exc()
        raise

def main():
    print("Script base folder:", BASE)
    model_path = find_model_file(BASE)
    if model_path is None:
        print("ERROR: No Keras model (.h5) or SavedModel directory found in:", BASE)
        print("Place 'model_keras.h5' or a SavedModel directory in the script folder.")
        sys.exit(1)

    # Load model
    try:
        model = load_keras_model(model_path)
    except Exception:
        print("ERROR: Failed to load the Keras model. Aborting.")
        sys.exit(1)

    # Load scaler params and values
    try:
        mean, std, N_STEPS = load_scaler_params(BASE)
        print(f"Scaler params: mean={mean}, std={std}, N_STEPS={N_STEPS}")
    except Exception as e:
        print("ERROR loading scaler params:", e)
        sys.exit(1)

    try:
        vals = load_values(BASE)
        print(f"Loaded {len(vals)} samples from thingspeak_data.csv")
    except Exception as e:
        print("ERROR loading values:", e)
        sys.exit(1)

    if len(vals) < N_STEPS:
        print(f"ERROR: Not enough data ({len(vals)}) for N_STEPS={N_STEPS}. Need at least N_STEPS samples.")
        sys.exit(1)

    # Convert
    try:
        convert_model_to_tflite(model, vals, mean, std, N_STEPS, BASE)
    except Exception:
        print("Conversion failed. See trace above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
