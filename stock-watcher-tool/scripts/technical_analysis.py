#!/usr/bin/env python3
"""
Technical analysis module for stock watcher.
Provides MA crossover (golden cross / death cross) analysis.
"""
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import time
import yfinance as yf

# Standardized watchlist file path
WATCHLIST_FILE = os.path.expanduser("~/.clawdbot/stock_watcher/watchlist.txt")

def get_stock_ticker(code):
    """Convert stock code to yfinance ticker format."""
    # Check if it's Shanghai (6开头) or Shenzhen (0/3开头)
    if code.startswith('6'):
        return f"{code}.SS"  # Shanghai
    elif code.startswith('0') or code.startswith('3'):
        return f"{code}.SZ"  # Shenzhen
    else:
        return f"{code}.SS"  # Default to Shanghai

def fetch_historical_data(stock_code, days=60):
    """Fetch historical stock data from yfinance."""
    ticker = get_stock_ticker(stock_code)
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Download data with delay to avoid rate limiting
        time.sleep(1)
        stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if len(stock_data) == 0:
            return None
            
        return stock_data
        
    except Exception as e:
        print(f"Error fetching data for {stock_code}: {e}", file=sys.stderr)
        return None

def calculate_ma_crossover(stock_data, short_period=5, long_period=30):
    """Calculate moving averages and detect crossovers."""
    if stock_data is None or len(stock_data) < long_period:
        return None
    
    # Calculate moving averages
    stock_data['MA_short'] = stock_data['Close'].rolling(window=short_period).mean()
    stock_data['MA_long'] = stock_data['Close'].rolling(window=long_period).mean()
    
    # Get the last two days with valid MA values
    valid_data = stock_data.dropna(subset=['MA_short', 'MA_long'])
    
    if len(valid_data) < 2:
        return None
    
    # Latest two data points
    prev = valid_data.iloc[-2]
    latest = valid_data.iloc[-1]
    
    # Determine crossover
    signal = "无交叉"
    suggestion = "持有"
    reason = "移动平均线未形成明显交叉"
    
    if prev['MA_short'] < prev['MA_long'] and latest['MA_short'] > latest['MA_long']:
        signal = "金叉"
        suggestion = "买入/增持"
        reason = f"短期均线({short_period}日)上穿长期均线({long_period}日)，形成金叉，通常为买入信号"
    elif prev['MA_short'] > prev['MA_long'] and latest['MA_short'] < latest['MA_long']:
        signal = "死叉"
        suggestion = "卖出/减仓"
        reason = f"短期均线({short_period}日)下穿长期均线({long_period}日)，形成死叉，通常为卖出信号"
    
    return {
        'current_price': latest['Close'],
        'ma_short': latest['MA_short'],
        'ma_long': latest['MA_long'],
        'signal': signal,
        'suggestion': suggestion,
        'reason': reason
    }

def analyze_stocks():
    """Analyze all stocks in watchlist for technical signals."""
    if not os.path.exists(WATCHLIST_FILE):
        print("观察列表为空")
        return
    
    with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if not lines or all(not line.strip() for line in lines):
        print("观察列表为空")
        return
    
    print("=== 技术分析报告 ===")
    print("(基于5日/30日移动平均线金叉死叉分析)")
    print()
    
    for line in lines:
        line = line.strip()
        if line:
            parts = line.split('|')
            if len(parts) == 2:
                code, name = parts
                
                print(f"📈 {code} - {name}")
                
                # Fetch historical data
                stock_data = fetch_historical_data(code)
                
                if stock_data is None:
                    print("  ❌ 无法获取历史数据")
                    print()
                    continue
                
                # Calculate MA crossover
                analysis = calculate_ma_crossover(stock_data)
                
                if analysis:
                    print(f"  当前价格: {analysis['current_price']:.2f}")
                    print(f"  MA5: {analysis['ma_short']:.2f}")
                    print(f"  MA30: {analysis['ma_long']:.2f}")
                    print(f"  信号: {analysis['signal']}")
                    print(f"  建议: {analysis['suggestion']}")
                    print(f"  理由: {analysis['reason']}")
                else:
                    print("  ⚠️ 数据不足，无法进行技术分析")
                
                print()

if __name__ == "__main__":
    analyze_stocks()