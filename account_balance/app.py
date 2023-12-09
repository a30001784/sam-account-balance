import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta, date
import time
from forex_python.converter import CurrencyRates


# Example usage
symbols = ['ONEUSDT', 'DOGEUSDT']
holding_quantities = [346998, 121266]          # as of 20/8/2023
initial_account_balance = 40000

def fundamental_metric(soup, metric):
    return soup.find(text = metric).find_next(class_='snapshot-td2').text

def exchange_usd_to_aud(usd_amount):
    c = CurrencyRates()
    aud_amount = c.convert('USD', 'AUD', usd_amount)
    return aud_amount

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

def send_email(to_email, subject, body):
    from_email = '156709406@qq.com'
    smtp_server = 'smtp.qq.com'
    smtp_port = 587
    smtp_username = '156709406@qq.com'
    smtp_password = 'esdrnpzdsscbcajj'

    msg = MIMEText(body)
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.send_message(msg)
    server.quit()

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

    try:
        #  Calculate daily account balance
        bitcoin_account_balance = calculate_account_balance(symbols, holding_quantities)
        bitcoin_account_balance_aud = exchange_usd_to_aud(bitcoin_account_balance)

        # Print daily account balance
        print(f'Daily Bitcoin Account Balance: {bitcoin_account_balance:.2f} USDT')
        print(f'Daily Bitcoin Account Balance: AU${bitcoin_account_balance_aud:.2f}')

        # Send email with the result
        to_email = '156709406@qq.com'
        subject = 'Daily Bitcoin Account Balance'
        body1 = f'Daily Account Balance: {bitcoin_account_balance:.2f} USDT'
        body2 = f'Daily Account Balance: AU${bitcoin_account_balance_aud:.2f}'
        body = body1 + '\n' + body2
        send_email(to_email, subject, body)

        return {
            'statusCode': 200,
            'body': 'Daily Account Balance calculated and email sent'
        }
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise

    # return {
    #     "statusCode": 200,
    #     "body": json.dumps({
    #         "message": "hello world",
    #         # "location": ip.text.replace("\n", "")
    #     }),
    # }
