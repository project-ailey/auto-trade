from datetime import datetime

def find_most_low(candles, start, end):
    most_low = candles[start].low
    most_low_index = start
    for i in range(start + 1, end + 1):
        if most_low > candles[i].low:
            most_low = candles[i].low
            most_low_index = i

    return most_low_index


def find_most_high(candles, start, end):
    most_high = candles[start].high
    most_high_index = start
    for i in range(start + 1, end + 1):
        if most_high < candles[i].high:
            most_high = candles[i].high
            most_high_index = i

    return most_high_index
