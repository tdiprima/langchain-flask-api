The error message:

```
"Unexpected error: NotFoundError: Error code: 404 - {'error': {'code': 'DeploymentNotFound', 'message': 'The API deployment for this resource does not exist...'}}"
```

indicates that your **Azure OpenAI deployment name is either incorrect, missing, or not yet fully set up**.

### ✅ **Steps to Fix:**
#### 1️⃣ **Verify Environment Variables**
Double-check your `.env` file or environment variables to ensure they are correctly set:

```sh
echo $AZURE_OPENAI_API_KEY
echo $AZURE_OPENAI_ENDPOINT
echo $AZURE_OPENAI_API_VERSION
echo $AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
```

Make sure:

- `AZURE_OPENAI_API_KEY` is correctly copied from your Azure OpenAI resource.
- `AZURE_OPENAI_ENDPOINT` follows the format:  
  ```
  https://<your-resource-name>.openai.azure.com/
  ```
- `AZURE_OPENAI_API_VERSION` is set to the correct version (e.g., `2023-03-15-preview` or latest).
- `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` matches **exactly** with the deployment name in Azure.

#### 2️⃣ **Verify Your Azure OpenAI Deployment**
Run the following command (replace `<your-resource-name>` with your actual Azure resource name):

```sh
curl -X GET "https://<your-resource-name>.openai.azure.com/openai/deployments?api-version=2023-03-15-preview" \
  -H "api-key: YOUR_AZURE_OPENAI_API_KEY"
```

- If the deployment name is missing, **you need to create it in Azure**.

#### 3️⃣ **Check in Azure Portal**
1. **Go to [Azure Portal](https://portal.azure.com/)**
2. **Navigate to your OpenAI Resource**
3. Click **"Deployments"** in the sidebar.
4. Check if:
   - The deployment exists.
   - The model (e.g., `gpt-4`) is assigned to the deployment.
   - The deployment name **matches exactly** what you set in `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`.

#### 4️⃣ **Fix the Deployment Name in Your Code**
If the deployment name is incorrect, update it in your `.env` file:

```sh
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=correct_deployment_name
```

Then, restart your Flask server:

```sh
python app.py
```

#### 5️⃣ **Wait a Few Minutes & Try Again**
If you just created the deployment, **wait 5–10 minutes** before trying again, as Azure sometimes takes time to fully activate the deployment.

---

### 🔄 **Retry the API Call**
Once everything is fixed, test again:

```sh
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the capital of California?"}'
```

---

### 🚀 **Final Thoughts**
This issue is usually caused by:

- **Wrong deployment name**
- **Azure OpenAI deployment not yet created**
- **Azure service delay after creation**

After fixing these, your API should work! 🎯 Let me know if you need further debugging. 🚀

<br>
