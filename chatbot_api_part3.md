## Testing Conversation Persistence

Now that conversation persistence is implemented, you can test it with the following steps:

1. Start your Flask application:

    ```bash
    python chatbot_api_part3.py
    ```

2. Generate a new session ID:

    ```bash
    curl -X GET http://localhost:3000/generate-session
    ```

3. Use the session ID to ask questions (replace `YOUR_SESSION_ID` with the session ID you generated):

    ```bash
    curl -X POST http://localhost:3000/ask \
      -H "Content-Type: application/json" \
      -d '{"question":"What is artificial intelligence?", "session_id":"YOUR_SESSION_ID"}'
```

4. Restart your Flask application (press `Ctrl+C` to stop and then restart):

    ```bash
    python app.py
    ```

5. Verify your chat history is retained:

    ```bash
    curl -X GET "http://localhost:3000/history?session_id=YOUR_SESSION_ID"
    ```

6. Ask a follow-up question to confirm context maintenance:

    ```bash
    curl -X POST http://localhost:3000/ask \
      -H "Content-Type: application/json" \
      -d '{"question":"What are its main applications?", "session_id":"YOUR_SESSION_ID"}'
```

Register a new user

```sh
curl -X POST http://localhost:3000/register \ -H "Content-Type: application/json" \ -d '{"username":"testuser", "password":"password123"}'
```

Log in with the new user

```sh
curl -X POST http://localhost:3000/login \ -H "Content-Type: application/json" \ -d '{"username":"testuser", "password":"password123"}'
```

Use the session ID to ask questions

```sh
# Replace YOUR_SESSION_ID with the session ID from the login response
curl -X POST http://localhost:3000/ask \ -H "Content-Type: application/json" \ -d '{"question":"What is machine learning?", "session_id":"YOUR_SESSION_ID"}'
```

```sh
# Replace YOUR_SESSION_ID with the session ID from the login response
curl -X POST http://localhost:3000/logout \ -H "Content-Type: application/json" \ -d '{"session_id":"YOUR_SESSION_ID"}'
```

<br>
