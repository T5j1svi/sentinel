import os
import zipfile

def create_export_zip(source_dir, output_filename):
    print(f"Creating {output_filename}...")
    
    # Exclude these heavy or auto-generated directories
    exclude_dirs = {'venv', 'node_modules', '__pycache__', '.git', 'uploads', 'exports', 'database'}
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                # Skip some file types
                if file.endswith('.db') or file.endswith('.pyc') or file == 'sentinel_export.zip':
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                
                # Add to zip
                zipf.write(file_path, arcname)
                
    print(f"Successfully created {output_filename}")
    print(f"Size: {os.path.getsize(output_filename) / (1024 * 1024):.2f} MB")

if __name__ == "__main__":
    source_dir = r"c:\Users\tejat\OneDrive\Desktop\propaganda_detector_final_professional"
    output_zip = r"c:\Users\tejat\OneDrive\Desktop\SENTINEL_Shareable.zip"
    create_export_zip(source_dir, output_zip)
