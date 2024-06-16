import streamlit as st 
import pandas as pd
import openpyxl
from io import BytesIO
import xlsxwriter

buffer = BytesIO()
st.markdown("# HL5 Grid Composer")

st.write("Ciao questa è la pagina di calcolo della griglia dell'alleanza Held Server 434")

class Coordinate:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    @classmethod
    def from_str(cls, input):
        coord = input.split(':')
        return cls(x=int(coord[0]), y=int(coord[1]))
    
    def __repr__(self) -> str:
        return f'{self.x}:{self.y}'

members_data = pd.DataFrame()
mare_coo = st.text_input("Coordinate del maresciallo", value="104:557", max_chars=7, key=None, type="default")
fileUploadLabel = "carica l'excel con i dati dell'alleanza"
uploadedFile = st.file_uploader(fileUploadLabel, type=['csv','xlsx'],accept_multiple_files=False,key="fileUploader")

def quadrato_concentrico(coord: Coordinate, d: int):
    # Lista per memorizzare tutte le coordinate del perimetro del quadrato
    perimetro = []
    
    # Lati orizzontali (superiore e inferiore)
    for i in range(-d, d, 2):
        perimetro.append(str(Coordinate(coord.x + i, coord.y - d)))  # Lato inferiore
        perimetro.append(str(Coordinate(coord.x + i, coord.y + d)))  # Lato superiore
    
    # Lati verticali (sinistro e destro)
    for i in range(-d, d, 2):  # Escludiamo gli angoli già considerati
        perimetro.append(str(Coordinate(coord.x - d, coord.y + i)))  # Lato sinistro
        perimetro.append(str(Coordinate(coord.x + d, coord.y + i)))  # Lato destro

    return perimetro

if uploadedFile:
    members_data = pd.read_excel(uploadedFile)
    # wb = openpyxl.load_workbook(uploadedFile, read_only=True)
    # st.info(f"File uploaded: {uploadedFile.name}")
    # st.info(f"Sheet names: {wb.sheetnames}")
    ring = [quadrato_concentrico(Coordinate.from_str(mare_coo), 2*i) for i in range(1,5)] 
    available_pos = [quadrato_concentrico(Coordinate.from_str(mare_coo), 2*i) for i in range(1,5)]

    r45 = members_data[members_data['Ruolo'].isin(['r4', 'r5'])]
    r45['Ring'] = 1
    r45['OK'] = r45['Coordinate'].isin(ring[0])
    for index, row in r45.iterrows():
        if row['OK']:
            if row['Coordinate'] in available_pos[0]:
                available_pos[0].remove(row['Coordinate'])

    r45['Nuove Coordinate'] = None
    for index, row in r45.iterrows():
        if not row['OK']:
            r45.at[index, 'Nuove Coordinate'] = available_pos[0].pop(0)
            
    others = members_data.drop(members_data[members_data['Ruolo'].isin(['r4', 'r5'])].index, inplace = False)
    others.sort_values("Potenza", ascending=False, inplace=True)
    residual = others
    for ring_index in reversed(range(1, len(ring))):
        topn = 0
        for t in range(1, ring_index + 1):
            topn += len(ring[t])
        
        topn_members = others.nlargest(topn, 'Potenza')
        others.loc[topn_members.index, 'Ring'] = ring_index + 1
        others.loc[topn_members.index, 'OK'] = topn_members['Coordinate'].isin(ring[ring_index])
    
    for index, row in others.iterrows():
        if row['OK']:
            available_pos[int(row['Ring']-1)].remove(row['Coordinate'])
    for index, row in others.iterrows():
        if not row['OK']:
            others.at[index, 'Nuove Coordinate'] = available_pos[int(row['Ring']-1)].pop(0)
    results = pd.concat([r45, others])         
    st.write(results)

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



# st.write(members_data)

