import boto3
from collections import defaultdict
from urllib.parse import unquote_plus
import json
import base64

def print_labels_and_values(field, keys):
    if "LabelDetection" in field and "ValueDetection" in field:
        a, b = str(field.get('LabelDetection')['Text']), str(field.get('ValueDetection')['Text'])
        for w in keys:
            if w in a:
                print(f"{a}:{b}")
                return w, b
    return None, None

def process_expense_analysis(response):
    wanted = {"NIP":"", "Sprzedawca":"", "brutto":""}
    for expense_doc in response["ExpenseDocuments"]:
        for summary_field in expense_doc["SummaryFields"]:
            a,b = print_labels_and_values(summary_field, wanted.keys())
            if a != None:
                wanted[a] = b
            print()
    return wanted



def lambda_handler(event, context):
    file_obj = event["Records"][0]
    bucket = unquote_plus(str(file_obj["s3"]["bucket"]["name"]))
    file_name = unquote_plus(str(file_obj["s3"]["object"]["key"]))
    print(f'Bucket: {bucket}, file: {file_name}')
    
    client = boto3.client('textract')
    response = client.analyze_expense(Document={'S3Object': {'Bucket': bucket, "Name": file_name}})
    
    
    invoice_data = process_expense_analysis(response)
    invoice_data['name'] = file_name
    print(json.dumps(invoice_data, indent=4))
    
    dynamodb = boto3.resource('dynamodb')
    
    table = dynamodb.Table('texttract-s478874')
    
    table.put_item(Item=invoice_data)
    
    
    responseObj = {}
    responseObj['statusCode']  = 200
    responseObj['headers'] = {}
    responseObj['body'] = json.dumps(invoice_data)
    
    return responseObj