import streamlit as st 
import pandas as pd
import openpyxl
from io import BytesIO
import xlsxwriter
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple

lato_fornace = "sinistra"

coordinates = [
                                          (4,15),(7,15),(10,15),(13,15),
                           (-2,13),(1,13),(4,12),(7,12),(10,12),(13,12),(16,12),
                   (-5,11),(-2,10),(1,10), (4,9), (7,9), (10,9), (13,9), (16,9),
            (-8,8),(-5,8), (-2,7), (1,7),  (4,6), (7,6), (10,6), (13,6), (16,6),
          (-8, 5), (-5, 5), (-2, 4), (1, 4), (4, 3), (7, 3), (10, 3), (13, 3), (16, 3),
           (-11, 2), (-8, 2), (-5, 2),                  (4, 0), (7, 0), (10, 0), (13, 0), (16, 0),
(-14, -1), (-11, -1), (-8, -1), (-5, -1),                               (10, -3), (13, -3), (16, -3),
(-15, -4), (-12, -4), (-9, -4), (-6, -4), (-3, -4),(0, -4),             (10, -6), (13, -6), (16, -6),
(-15, -7), (-12, -7), (-9, -7), (-6, -7), (-3, -7),(0, -7),             (10, -9), (13, -9), (16, -9),
(-15, -10), (-12, -10), (-9, -10), (-6, -10), (-3, -10),(1, -10),(4, -10), (7, -10),
(-15, -13), (-12, -13), (-9, -13), (-6, -13), (-3, -13),(0, -13),(3, -13), (6, -13), (9, -13), (12, -13), (15, -13),
            (-12, -16), (-9, -16), (-6, -16), (-3, -16),(0, -16),(3, -16), (6, -16), (9, -16), (12, -16), (15, -16)
]

coordinates = []
for x in range(-18, 18, 3):
    for y in range(-18, 18, 3):
        if not((x > -6) and (x < 3) and (y > -3) and (y < 6)):
            coordinates.append((x,y))


buffer = BytesIO()
st.markdown("# HL5 Grid Composer")

st.write("Ciao questa è la pagina di calcolo della griglia dell'alleanza Held Server 434")
categories = ["MUSA", "MAGGIORDOMO", "SIG.GUERRA", "RECRUITER", "R5", "R4+", "R4", "R3+", "R3", "R2", "R1", "R0"]
grid_size = 15
grid_step = 3
max_offset = grid_size

class Coordinate:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    @classmethod
    def from_str(cls, input):
        if not input:
            return 
        x, y = map(int, input.split(':'))
        return cls(x=x, y=y)
    
    def __repr__(self) -> str:
        return f'{self.x}:{self.y}'
    
    def __add__(self, other_coord):
        return self.x + other_coord.x, self.y + other_coord.y

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def get_distance_from_coordinate(self, other) -> float:
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


# Funzione per trovare le celle vicine al centro
def get_nearest_cells(center: Coordinate, grid_size: int) -> List[Tuple[float, Coordinate]]:
    cells = []
    for x in range(center.x - grid_size, center.x + grid_size + 1, grid_step):
        for y in range(center.y - grid_size, center.y + grid_size + 1, grid_step):
            current_cell = Coordinate(x, y)
            if current_cell != center:
                distance = current_cell.get_distance_from_coordinate(center)
                cells.append((distance, current_cell))
    cells.sort(key=lambda x: x[0])  # Ordina per distanza dal centro
    return cells

# Funzione per assegnare le celle agli oggetti
    """def assign_cells_to_members(members: pd.DataFrame, center: Coordinate, grid_size: int) -> List[Tuple[str, Coordinate]]:
    cells = get_nearest_cells(center, grid_size)
    assigned_cells = []
    for index, row in members.iterrows():
        if cells:
            _, cell = cells.pop(0)
            assigned_cells.append((row["Nickname"], cell))
            members.at[index, 'Nuove Coordinate'] = "{}".format(cell)
    return assigned_cells"""
def assign_cells_to_members(members: pd.DataFrame, center: Coordinate, grid_size: int) -> List[Tuple[str, Coordinate]]:
    cells = []
    for coo in coordinates:
        # if "{}".format(lato_fornace) == "sinistra":
        #    current_cell = Coordinate(x=coo[0] - 5 + center.x, y=coo[1] +5 + center.y) 
        #else:
        #    current_cell = Coordinate(x=coo[0] + 5 + center.x, y=coo[1] +5 + center.y)
        
        current_cell = Coordinate(x=coo[0] + center.x +1, y=coo[1] + center.y - 1)
        cells.append((current_cell.get_distance_from_coordinate(center), current_cell))
        cells.sort(key=lambda x: x[0])  # Ordina per distanza dal centro
    assigned_cells = []
    for index, row in members.iterrows():
        if cells:
            _, cell = cells.pop(0)
            assigned_cells.append((row["Nickname"], cell))
            members.at[index, 'Nuove Coordinate'] = "{}".format(cell)
    return assigned_cells


def create_grid(df: pd.DataFrame, center: Coordinate):
    board_size = 19
    # if "{}".format(lato_fornace) == "sinistra":
    #    x_range = (center.x - board_size -5, center.x + board_size -5)
    #else:
    #    x_range = (center.x - board_size + 5, center.x + board_size + 5)
    
    x_range = (center.x - board_size, center.x + board_size)
    # Creazione della scacchiera
    fig, ax = plt.subplots()
    for y in range(center.y - board_size , center.y + board_size):
        ax.axhline(y, color='black', linewidth=0.5)  # Linee orizzontali
    for x in range(*x_range):
        ax.axvline(x, color='black', linewidth=0.5)  # Linee verticali
    for index, row in df.iterrows():
        # st.write(row["Nickname"] + " ---> " + str(row["Nuove Coordinate"]))
        coord = Coordinate.from_str(row["Nuove Coordinate"])
        ax.add_patch(plt.Rectangle((coord.x, coord.y), 1, 1, color='red', alpha=0.6))  # Riempi la cella con un colore 
        ax.text(coord.x + 0.5, coord.y + 0.5, row["Nickname"], color='black', ha='center', va='center', fontsize=4)  
    
    ax.add_patch(plt.Rectangle((center.x, center.y), 1, 1, color='violet', alpha=0.6))  # Riempi la cella con un colore 
    ax.text(center.x + 0.5, center.y + 0.5, "Marshall", color='black', ha='center', va='center', fontsize=4)
    #if "{}".format(lato_fornace) == "sinistra":
    #    ax.add_patch(plt.Rectangle((center.x - 5, center.y + 5), 1, 1, color='orange', alpha=0.6))  # Riempi la cella con un colore 
    #    ax.text(center.x - 4.5, center.y + 5.5, "Furnace", color='black', ha='center', va='center', fontsize=4)  
    #else:
    #    ax.add_patch(plt.Rectangle((center.x + 5, center.y + 5), 1, 1, color='orange', alpha=0.6))  # Riempi la cella con un colore 
    #    ax.text(center.x + 5.5, center.y + 5.5, "Furnace", color='black', ha='center', va='center', fontsize=4)  
    
    return fig


def quadrato_concentrico(coord: Coordinate, d: int):
    # Lista per memorizzare tutte le coordinate del perimetro del quadrato
    perimetro = []
    
    # Lati orizzontali (superiore e inferiore)
    for i in range(-d, d, step_distanza):
        perimetro.append(str(Coordinate(coord.x + i, coord.y - d)))  # Lato inferiore
        perimetro.append(str(Coordinate(coord.x + i, coord.y + d)))  # Lato superiore
    
    # Lati verticali (sinistro e destro)
    for i in range(-d, d, step_distanza):  # Escludiamo gli angoli già considerati
        perimetro.append(str(Coordinate(coord.x - d, coord.y + i)))  # Lato sinistro
        perimetro.append(str(Coordinate(coord.x + d, coord.y + i)))  # Lato destro

    return perimetro

members_data = pd.DataFrame()
mare_coo = st.text_input("Coordinate del maresciallo", value="104:557", max_chars=7, key=None, type="default")
lato_fornace = option = st.selectbox(
    "Lato della fornace",
    ("sinistra", "destra"),
)
fileUploadLabel = "carica l'excel con i dati dell'alleanza"
uploadedFile = st.file_uploader(fileUploadLabel, type=['csv','xlsx'],accept_multiple_files=False,key="fileUploader")
step_distanza = 3

center_coo = Coordinate.from_str(mare_coo)


if uploadedFile:
    if "{}".format(lato_fornace) == "destra":
        coordinates = [(-item[0], item[1]) for item in coordinates]

    members_data = pd.read_excel(uploadedFile)
    # wb = openpyxl.load_workbook(uploadedFile, read_only=True)
    # st.info(f"File uploaded: {uploadedFile.name}")
    # st.info(f"Sheet names: {wb.sheetnames}")

    # ring = [quadrato_concentrico(Coordinate.from_str(mare_coo), step_distanza * i) for i in range(1,6)] 
    # available_pos = [quadrato_concentrico(Coordinate.from_str(mare_coo), step_distanza * i) for i in range(1,6)]
    members_data['Ruolo'] = members_data['Ruolo'].str.upper()
    members_data['Ruolo'].fillna("R1", inplace=True)
    members_data['Ruolo'] = members_data['Ruolo'].str.strip()
    members_data['category_order'] = members_data['Ruolo'].apply(lambda x: categories.index(x))

    ordered_members = members_data.sort_values(by=['category_order', 'Potenza'], ascending=[True, False])
    assign_cells_to_members(ordered_members, center_coo, grid_size)
    results = ordered_members

             
    st.write(results)
    st.title("Griglia delle Posizioni")
    st.write("Questa applicazione visualizza una griglia di oggetti con i loro nomi alle coordinate date.")

    # Crea e mostra la griglia
    fig = create_grid(results, Coordinate.from_str(mare_coo))
    st.pyplot(fig)
    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    # Write each dataframe to a different worksheet.
        results.to_excel(writer, sheet_name='Sheet1', index=False)

        download2 = st.download_button(
            label="Download data as Excel",
            data=buffer,
            file_name='large_df.xlsx',
            mime='application/vnd.ms-excel'
        )
else:
    st.warning("Devi caricare il file excel per continuare")
