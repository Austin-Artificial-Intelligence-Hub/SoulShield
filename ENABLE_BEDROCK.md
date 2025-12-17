# Enable AWS Bedrock Access

Your chatbot is deployed but needs Bedrock model access enabled.

## Quick Fix - Enable Claude Model Access:

1. **Go to AWS Bedrock Console:**
   https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess

2. **Click "Manage model access"** (orange button on the right)

3. **Find "Claude 3 Haiku"** in the list

4. **Check the box** next to "Claude 3 Haiku"

5. **Click "Request model access"** at the bottom

6. **Fill out the use case form:**
   - Use case: General purpose chatbot
   - Description: Customer service and educational assistant
   - Click Submit

7. **Wait 1-2 minutes** for approval (usually instant)

8. **Refresh the page** - Status should show "Access granted"

## Alternative: Use OpenAI Instead

If you prefer to use OpenAI instead of Bedrock:

1. Get an OpenAI API key from https://platform.openai.com/api-keys

2. Update your `.env` file:
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=your-openai-key-here
   ```

3. Redeploy:
   ```bash
   cdk deploy --require-approval never
   ```

## Test After Enabling

Once Bedrock access is enabled, try your chatbot again in Streamlit!
