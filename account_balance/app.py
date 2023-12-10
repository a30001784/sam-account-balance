import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from forex_python.converter import CurrencyRates
from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs


# Example usage
symbols = ['ONEUSDT', 'DOGEUSDT']
holding_quantities = [346998, 121266]             # as of 20/8/2023
initial_account_balance = 40000
us_stock_position = 4938
us_stock_ticker = 'open'
us_stock_metric = 'Price'
cash = 13453

def fundamental_metric(soup, metric):
    return soup.find(text = metric).find_next(class_='snapshot-td2').text


def get_fundamental_data(ticker, metric):
    try:
        url = ("http://finviz.com/quote.ashx?t=" + ticker.lower())
        session = HTMLSession()
        response = session.get(url)
        soup =bs(response.content, 'html.parser')
        price = fundamental_metric(soup,metric)
    except Exception as e:
        print(ticker, 'not found')
    return float(price)

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

def get_stock_account_balance(holding_size, ticker, metric):
    current_price = get_fundamental_data(ticker, metric)

    # Calculate the stock account balance
    account_balance = current_price * holding_size
    # print(f"The current stock account balance for {ticker} is: ${account_balance}")
    return account_balance

def exchange_usd_to_aud(usd_amount):
    c = CurrencyRates()
    aud_amount = c.convert('USD', 'AUD', usd_amount)
    return aud_amount


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


def cmd_email():

    values = [cash]
    #  Calculate daily account balance
    subject = 'Daily Account Balance'
    us_stock_balance = get_stock_account_balance(us_stock_position, us_stock_ticker, us_stock_metric)
    us_stock_balance_aud = exchange_usd_to_aud(us_stock_balance)

    bitcoin_account_balance = calculate_account_balance(symbols, holding_quantities)
    bitcoin_account_balance_aud = exchange_usd_to_aud(bitcoin_account_balance)
    values.append(bitcoin_account_balance_aud)

    print(f'Total US Stock Account Balance: US${us_stock_balance:.2f}')
    print(f'Total US Stock Account Balance: AU${us_stock_balance_aud:.2f}')

    print(f'Daily Bitcoin Account Balance: {bitcoin_account_balance:.2f} USDT')
    print(f'Daily Bitcoin Account Balance: AU${bitcoin_account_balance_aud:.2f}')

    #### Account balance for US Stock ##########
    body1 = f'US Stock Balance: US${us_stock_balance:.2f}'
    body2 = f'US Stock Balance: AU${us_stock_balance_aud:.2f}'

    #### Account balance for bitcoin ##########
    body3 = f'Bitcoin Balance: {bitcoin_account_balance:.2f} USDT'
    body4 = f'Bitcoin Balance: AU${bitcoin_account_balance_aud:.2f}'

    ##### Total Account Balance ############
    values.append(us_stock_balance_aud)
    total_balance = sum(values)
    body5 = f'Total Balance: AU${total_balance:.2f}'

    body = body1 + '\n' + body2 + '\n' + body3 + '\n' + body4 + '\n' + body5

    # Send the email on the bitcoin account balance
    result = send_email(subject, body)

    if result == 0:
        print('Email sent successfully.')
    else:
        print(f'Error sending email: {result}')
    return result

# def lambda_handler(event, context):
#
#     cmd_email()


def main():
    cmd_email()


if __name__ == "__main__":
    main()



