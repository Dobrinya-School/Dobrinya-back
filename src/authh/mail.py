import base64
from googleapiclient.discovery import build
from google.oauth2 import service_account
from email.mime.text import MIMEText
import dotenv, json

GOOGLE_SERVICE_ACCOUNT_JSON = json.loads(dotenv.dotenv_values(".env").get("GOOGLE_SERVICE_ACCOUNT_JSON"))


SERVICE_ACCOUNT_FILE = "service-account-key.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Создаём credentials
credentials = service_account.Credentials.from_service_account_info(
    GOOGLE_SERVICE_ACCOUNT_JSON, scopes=SCOPES
)

# Для отправки от конкретного пользователя (делегирование домена)
delegated_credentials = credentials.with_subject("dobrinya-mail@dobrinya-486519.iam.gserviceaccount.com")

# Подключаемся к Gmail API
service = build("gmail", "v1", credentials=delegated_credentials)

# Создаём письмо
message = MIMEText("Тестовое письмо от сервиса")
message['to'] = "vladvarnovo@gmail.com"
message['from'] = "dobrinya-mail@dobrinya-486519.iam.gserviceaccount.com"
message['subject'] = "Тема письма"

# Преобразуем в base64
raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

# Отправляем
send_message = service.users().messages().send(
    userId="me",
    body={"raw": raw_message}
).execute()

print(f"Message Id: {send_message['id']}")
