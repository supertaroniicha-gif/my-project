# Google Cloud Function Setup - Daily Semiconductor News

This guide explains how to deploy the Cloud Function to Google Cloud Platform for daily 8 AM email delivery.

## Prerequisites

1. **Google Cloud Project**: Create one at [console.cloud.google.com](https://console.cloud.google.com)
2. **gcloud CLI**: Install from [cloud.google.com/sdk](https://cloud.google.com/sdk)
3. **Authentication**: Run `gcloud auth login`

## Setup Steps

### 1. Enable Required APIs

```bash
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable gmail.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. Create Service Account for Gmail Access

```bash
# Create service account
gcloud iam service-accounts create semiconductor-news \
  --display-name="Semiconductor News Sender"

# Grant necessary Gmail permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=serviceAccount:semiconductor-news@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/compute.serviceAgent
```

### 3. Generate Service Account Key

```bash
gcloud iam service-accounts keys create cloud_function/service_account_key.json \
  --iam-account=semiconductor-news@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 4. Set Up Gmail API Credentials

For Gmail access, you need to:
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 credentials (or use service account)
3. Download and place credentials in `cloud_function/service_account_key.json`

### 5. Deploy the Cloud Function

```bash
gcloud functions deploy send-semiconductor-news \
  --runtime python311 \
  --trigger-topic semiconductor-news-trigger \
  --entry-point send_semiconductor_news \
  --source ./cloud_function \
  --region us-central1 \
  --set-env-vars RECIPIENT_EMAIL="supertaroniicha@gmail.com"
```

### 6. Create Cloud Scheduler Job for Daily Execution

```bash
# Create scheduler job (8 AM UTC daily)
gcloud scheduler jobs create pubsub semiconductor-news-daily \
  --schedule="0 8 * * *" \
  --topic semiconductor-news-trigger \
  --message-body='{"trigger": "daily"}' \
  --location us-central1 \
  --time-zone "UTC"
```

For different timezone (e.g., EST = UTC-5, 8 AM EST = 1 PM UTC):
```bash
gcloud scheduler jobs create pubsub semiconductor-news-daily \
  --schedule="0 13 * * *" \
  --topic semiconductor-news-trigger \
  --message-body='{"trigger": "daily"}' \
  --location us-central1 \
  --time-zone "America/New_York"
```

### 7. Verify Deployment

```bash
# List deployed functions
gcloud functions list

# List scheduler jobs
gcloud scheduler jobs list --location us-central1

# View logs
gcloud functions logs read send-semiconductor-news --limit 50
```

## Testing

### Test the function locally:
```bash
cd cloud_function
python -m functions_framework --target=send_semiconductor_news --debug
```

Then in another terminal:
```bash
curl http://localhost:8080
```

### Test scheduled trigger manually:
```bash
gcloud scheduler jobs run semiconductor-news-daily --location us-central1
```

## Configuration

- **Timezone**: Modify the `--time-zone` parameter in scheduler job
- **Email recipient**: Update `RECIPIENT_EMAIL` in environment variables
- **Schedule**: Use cron expression format (see examples below)

### Cron Schedule Examples:
- `0 8 * * *` - 8 AM daily (UTC)
- `0 13 * * MON-FRI` - 1 PM weekdays (UTC)
- `0 0 * * 0` - Midnight Sunday (UTC)

## Troubleshooting

### Gmail API Errors
- Ensure service account has Gmail API access
- Check that service account credentials are properly set

### Scheduler Not Triggering
- Verify Cloud Scheduler API is enabled
- Check timezone is correct
- View scheduler logs: `gcloud scheduler jobs describe semiconductor-news-daily --location us-central1`

### Cloud Function Errors
- View logs: `gcloud functions logs read send-semiconductor-news --limit 100`
- Check that all required Python packages are in `requirements.txt`

## Cost Estimates

- **Cloud Functions**: First 2M invocations free per month, then $0.40 per million
- **Cloud Scheduler**: First 3 jobs free, then $0.10 per job per month
- **Gmail API**: Free tier available

For daily emails (365/year), costs should be minimal (under $1/month).

## Clean Up

To remove all resources:
```bash
# Delete scheduler job
gcloud scheduler jobs delete semiconductor-news-daily --location us-central1

# Delete Cloud Function
gcloud functions delete send-semiconductor-news --region us-central1

# Delete service account
gcloud iam service-accounts delete semiconductor-news@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Delete service account key
rm cloud_function/service_account_key.json
```

## Next Steps

1. Update `RECIPIENT_EMAIL` to your actual Gmail address
2. Follow the deployment steps above
3. Test the function manually first
4. Once verified, the scheduler will automatically send emails at 8 AM daily
5. Monitor logs in Cloud Console for any issues
