# Mentat
Crypto trader

## Balanced fund simulator
### Initialise a new portfolio
`$python balance.py --init --coins BTC ETH USDT --values 1.2 10.0 100.0 --portfolio my_portfolio`

### Perform a rebalance
`$python balance.py --portfolio my_portfolio`

### Perform hourly rebalance
Add the following line to a user's `crontab`:

`0 * * * * cd /path/to/mentat/ && python balance.py --portfolio my_portfolio`
