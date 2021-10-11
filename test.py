'''
A simple script to test the tradeBot over a period of time and saves the
resulting trades
'''

import tradeBot
import time
import multiprocessing

# Config
periods = 250
trailLength = 90
maxPeriod = 200
fileName = 'Data/AAPL.csv'
processes = 8

startTime = time.time()

# Loading and cleaning test data
data = []
with open(fileName) as file:
    lines = file.readlines()[1:]
    for line in lines:
        line = line.split(',')
        data.append([line[0], float(line[4])])
data = data[-trailLength-maxPeriod-periods:] + ['END']

trades = []

# Main function iterating over each day in test period
def process(startingPeriod):
    processTrades = []
    for period in range(startingPeriod, 0, -processes):
        print('Starting period', periods-period)
        currentData = [record[1] for record in data[periods-period:-period]]
        periodData = data[-period-1]
        signal = tradeBot.generateSignal(trailLength, maxPeriod, currentData)
        if signal != 0:
            processTrades.append([periodData[0], periodData[1]*signal])
    return processTrades

# Launch processes and compile input
if __name__ == '__main__':
    start = time.time()
    p = multiprocessing.Pool(processes)
    tradesLists = p.map(process, range(periods, periods-processes, -1))
    p.close()

    trades = []
    for tradesList in tradesLists:
        trades.extend(tradesList)

    trades.sort(key=lambda x: x[0])
    
    with open('trades.txt', 'w') as file:
        file.write(str(trades))
    
    print(f'Finished in {time.time()-start:.2f}s')
    import tradeAnalyzer