from flask import Flask, request, jsonify, make_response
import gspread
from google.oauth2.service_account import Credentials
import json
import base64
import requests

app = Flask(__name__)

# === Chave codificada direto no código ===
GOOGLE_CREDENTIALS_BASE64 = """
ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAidml0dGFnby00NjYzMTgiLAogICJwcml2YXRlX2tleV9pZCI6ICI0ZmE0NjVhNjE1NTNiZDUwNDc1Mzk2MGE5ODc2YmI5OWY0NTBlYWU2IiwKICAicHJpdmF0ZV9rZXkiOiAiLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdmdJQkFEQU5CZ2txaGtpRzl3MEJBUUVGQUFTQ0JLZ3dnZ1NrQWdFQUFvSUJBUUNsb3djU1Iydk0rWWhFXG5mRjRpQkxqZC9kSGs1cVVyRXBZWXRwbjVKZ3J2am4xUnNpbThFR3psMnpHSkJvRGh0a0pCRW9TRmcwZnprVUY0XG5mOURSVWo3WkNlNm1xaWR6VFNmY0plU1RhSldNcVE0VmwzemZsdWlsNXVJOEhjWnVIa2FLczd5S2VmdUtnTFc1XG5RNHdmQ0VJenN1UHBOdkVmVXRSeU8xdXg4MElXYitPYUx3cGZ5NlE0Si8zNmcxczVxT3VKZFdkaUg1anB2ZGlrXG5JTVcxR1kwWTMrbnNML21Dc2VpY2N6UmRadEZNL3ZJRXBrU1VMMkpvbkRXUmhnM250bGkvRkxXN3JMSGV4a0FTXG40VkdTM2trT1VQRWtFdVpNY2FnbUdIbGRCYVcvN3hzcXdGU0dBTlRiZW9KcWF0SUpubHd6cllDdEswRVJwYXlZXG45MDVYS09kaEFnTUJBQUVDZ2dFQUhWdjYxbVliZVE4bjlMKzRyYjM1aUx2RFZ4Zjg0ZGdmQzgxZUdIZ0NTemtPXG5CSXVZY3pIVUk2QUpOVGtXWWl1OHJhMGJHVkZPVVNHSG9kVENEa0JPVElsQ3FIOFRsQS95aDBhZUwvVERRVlg3XG4zWjdtN3ZqZ1R2dlFVUWlVRWhQQ3ZEWWtyc1QxYmJUbndTbDBibEczN2xNQXErZGxzUUF0RVB4dGdlclU1WVh4XG5mV1BPWDFpakVvSzQvdURQL1dzYUY4RzEyYnh5VDQvWDVocjFNUG9ERHMrN0Ivam9RY2w0cW02Mm9hOHRjeW1aXG55SFFtLzd4ZEZISUZJTzh6YzhnSnNSQW1IV2JxSFhVVTlva1hsUStvU1gxWFhxRjNQYnhDdnlkU3IxMm9xcC9nXG5yTGUvYyt4akpKYWhub2k1b2RRUGRtNTMwOWo0U0Q0Nm51V0pVeDJ3WXdLQmdRRGNqRDdDNjRHSlY5Qk5BRHZiXG5veDhmN3RSL1o2UEJCNHJ6UlJQb2F4anAvampnUlpvTmFuWFExODBHZXhVNUsvNkNsTlQ4OUVCcytuL3crWG5qXG5GVUUxRVg3YTVVRjZLREFSd09TQzVKc2xqaHlDVEdYZjFZemlJT0l2WDBrWUtiWUZRcTltb2hEaHR4dHQ2dHY3XG5HU1h1OXpGVTJlOTdyQ2orYXBkT1NEdWp6d0tCZ1FEQVF5UlRnV2JTWVYzR0NFbldXRlhHZU8wa21CY2J1ZWtnXG5QQ0tDaEg4eXl4Uk52aFEvY3BzaGtPVjk3VXd6L2xYZGhrWjNRdkxmM0Fnb01ENDZiTlRROS9vVCtBOEFOdDBBXG5KaHdDa0ozTE5DN25sbE95MXBlTEJ3ejQyREFZZVFBSTI2N0ZHeUpRdHQ4WGpzKzV5RXFsN1ovODFYOHVhWG5BXG5uT1BqOTg4ZHp3S0JnUURVWHN1MG9GaGM2MDB1U0hKYlBja2owN09WZHpQdEZSbE14WkMwOWlQSWRqOUlYbDFJXG5XK0pWRnVoYlBEd2trR09FVkZKL3ZhY29DVk1YdFBNVW9vdm0wUkVKTVVjS25SWWtra3k0YWUrbml4K1NySVJRXG50Rzd6OUZ3NDU1VVlDbG8yMkk3VDBtMVZIQi95aVB3STM1OXlhMTk2YUYwK0JucDIraWIyZjRIR2F3S0JnQjI1XG5RNkIxWFFRaGNYSHdUaG9KUmhtTkVIeWIxdGErZzBBc2k5bEp5ckI3blFQMzR3RjhJbWVxRXhESTR3TVd5d2VZXG5mc1JwWVVzaXBWQXhSUzJiTGJ1dzJzVERrTzRqalQ4OHBRL3djN1M2dUpXdE0vdHVHYmV3dTF5dGI2SVk4dHhyXG51alZXNEpOQjhuT2Q3SmQ0VTdJYmJxU1VEVG1MclBzT1JsMDBMcDBaQW9HQkFNeThzeEdVVnl5Q0hTbk8vMjBoXG5ZVkllTGM2VFhzNUtwOW9LWWpLRThOYUk1Nk5NaUVQRXh5SllzdXgvQkFXcnpwTW9KWm5idC9QN2VTbG9uYllXXG5XR2xtUXloNFFtWjRwdjZBbmQ5MloxT21lTjN0MWtPOGMrYjJwVXNsZ245VlNGV3I1cUtrNGJlUGxaNWhzOUwvXG5jWTZhOVpEUVJhTHJFZHVsUG9iSnlHUmlcbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsCiAgImNsaWVudF9lbWFpbCI6ICJ2aXR0YWdvcGxhbmlsaGFzQHZpdHRhZ28tNDY2MzE4LmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjEwMjY0Nzc1Nzg3OTQzODA0ODEzNCIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvdml0dGFnb3BsYW5pbGhhcyU0MHZpdHRhZ28tNDY2MzE4LmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAidW5pdmVyc2VfZG9tYWluIjogImdvb2dsZWFwaXMuY29tIgp9Cg==
""".strip()

STRIPE_SECRET_KEY_BASE64 = """
c2tfbGl2ZV81MVJuZ0QyQW13UlhOVGlGRGgwVkpxM2NJbFFTSWI1RUxvN2dudnlPRXQ4SmhJUzJwSDM2cDRuTVBRS29mblBZZWhwZVFRb3VWeXhVMG9LbXg2Z0JxWFVJRjAwS0RuYlJUNWs=
""".strip()

STRIPE_SECRET_KEY = "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"


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

    # 1. Recebe e trata uma requisição de estorno via AppSheet
    if payload.get("acao") == "cancelar_assinatura":
        subscription_id = payload.get("subscription_id", "").strip()
        if not subscription_id:
            return make_response("subscription_id ausente", 400)

        try:
            # Chamada para cancelar assinatura
            response = requests.delete(
                f"https://api.stripe.com/v1/subscriptions/{subscription_id}",
                auth=(STRIPE_SECRET_KEY, "")
            )

            if response.status_code == 200:
                print(f"✅ Assinatura {subscription_id} cancelada com sucesso")
                return jsonify({"status": "assinatura cancelada"}), 200
            else:
                print(f"❌ Falha ao cancelar assinatura: {response.text}")
                return make_response("Erro ao cancelar", 500)
        except Exception as e:
            print(f"❌ Erro interno ao cancelar: {e}")
            return make_response("Erro interno", 500)

    # 2. Recebe e trata eventos normais do Stripe
    event_type = payload.get("type")
    data = payload.get("data", {}).get("object", {})

    cpf = data.get("client_reference_id")
    status = data.get("payment_status") or "desconhecido"
    subscription_id = data.get("subscription")

    print(f"📩 Evento: {event_type} | CPF: {cpf} | Status: {status} | Subscription: {subscription_id}")

    if not cpf:
        return make_response("CPF ausente no payload", 400)

    try:
        all_rows = worksheet.get_all_values()
        header = all_rows[0]

        col_cpf = 2  # Coluna B
        col_status = header.index("STATUS LINK PAGAMENTO") + 1
        col_status_final = 8  # Coluna H
        col_assinatura = header.index("ID ASSINATURA") + 1  # Coluna W

        for i, row in enumerate(all_rows[1:], start=2):
            cpf_planilha = row[col_cpf - 1].strip().zfill(11)
            cpf_recebido = cpf.strip().zfill(11)

            if cpf_planilha == cpf_recebido:
                worksheet.update_cell(i, col_status, status)

                if status.lower() == "paid":
                    worksheet.update_cell(i, col_status_final, "LIBERAÇÃO")

                    if subscription_id:
                        worksheet.update_cell(i, col_assinatura, subscription_id)

                print(f"✅ Linha {i} atualizada com status '{status}' e assinatura '{subscription_id}'")
                return jsonify({"status": "ok"}), 200

        print("❌ CPF não localizado na planilha")
        return make_response("CPF não encontrado", 404)

    except Exception as e:
        print(f"❌ Erro interno: {e}")
        return make_response("Erro interno", 500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
