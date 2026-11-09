from threading import Thread
from flask import current_app, render_template
import requests

PROFESSOR_EMAIL = 'flaskaulasweb@zohomail.com'
PRONTUARIO = 'PT3036278'
NOME_ALUNO = 'Alice Francischette Blanco'


def unique_recipients(*addresses):
    seen = set()
    result = []
    for address in addresses:
        address = (address or '').strip()
        if address and address.lower() not in seen:
            seen.add(address.lower())
            result.append(address)
    return result


def _send_one(api_url, api_key, api_from, recipient, subject, body_text):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "personalizations": [{"to": [{"email": recipient}], "subject": subject}],
        "from": {"email": api_from},
        "content": [{"type": "text/plain", "value": body_text}]
    }
    try:
        resposta = requests.post(api_url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        print(f'[EMAIL] FALHA ao enviar para {recipient}: exceção {e}', flush=True)
        return False

    ok = 200 <= resposta.status_code < 300
    print(f'[EMAIL] {"OK" if ok else "FALHA"} para {recipient} - '
          f'status {resposta.status_code} - {resposta.text}', flush=True)
    return ok


def send_async_simple_message(app, recipients, subject, newUser):
    with app.app_context():
        full_subject = app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject

        body_text = (
            f"Prontuário: {PRONTUARIO}\n"
            f"Nome do aluno: {NOME_ALUNO}\n"
            f"Novo usuário cadastrado: {newUser}"
        )

        api_url = app.config.get('API_URL')
        api_key = app.config.get('API_KEY')
        api_from = app.config.get('API_FROM')

        if not api_url or not api_key:
            print('[EMAIL] ERRO: API_URL ou API_KEY não configurados. '
                  'Nenhum e-mail foi enviado.', flush=True)
            return

        recipients = unique_recipients(*recipients)
        print(f'[EMAIL] Enviando via API para: {recipients}', flush=True)

        results = {r: _send_one(api_url, api_key, api_from, r, full_subject, body_text)
                   for r in recipients}

        falhas = [r for r, ok in results.items() if not ok]
        if falhas:
            print(f'[EMAIL] ATENÇÃO: não entregue para: {falhas}', flush=True)
        else:
            print('[EMAIL] Todos os envios foram aceitos pela API.', flush=True)


def send_simple_message(recipients, subject, newUser):
    app = current_app._get_current_object()
    thr = Thread(target=send_async_simple_message, args=[app, recipients, subject, newUser])
    thr.start()
    return thr


def send_async_email(app, to, subject, text_body, html_body):
    with app.app_context():
        api_url = app.config.get('API_URL')
        api_key = app.config.get('API_KEY')
        if not api_url or not api_key:
            print('[EMAIL] ERRO: API_URL ou API_KEY não configurados. '
                  'Nenhum e-mail foi enviado.', flush=True)
            return
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "personalizations": [{"to": [{"email": to}], "subject": subject}],
            "from": {"email": app.config.get('API_FROM')},
            "content": [
                {"type": "text/plain", "value": text_body},
                {"type": "text/html", "value": html_body}
            ]
        }
        try:
            resposta = requests.post(api_url, json=payload, headers=headers, timeout=10)
            print(f'[EMAIL] status {resposta.status_code} para {to} - {resposta.text}', flush=True)
        except Exception as e:
            print(f'[EMAIL] FALHA ao enviar para {to}: exceção {e}', flush=True)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    full_subject = app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject
    text_body = render_template(template + '.txt', **kwargs)
    html_body = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email,
                 args=[app, to, full_subject, text_body, html_body])
    thr.start()
    return thr
