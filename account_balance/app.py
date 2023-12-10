import requests
import smtplib
import time
import configparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from forex_python.converter import CurrencyRates


# Example usage
symbols = ['ONEUSDT', 'DOGEUSDT']
holding_quantities = [346998, 121266]            # as of 01/12/2023
initial_account_balance = 40000
CONFIG_FILE = './config.ini'
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

def fundamental_metric(soup, metric):
    return soup.find(text = metric).find_next(class_='snapshot-td2').text

def exchange_usd_to_aud(usd_amount):
    try:
        c = CurrencyRates()
        aud_amount = c.convert('USD', 'AUD', usd_amount)
        return aud_amount
    
    except Exception as e:
    # If there's an error, return the error message
        return str(e)

def get_binance_market_data(symbol):
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    response = requests.get(url)
    data = response.json()
    price = float(data['price'])
    return price

def calculate_account_balance(symbols, holding_quantities):
    account_balance = 0.0
    for symbol, holding_quantity in zip(symbols, holding_quantities):
        price = get_binance_market_data(symbol)
        account_balance += price * holding_quantity
    return account_balance

def send_email(subject, body):
    from_email = '156709406@qq.com'
    to_email = '156709406@qq.com'
    smtp_server = 'smtp.qq.com'
    smtp_port = 587
    smtp_username = '156709406@qq.com'
    smtp_password = 'esdrnpzdsscbcajj'

    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject
    
    # Attach the body of the email
    message.attach(MIMEText(body, 'plain'))
    
    print(f'Start to send email')

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Login to the email server
            server.starttls()
            server.login(smtp_username, smtp_password)
            
            # Send the email
            print(f'Start to send the message')
            server.sendmail(from_email, to_email, message.as_string())
            server.quit()
                # If successful, return 0

        # If successful, return 0
        return 0

    except Exception as e:
        # If there's an error, return the error message
        return str(e)

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
#  Calculate daily account balance
    subject = 'Daily Bitcoin Account Balance'
    bitcoin_account_balance = calculate_account_balance(symbols, holding_quantities)
    bitcoin_account_balance_aud = exchange_usd_to_aud(bitcoin_account_balance)

    body1 = f'Daily Account Balance: {bitcoin_account_balance:.2f} USDT'
    body2 = f'Daily Account Balance: AU${bitcoin_account_balance_aud:.2f}'
    body = body1 + '\n' + body2
    
    # Send the email on the bitcoin account balance
    result = send_email(subject, body)
    
    if result == 0:
        print('Email sent successfully.')
    else:
        print(f'Error sending email: {result}')
    