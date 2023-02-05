# AWS image recognition with Textract


### To deploy:
 - clone lambda.py code into your lambda trigger
 - Add S3 bucket to your Lambda Trigger
 - Add invoice to your bucket
 - Enjoy!


 ## Application based on double requests: 
  - PUT https://9kpwan8769.execute-api.us-east-1.amazonaws.com/textract/{bucket-name}/{file-name} to send file to S3 and trigger serverless Textract
  - GET https://gp1q182wu2.execute-api.us-east-1.amazonaws.com/read to read textract result from database