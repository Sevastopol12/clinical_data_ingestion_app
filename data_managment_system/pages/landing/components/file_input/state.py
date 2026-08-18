import reflex as rx
import pandas as pd
from io import BytesIO

class FileInputState(rx.State):
    @rx.event(background=True)
    async def read_files(files: list[rx.UploadFile]):
        for file in files:
            raw_bytes = await file.read()
            
            buffer = BytesIO(raw_bytes)
            
            df = pd.read_excel(buffer)
            
        
    
            
            