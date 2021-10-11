'''
This program generates buy and sell signals based on past price data. It
generates signals from crossovers of the moving averages that have
generated the best buy and sell signals over a previous period of time.
'''

import time

class InputException(Exception):
    '''
    Input exception for bad user input
    '''
    def __init__(self, msg):
        print(msg)

def loadData(trailLength, maxPeriod, fileName):
    '''
    Load, check, and clean price data file and return closes
    '''
    data = []

    # Load file into array
    try:
        with open(fileName) as file:
            lines = file.readlines()
            for line in lines:
                line = line.split(',')
                data.append(line)
    except FileNotFoundError:
        raise InputException('Cannot find specified file')

    # Check for proper file formating
    if data[0] != ['Date','Open','High','Low','Close','Adj Close','Volume\n']:
        raise InputException('Data not formatted correctly')

    # Check if there's enough data
    try:
        assert len(data) > trailLength + maxPeriod
    except AssertionError:
        raise InputException('Not enough data for current settings')

    # Final data transformations
    data = [float(record[4]) for record in data[-trailLength-maxPeriod:]]

    return data

def findMovAvgValues(data, movAvgLength):
    '''
    Find values of a moving average for each data point
    '''
    values = []
    
    # Iterate through each close and calculate moving average value
    for i in range(len(data)):
        value = data[i - movAvgLength + 1 : i + 1]
        value = sum(value) / movAvgLength
        values.append(value)
    
    return values

def findCrossovers(fastMovAvgValues, slowMovAvgValues):
    '''
    Find crossovers in moving averages
    '''
    crossovers = []

    # Iterate over moving average values
    for i in range(1, len(fastMovAvgValues)):
        lastDif = fastMovAvgValues[i-1] - slowMovAvgValues[i-1]
        thisDif = fastMovAvgValues[i] - slowMovAvgValues[i]

        # Check if difference switched signs
        if lastDif < 0 and thisDif > 0:
            crossovers.append(1)
        elif lastDif > 0 and thisDif < 0:
            crossovers.append(-1)
        else:
            crossovers.append(0)
        
    return crossovers

def findOptimumMovAvgs(data, trailLength, maxPeriod):
    '''
    Find best performing moving average pair over a given period of time
    '''
    results = []

    # Iterate through possible moving average pairs
    for slowMovAvg in range(1, maxPeriod):
        for fastMovAvg in range(1, slowMovAvg):
            # Cacluate values for both moving averages
            fastMovAvgValues = findMovAvgValues(data[-trailLength-fastMovAvg:], fastMovAvg)[-trailLength-1:]
            slowMovAvgValues = findMovAvgValues(data[-trailLength-slowMovAvg:], slowMovAvg)[-trailLength-1:]
            
            # Find crossovers/trades
            trades = []
            crossovers = findCrossovers(fastMovAvgValues, slowMovAvgValues)
            for i in range(len(crossovers)):
                trades.append(crossovers[i] * data[-trailLength+i])

            # Isolate buys and sells
            buys = []
            sells = []
            for trade in trades:
                if trade > 0:
                    buys.append(trade)
                elif trade < 0:
                    sells.append(trade)
                    
            # Cacluate average buy and average sell price
            try:
                avgBuy = sum(buys)/len(buys)
                avgSell = sum(sells)/len(sells)
                avgDif = -avgSell - avgBuy
                results.append([fastMovAvg, slowMovAvg, avgDif])
            except ZeroDivisionError:
                results.append([fastMovAvg, slowMovAvg, 0])

    # Find and return best-performing moving averages
    results.sort(key=lambda x: x[2], reverse=True)
    return results[0]

def generateSignal(trailLength, maxPeriod, file):
    '''
    This function generates a buy or sell signal based on previous price data
    '''
    # Load in data and find best-performing moving averages
    if type(file) == str:
        data = loadData(trailLength, maxPeriod, file)
    else:
        data = file
    movAvgs = findOptimumMovAvgs(data, trailLength, maxPeriod)
    
    # Determine if a crossover occured on the most recent period
    fastMovAvgValues = findMovAvgValues(data, movAvgs[0])[-2:]
    slowMovAvgValues = findMovAvgValues(data, movAvgs[1])[-2:]
    crossover = findCrossovers(fastMovAvgValues, slowMovAvgValues)[0]
    
    return crossover