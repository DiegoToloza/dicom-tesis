import pydicom

# Ruta del archivo RTSTRUCT
#dicom_path = "C:/Users/whois/OneDrive/Desktop/Tesis/Datasets/Alberto/RS.ALBERTO YESCAS BANEGAS_.dcm"
dicom_path = "C:/Users/whois/OneDrive/Desktop/Tesis/Datasets/Hospital Naval/planes/PLANES APROBADOS/PACIENTE 1/RT_Structure_Set_Storage-"


# Cargar archivo
ds = pydicom.dcmread(dicom_path)

# ---- Información general ----
print(" Información general:")
print(" Información general del archivo RTSTRUCT:")
print(f" - Modality               : {ds.get('Modality', 'No especificado')}")
print(f" - SOP Class UID          : {ds.get('SOPClassUID', 'N/A')}")
print(f" - SOP Instance UID       : {ds.get('SOPInstanceUID', 'N/A')}")

print("\n Información del paciente:")
print(f" - Patient Name           : {ds.get('PatientName', 'N/A')}")
print(f" - Patient ID             : {ds.get('PatientID', 'N/A')}")
print(f" - Patient Birth Date     : {ds.get('PatientBirthDate', 'N/A')}")
print(f" - Patient Sex            : {ds.get('PatientSex', 'N/A')}")

print("\n Información del estudio:")
print(f" - Study Instance UID     : {ds.get('StudyInstanceUID', 'N/A')}")
print(f" - Study ID               : {ds.get('StudyID', 'N/A')}")
print(f" - Study Description      : {ds.get('StudyDescription', 'N/A')}")
print(f" - Study Date             : {ds.get('StudyDate', 'N/A')}")
print(f" - Study Time             : {ds.get('StudyTime', 'N/A')}")

print("\n Información de la institución:")
print(f" - Institution Name       : {ds.get('InstitutionName', 'N/A')}")
print(f" - Manufacturer           : {ds.get('Manufacturer', 'N/A')}")
print(f" - Operators' Name        : {ds.get('OperatorsName', 'N/A')}")

print("\n Referencias espaciales:")
print(f" - Frame of Reference UID : {ds.ReferencedFrameOfReferenceSequence[0].FrameOfReferenceUID}")
#print(f" - Referenced Study UID   : {ds.ReferencedStudySequence[0].ReferencedSOPInstanceUID}")
#print(f" - Referenced Series UID  : {ds.ReferencedStudySequence[0].ReferencedSeriesSequence[0].SeriesInstanceUID}")
print()

# ---- ROIs definidos ----
print("ROIs (Regiones de interés):")
for roi in ds.StructureSetROISequence:
    print(f" - ROI #{roi.ROINumber} - {roi.ROIName}")

print()

# # ---- Contornos asociados a cada ROI ----
# print("Contornos definidos:")
# for i, roi_contour in enumerate(ds.ROIContourSequence):
#     roi_number = ds.StructureSetROISequence[i].ROINumber
#     roi_name = ds.StructureSetROISequence[i].ROIName
#     num_contours = len(roi_contour.ContourSequence)
#     print(f" - ROI #{roi_number} '{roi_name}' tiene {num_contours} contornos")

#     for j, contour in enumerate(roi_contour.ContourSequence):
#         num_points = contour.NumberOfContourPoints
#         print(f"   -> Contorno {j+1} con {num_points} puntos")
#         if num_points > 0:
#             print(f"      - Tipo de contorno: {contour.ContourGeometricType}")
#         else:
#             print("      -  Contorno vacío")