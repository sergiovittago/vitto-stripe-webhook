from flask import Flask, request, jsonify, make_response
import gspread
from google.oauth2.service_account import Credentials
import json
import base64

app = Flask(__name__)

# === Chave codificada direto no código ===
GOOGLE_CREDENTIALS_BASE64 = """
SEU_BLOCO_DE_CREDENCIAIS_AQUI
""".strip()

# === Autenticação com Google Sheets ===
cred_dict = json.loads(base64.b64decode(GOOGLE_CREDENTIALS_BASE64).decode("utf-8"))
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDS = Credentials.from_service_account_info(cred_dict, scopes=SCOPES)
client = gspread.authorize(CREDS)

# === Abre a planilha e aba correta ===
sheet = client.open_by_key("1qSl0p3z8Y8gZc5YJ4zLE7hS4RO6akd0mTsG4zpJonqc")
worksheet = sheet.worksheet("PESSOA FISICA")

@app.route("/webhook-stripe", methods=["POST"])
def webhook_stripe():
    payload = request.json
    event_type = payload.get("type")
    data = payload.get("data", {}).get("object", {})

    cpf = data.get("client_reference_id")
    status = data.get("payment_status") or "desconhecido"

    print(f"📩 Evento: {event_type} | CPF: {cpf} | Status: {status}")

    if not cpf:
        return make_response("CPF ausente no payload", 400)

    try:
        all_rows = worksheet.get_all_values()
        header = all_rows[0]

        col_cpf = 2  # Coluna B
        col_status = header.index("STATUS LINK PAGAMENTO") + 1
        col_status_final = 8  # Coluna H

        for i, row in enumerate(all_rows[1:], start=2):
            cpf_planilha = row[col_cpf - 1].strip().zfill(11)
            cpf_recebido = cpf.strip().zfill(11)

            if cpf_planilha == cpf_recebido:
                worksheet.update_cell(i, col_status, status)

                if status.lower() == "paid":
                    worksheet.update_cell(i, col_status_final, "LIBERAÇÃO")

                print(f"✅ Linha {i} atualizada com status '{status}'")
                return jsonify({"status": "ok"}), 200

        print("❌ CPF não localizado na planilha")
        return make_response("CPF não encontrado", 404)

    except Exception as e:
        print(f"❌ Erro interno: {e}")
        return make_response("Erro interno", 500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)