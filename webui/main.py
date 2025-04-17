import streamlit as st
import requests

API_BASE_URL = "http://localhost/api/v1"

if not st.session_state.get("access_token"):
    st.session_state.access_token = None

st.title("Streamlit App для взаимодействия с FastAPI")

st.subheader("Регистрация нового пользователя")
email = st.text_input("Имя пользователя:", key="email_for_create")
password = st.text_input("Пароль:", type="password", key="password_for_create")

if st.button("Зарегистрировать пользователя"):
    if email and password:
        try:
            endpoint = f"{API_BASE_URL}/users/"
            payload = {"email": email, "password": password}
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            st.success("Пользователь успешно зарегистрирован!")
        except Exception as e:
            st.error(f"Ошибка регистрации пользователя: {e}")
    else:
        st.warning("Заполните все поля для регистрации пользователя.")


st.header("Аутентификация")

email = st.text_input("Имя пользователя:")
password = st.text_input("Пароль:", type="password")

if st.button("Войти"):
    if email and password:
        try:
            endpoint = f"{API_BASE_URL}/users/login/"
            payload = {"email": email, "password": password}
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            token_pair = response.json()
            st.session_state.access_token = token_pair['access_token']
            st.success("Успешная аутентификация!")
        except Exception as e:
            st.error(f"Ошибка аутентификации: {e}")
    else:
        st.warning("Введите имя пользователя и пароль.")

if st.session_state.access_token:
    st.success("Вы авторизованы!")
else:
    st.warning("Войдите, чтобы продолжить использовать защищенные эндпойнты.")


st.header("Баланс Пользователя")
if st.button("Получить баланс"):
    try:
        endpoint = f"{API_BASE_URL}/users/balance/"
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        balance = response.json()
        st.success("Баланс успешно получен!")
        st.write(f"Баланс пользователя: {balance}")
    except Exception as e:
        st.error(f"Ошибка получения баланса: {e}")

amount = st.number_input("Выберите сумму для пополнения баланса", min_value=1, step=1)

if st.button("Пополнить баланс"):
    try:
        endpoint = f"{API_BASE_URL}/users/pay/"
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        params = {"amount": amount}
        response = requests.post(endpoint, params=params, headers=headers)
        response.raise_for_status()
        balance_info = response.json()
        st.success("Баланс успешно пополнен!")
    except Exception as e:
        st.error(f"Ошибка пополнения баланса: {e}")

if st.button("Получить список чатов"):
    try:
        endpoint = f"{API_BASE_URL}/chats/"
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        chats = response.json()
        st.json(chats)
    except Exception as e:
        st.error(f"Ошибка получения списка чатов: {e}")

st.subheader("Создать новый чат")

chat_type_choices = ["only_rag", "with_llm"]
chat_type = st.selectbox("Выберите тип чата:", chat_type_choices)

if st.button("Создать чат"):
    if chat_type:
        try:
            endpoint = f"{API_BASE_URL}/chats/"
            payload = {"type": chat_type}
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}  # Передача токена
            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            st.success("Чат успешно создан!")
            st.json(response.json())
        except Exception as e:
            st.error(f"Ошибка создания чата: {e}")
    else:
        st.warning("Выберите тип чата.")

chat_id = st.number_input("ID чата:", min_value=1, step=1)
message_text = st.text_area("Введите сообщение для отправки в чат:")

if st.button("Отправить сообщение"):
    if chat_id and message_text:
        try:
            endpoint = f"{API_BASE_URL}/chats/{chat_id}/"
            payload = {"message": message_text}
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            st.success("Сообщение успешно отправлено!")
            st.json(result)
        except Exception as e:
            st.error(f"Ошибка отправки сообщения: {e}")
    else:
        st.warning("Укажите ID чата и текст сообщения.")
