#!/usr/bin/env python

import urllib3, pickle, time, os
import argparse
from datetime import datetime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_ticker(coin=None):
    '''Get tickers from coinmarketcap.com
    Keyword arguments:
    coin -- the string symbol of the coin whose ticker to return.
            If None, all tickers are returned (default None).
    '''
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://api.coinmarketcap.com/v1/ticker/')
    ticker = eval(r.data.decode().replace('null', 'None'))
    if coin is not None:
        for t in ticker:
            if t['symbol'] == coin:
                return t
    return ticker

def get_dollar_value(coins):
    '''Get the USD value of the given coin
    Keyword arguments:
    coins -- A list of coins whose values to get.
    '''
    coin_tickers = [get_ticker(c) for c in coins]
    return {t['symbol']:float(t['price_usd']) for t in coin_tickers}

def rebalance(pname):
    '''Perform a rebalance of current holdings.
    Keyword arguments:
    pname -- The name of the portfolio to rebalance
    '''
    portfolio = pickle.load(open(f'{pname}.pkl', 'rb'))
    coins = list(portfolio.keys())
    usd_values = get_dollar_value(coins) 
    total_value = sum([portfolio[c]*usd_values[c] for c in coins])
    ind_value = total_value / len(coins)
    rebalance = [ind_value/usd_values[c] for c in coins]
    portfolio = {coins[i]:rebalance[i] for i in range(len(coins))}
    pickle.dump(portfolio, open(f'{pname}.pkl', 'wb'))
    str_holdings = ','.join([str(portfolio[c]) for c in coins])
    str_usd = ','.join([str(usd_values[c]) for c in coins])
    with open(f'{pname}.csv', 'a') as f:
        f.write(f'{datetime.now()},{str_holdings},{str_usd},{total_value}\n')
    return portfolio

def __init__(coins, portfolio, init_value):
    assert len(coins) == len(init_value) \
           or len(init_value) == 1, \
           'Incorrect number of initial values passed.'
    if not os.path.isfile(f'{portfolio}.csv'):
        with open(f'{portfolio}.csv', 'w+') as f:
            symbols = ",".join([c for c in coins])
            values = ",".join([f'{c}_usd' for c in coins])
            f.write(f'date,{symbols},{values},total\n')
    if len(init_value) == 1:
        p = {c:init_value for c in coins}
    else:
        p = {coins[i]:init_value[i] for i in range(len(coins))}
    print(p)
    pickle.dump(p, open(f'{portfolio}.pkl', 'wb'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--init', action='store_true', help='Initialise a new portfolio.')
    parser.add_argument('--coins', type=str, nargs='+', metavar='COIN', help='A list of coin symbols to initialise the new portfolio with. Ex: BTC ETH XRP')
    parser.add_argument('--portfolio', type=str, help='Name of the portfolio', default='portfolio')
    parser.add_argument('--values', type=float, nargs='+', metavar='VALUE', help='Initial coin values. Ether a single value or a list of values, one for each coin')
    args = parser.parse_args()
    if args.init:
        assert args.coins is not None, 'No coins supplied. Use the --coins argument to generate a new portfolio'
        assert args.values is not None, 'No values supplied. Use the --values argument to supply values. See --help for more details'
        __init__(args.coins, args.portfolio, args.values)
    else:
        rebalance(args.portfolio)


