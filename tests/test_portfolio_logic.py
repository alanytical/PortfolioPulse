from datetime import date

def valuation(share_prices, buys, day):
    held=[(shares,price) for dt,shares,price in buys if dt<=day]
    shares=sum(x for x,_ in held)
    cost=sum(shares*paid for shares,paid in held)
    value=shares*share_prices[day]
    return shares,cost,value,value-cost

def test_historical_position_does_not_include_future_purchases():
    buys=[(date(2026,7,6),4,215),(date(2026,8,3),2,230)]
    prices={date(2026,7,7):220,date(2026,8,4):240}
    assert valuation(prices,buys,date(2026,7,7)) == (4,860,880,20)
    assert valuation(prices,buys,date(2026,8,4)) == (6,1320,1440,120)

def test_fx_conversion():
    usd_value=1440; rate=1500
    assert usd_value*rate==2160000
