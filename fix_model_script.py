
import os
import zipfile
import keras

model_dir = r"D:\Mariyam\DermSkin\guest\models\densenet169_skin_disease_model.keras"
output_file = r"D:\Mariyam\DermSkin\guest\models\restored.keras"

print(f"Zipping contents of {model_dir} to {output_file}...")

try:
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(model_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate relative path for archive
                arcname = os.path.relpath(file_path, model_dir)
                zipf.write(file_path, arcname)
    print("Zip created.")

    print("Attempting to load model...")
    model = keras.models.load_model(output_file, compile=False)
    print("SUCCESS: Model loaded successfully.")

except Exception as e:
    print(f"ERROR: {e}")
