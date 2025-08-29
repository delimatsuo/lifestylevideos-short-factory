# Google Sheets Setup Checklist

## ✅ Completed Steps:
- [x] Created Google Cloud Project: **Lifestylevideos** 
- [x] Created Service Account: **lifestyle-videos-service**

## 📋 Remaining Steps:

### 1. Download Credentials
- [ ] Go to service account details in Google Cloud Console
- [ ] Click "Keys" tab → "Add Key" → "Create New Key" 
- [ ] Select JSON format
- [ ] Save as: `config/credentials/google-service-account.json`

### 2. Create Google Spreadsheet
- [ ] Go to https://sheets.google.com/
- [ ] Create blank spreadsheet
- [ ] Name it: `Lifestylevideos Shorts Factory Dashboard`
- [ ] Share with: `lifestyle-videos-service@lifestylevideos-470516.iam.gserviceaccount.com`
- [ ] Give "Editor" permissions
- [ ] Copy spreadsheet ID from URL

### 3. Update Configuration
- [ ] Update `.env` file with your actual spreadsheet ID:
  ```
  GOOGLE_SHEETS_SPREADSHEET_ID=your_actual_spreadsheet_id_here
  ```

### 4. Test Connection
- [ ] Run: `python test_sheets.py`
- [ ] Verify connection works
- [ ] Run: `python src/main.py test`

## 🎯 Success Criteria:
When setup is complete, you should see:
- ✅ Google Sheets connection successful!
- ✅ Dashboard headers created!
- ✅ Test content added with ID: [number]
- 🎉 All tests passed!

## 🚀 Next Steps:
Once Google Sheets is working → Start **Task #2: Content Ideation Engine**
