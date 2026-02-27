import qrcode

def qr_code(asset_id):
    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4,
        )

        qr.add_data(asset_id)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        return img

    except Exception as e:
        print(f"QR Code Error: {e}")
        return None