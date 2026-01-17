import qrcode
import os

def generate_qr(token, booking_id: int) -> str:
    img = qrcode.make(token)
    
    folder = os.path.join("static" , "qr_codes")
    os.makedirs(folder, exist_ok=True)
    
    path = os.path.join(folder, f"booking_{booking_id}.png")
    img.save(path)
    return path