import os
import pydicom
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def cargar_contorno_y_imagenes(folder_path):
    """ Carga el archivo de contorneo y todas las imágenes DICOM en la carpeta """
    imagenes = {}  
    contorno_dicom = None  

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        try:
            dicom_data = pydicom.dcmread(file_path)
            
            if filename.startswith("RT_Structure_Set_Storage-"):
                contorno_dicom = dicom_data
            
            elif hasattr(dicom_data, "PixelData"):  
                imagenes[dicom_data.SOPInstanceUID] = {
                    "dicom": dicom_data,
                    "filename": filename  
                }
        
        except Exception as e:
            print(f"Error al leer {filename}: {e}")

    return contorno_dicom, imagenes

def extraer_contornos_por_imagen(contorno_dicom):
    """ Extrae los contornos y los asocia a cada imagen """
    contornos_por_imagen = {}

    if hasattr(contorno_dicom, "ROIContourSequence"):
        for roi_contour in contorno_dicom.ROIContourSequence:
            roi_number = roi_contour.ReferencedROINumber  
            
            for contour in roi_contour.ContourSequence:
                if hasattr(contour, "ContourImageSequence"):
                    for image_ref in contour.ContourImageSequence:
                        image_uid = image_ref.ReferencedSOPInstanceUID  
                        
                        if image_uid not in contornos_por_imagen:
                            contornos_por_imagen[image_uid] = []
                        
                        contornos_por_imagen[image_uid].append({
                            "roi_number": roi_number,
                            "contour_data": np.array(contour.ContourData).reshape(-1, 3)  
                        })
    
    return contornos_por_imagen

def extraer_nombres_rois(contorno_dicom):
    """ Extrae los nombres de los órganos y sus IDs """
    organ_dict = {}

    if hasattr(contorno_dicom, "StructureSetROISequence"):
        for roi in contorno_dicom.StructureSetROISequence:
            organ_dict[roi.ROINumber] = roi.ROIName

    return organ_dict

def transformar_coordenadas(contorno_data, dicom_image):
    """ Convierte coordenadas de paciente a coordenadas de píxeles, con mejor manejo de orientación """
    ipp = np.array(dicom_image.ImagePositionPatient)
    ps = np.array(dicom_image.PixelSpacing)
    rows, cols = dicom_image.pixel_array.shape
    
    if hasattr(dicom_image, 'ImageOrientationPatient'):
        orientation = np.array(dicom_image.ImageOrientationPatient).reshape(2, 3)
        puntos_transformados = []
        for punto in contorno_data:
            v = punto - ipp
            x = np.dot(v, orientation[0]) / ps[0]
            y = np.dot(v, orientation[1]) / ps[1]
            x = np.clip(x, 0, cols - 1)
            y = np.clip(y, 0, rows - 1)
            puntos_transformados.append([x, y])
        return np.array(puntos_transformados)
    else:
        x = (contorno_data[:, 0] - ipp[0]) / ps[0]  
        y = (contorno_data[:, 1] - ipp[1]) / ps[1]  
        x = np.clip(x, 0, cols - 1)
        y = np.clip(y, 0, rows - 1)
        return np.vstack((x, y)).T  

def graficar_imagen_con_contorno(image_dicom, contornos, organ_dict):
    """ Muestra la imagen DICOM con su contorno con mejor visualización """
    if hasattr(image_dicom, 'pixel_array'):
        pixel_array = image_dicom.pixel_array
    else:
        print("Error: La imagen DICOM no contiene datos de píxeles.")
        return
    
    p_min, p_max = np.percentile(pixel_array, [2, 98])
    img_display = np.clip(pixel_array, p_min, p_max)
    img_display = (img_display - p_min) / (p_max - p_min)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(img_display, cmap="gray", origin="upper", zorder=1)
    
    image_uid = image_dicom.SOPInstanceUID
    if image_uid in contornos:
        print(f"Encontrados {len(contornos[image_uid])} contornos para esta imagen")
        
        for i, contorno in enumerate(contornos[image_uid]):
            roi_name = organ_dict.get(contorno["roi_number"], f"ROI {contorno['roi_number']}")
            color = plt.cm.tab10(i % 10)

            puntos_transformados = transformar_coordenadas(contorno["contour_data"], image_dicom)
            
            print(f"ROI {roi_name}: Rango X: {np.min(puntos_transformados[:, 0]):.1f}-{np.max(puntos_transformados[:, 0]):.1f}, "
                  f"Rango Y: {np.min(puntos_transformados[:, 1]):.1f}-{np.max(puntos_transformados[:, 1]):.1f}")
            
            ax.plot(puntos_transformados[:, 0], puntos_transformados[:, 1], 
                   color=color, label=roi_name, linewidth=2, zorder=2)
            ax.scatter(puntos_transformados[:, 0], puntos_transformados[:, 1], 
                      color=color, s=10, alpha=0.7, zorder=3)
    else:
        print(f"No se encontraron contornos para la imagen con UID: {image_uid}")
    
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax.set_title(f"Imagen: {image_dicom.SOPInstanceUID[-8:]}")
    plt.tight_layout()
    plt.show()

def encontrar_uid_por_nombre(imagenes, nombre_archivo):
    """ Busca el UID de una imagen según su nombre de archivo """
    for uid, data in imagenes.items():
        if data["filename"].lower() == nombre_archivo.lower():
            return uid
    return None

def mostrar_informacion_diagnostica(imagenes, contornos_por_imagen):
    """ Muestra información de diagnóstico sobre los archivos cargados """
    print("\n===== INFORMACIÓN DE DIAGNÓSTICO =====")
    print(f"Total de imágenes DICOM: {len(imagenes)}")
    print(f"Total de imágenes con contornos: {len(contornos_por_imagen)}")
    
    print("\nImágenes con contornos:")
    for uid in contornos_por_imagen.keys():
        for key, value in imagenes.items():
            if key == uid:
                print(f"- {value['filename']} tiene {len(contornos_por_imagen[uid])} contornos")

# Ruta de la carpeta con los archivos DICOM
folder_path = "C:/Users/whois/OneDrive/Desktop/Tesis/Datasets/Hospital Naval/planes/PLANES APROBADOS/PACIENTE 1"

# Cargar los archivos
contorno_dicom, imagenes = cargar_contorno_y_imagenes(folder_path)

if contorno_dicom is None:
    print("No se encontró el archivo de contorno (RT_Structure_Set_Storage-...)")
else:
    print(f"Archivo de contorno cargado: {contorno_dicom.filename}")

organ_dict = extraer_nombres_rois(contorno_dicom)
contornos_por_imagen = extraer_contornos_por_imagen(contorno_dicom)

mostrar_informacion_diagnostica(imagenes, contornos_por_imagen)

# Especificar la imagen que quieres visualizar
nombre_imagen = "CT_Image_Storage-107"

image_uid = encontrar_uid_por_nombre(imagenes, nombre_imagen)

if image_uid:
    print(f"\nInformación para imagen: {nombre_imagen}")
    print(f"UID: {image_uid}")
    
    if image_uid in contornos_por_imagen:
        print(f"La imagen tiene {len(contornos_por_imagen[image_uid])} contornos")
        graficar_imagen_con_contorno(imagenes[image_uid]["dicom"], contornos_por_imagen, organ_dict)
    else:
        print(f"La imagen {nombre_imagen} no tiene contornos en el archivo de contorneo.")
        plt.figure(figsize=(10, 10))
        plt.imshow(imagenes[image_uid]["dicom"].pixel_array, cmap="gray")
        plt.title(f"Imagen sin contornos: {nombre_imagen}")
        plt.show()
else:
    print(f"No se encontró la imagen {nombre_imagen} en la carpeta.")