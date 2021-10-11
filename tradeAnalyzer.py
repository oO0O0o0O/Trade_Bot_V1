'''
This program is used to analyze the performance of trades generated over a
period of time using tradeBot. It can be configured to account for account
size, margin, and the size of each trade relative to the account.
'''

with open('trades.txt') as file:
    trades = eval(file.read())

# Config
startingBal = 500
bal = startingBal
pos = 0
tradePercOfAccount = 0.5
shortable = False

qty = int(abs(500 * tradePercOfAccount / trades[0][1]))
buys = []
sells = []
actualTrades = []

for trade in trades:
    tradeValue = trade[1]
    if qty == 0:
        print('Account too small')
        break

    # Open/add to long position
    if tradeValue > 0 and pos >= 0 and bal >= tradeValue * qty:
        bal -= tradeValue * qty
        pos += qty
        buys.append(tradeValue)
        actualTrades.append(trade)

    # Close short position
    elif tradeValue > 0 and pos < 0 and shortable:
        bal += tradeValue * pos
        pos = 0
        buys.append(tradeValue)
        actualTrades.append(trade)

    # Open/add to short position
    elif tradeValue < 0 and pos <= 0 and shortable:
        bal -= tradeValue * qty
        pos -= qty
        sells.append(tradeValue)
        actualTrades.append(trade)

    # Close long position
    elif tradeValue < 0 and pos > 0:
        bal -= tradeValue * pos
        pos = 0
        sells.append(tradeValue)
        actualTrades.append(trade)

# Print info
print('Actual Trades:', actualTrades)

try:
    avgBuy = sum(buys)/len(buys)
    print(f'Average Buy: ${avgBuy:.2f}')
except ZeroDivisionError:
    pass

try:
    avgSell = -sum(sells)/len(sells)
    print(f'Average Sell: ${avgSell:.2f}')
except ZeroDivisionError:
    pass

netValue = bal + pos * 104.66

print(f'Net Value: ${netValue:.2f} | Percent: {(netValue-startingBal)/startingBal*100:.2f}% | Bal ${bal:.2f} | Pos: {pos}')