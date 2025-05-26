import pydicom
import pandas as pd

# Rutas actualizadas a tus archivos RTSTRUCT
file1_path = "C:/Users/whois/OneDrive/Desktop/Tesis/Datasets/Alberto/RS.ALBERTO YESCAS BANEGAS_.dcm"
file2_path = "C:/Users/whois/OneDrive/Desktop/Tesis/Datasets/Hospital Naval/planes/PLANES APROBADOS/PACIENTE 1/RT_Structure_Set_Storage-"

def extract_roi_info(filepath):
    ds = pydicom.dcmread(filepath)
    roi_info = []
    for roi in ds.StructureSetROISequence:
        roi_info.append((roi.ROINumber, roi.ROIName))
    return sorted(roi_info)

# Extraer info
roi_info1 = extract_roi_info(file1_path)
roi_info2 = extract_roi_info(file2_path)

# Igualar longitud de listas
max_len = max(len(roi_info1), len(roi_info2))
roi_info1 += [("", "")] * (max_len - len(roi_info1))
roi_info2 += [("", "")] * (max_len - len(roi_info2))

# Crear DataFrame
df = pd.DataFrame({
    "ROI_Number_File1": [roi[0] for roi in roi_info1],
    "ROI_Name_File1": [roi[1] for roi in roi_info1],
    "ROI_Number_File2": [roi[0] for roi in roi_info2],
    "ROI_Name_File2": [roi[1] for roi in roi_info2],
})

# Mostrar resultado
print(df.to_string(index=False))