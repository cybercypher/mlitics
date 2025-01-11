# mlitics


---


#### **Key Changes:**
- The **API key** is passed as a **query parameter (`api_key`)** or via an **Authorization header**.
- If the API key is not provided, the app will return an **error response**.
- Uses **multi-threading** with `ThreadPoolExecutor`.
---

### 🔧 **How to Run the Flask App**
1. Save the code as `app.py`.
2. Run the Flask app:

```bash
python app.py
```

---

### 🧪 **Example API Requests**

#### **1️⃣ Fetch Mentions by Keyword (API Key as Query Parameter)**
```bash
curl "http://localhost:5000/mentions?api_key=your_api_key_here&keyword=OpenAI&project_id=123"
```

#### **2️⃣ Fetch Mentions (API Key in Authorization Header)**
```bash
curl -H "Authorization: your_api_key_here" \
"http://localhost:5000/mentions?keyword=OpenAI&project_id=123"
```

#### **3️⃣ Create a New Alert**
```bash
curl -X POST "http://localhost:5000/alerts?api_key=your_api_key_here" \
-H "Content-Type: application/json" \
-d '{"project_id": "123", "name": "AI Monitoring", "keywords": ["OpenAI", "Anthropic"]}'
```

#### **4️⃣ Get All Alerts for a Project**
```bash
curl "http://localhost:5000/alerts?api_key=your_api_key_here&project_id=123"
```

---

### 🔒 **Security Best Practices**
1. Store the **API key in environment variables** and retrieve it when needed.
2. Use **HTTPS** when deploying to production.
3. Add **authentication and rate limiting** to your Flask app.

