
from flask import Flask, render_template, request, jsonify, session
import json
import sqlite3
from datetime import datetime
import threading
import time
from typing import Dict, List, Any
import requests
import hashlib
import hmac
import base64

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Database initialization
def init_db():
    conn = sqlite3.connect('trading_platform.db')
    cursor = conn.cursor()
    
    # Strategies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            exchange TEXT NOT NULL,
            instrument_type TEXT NOT NULL,
            symbol TEXT NOT NULL,
            signal_source TEXT NOT NULL,
            position_size_type TEXT NOT NULL,
            position_size REAL NOT NULL,
            order_type TEXT NOT NULL,
            product_type TEXT NOT NULL,
            stop_loss REAL,
            target REAL,
            trailing_stop_loss REAL,
            entry_condition TEXT,
            exit_condition TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Signals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_id INTEGER,
            signal_type TEXT NOT NULL,
            symbol TEXT NOT NULL,
            price REAL,
            quantity INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (strategy_id) REFERENCES strategies (id)
        )
    ''')
    
    # Trades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_id INTEGER,
            broker TEXT,
            order_id TEXT,
            symbol TEXT,
            side TEXT,
            quantity INTEGER,
            price REAL,
            status TEXT,
            trading_mode TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (signal_id) REFERENCES signals (id)
        )
    ''')
    
    # Broker configurations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS broker_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broker_name TEXT NOT NULL,
            api_key TEXT,
            api_secret TEXT,
            access_token TEXT,
            is_active BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Broker API integrations
class BrokerManager:
    def __init__(self):
        self.brokers = {
            'angel_one': AngelOneBroker(),
            'upstox': UpstoxBroker(),
            'zerodha': ZerodhaBroker(),
            'fyers': FyersBroker(),
            'dhan': DhanBroker(),
            'groww': GrowwBroker(),
            'axis_direct': AxisDirectBroker(),
            'alice_blue': AliceBlueBroker(),
            'five_paisa': FivePaisaBroker(),
            'flattrade': FlatTradeBroker(),
            'kotak_neo': KotakNeoBroker(),
            'motilal_oswal': MotilalOswalBroker(),
            'paytm_money': PaytmMoneyBroker(),
            'tradejini': TradejiniBroker()
        }
    
    def get_broker(self, broker_name: str):
        return self.brokers.get(broker_name)

# Base broker class
class BaseBroker:
    def __init__(self):
        self.api_key = None
        self.api_secret = None
        self.access_token = None
        self.base_url = None
    
    def authenticate(self, api_key: str, api_secret: str, access_token: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
    
    def place_order(self, symbol: str, side: str, quantity: int, price: float, order_type: str, product_type: str):
        raise NotImplementedError
    
    def get_positions(self):
        raise NotImplementedError
    
    def cancel_order(self, order_id: str):
        raise NotImplementedError

# Specific broker implementations
class AngelOneBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://apiconnect.angelbroking.com"
    
    def place_order(self, symbol: str, side: str, quantity: int, price: float, order_type: str, product_type: str):
        # Angel One API implementation
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-UserType': 'USER',
            'X-SourceID': 'WEB',
            'X-ClientLocalIP': '192.168.1.1',
            'X-ClientPublicIP': '106.193.147.98',
            'X-MACAddress': 'fe80::216:3eff:fe00:362a',
            'X-PrivateKey': self.api_key
        }
        
        payload = {
            'variety': 'NORMAL',
            'tradingsymbol': symbol,
            'symboltoken': self._get_symbol_token(symbol),
            'transactiontype': side.upper(),
            'exchange': 'NSE',
            'ordertype': order_type.upper(),
            'producttype': product_type.upper(),
            'duration': 'DAY',
            'price': str(price),
            'quantity': str(quantity)
        }
        
        try:
            response = requests.post(f'{self.base_url}/rest/secure/angelbroking/order/v1/placeOrder', 
                                   json=payload, headers=headers)
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def _get_symbol_token(self, symbol: str):
        # Implementation to get symbol token
        return "3045"  # Example token

class UpstoxBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.upstox.com/v2"

class ZerodhaBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.kite.trade"

class FyersBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.fyers.in/api/v2"

class DhanBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.dhan.co"

class GrowwBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://groww.in/v1/api"

class AxisDirectBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://apiconnect.axisdirect.in"

class AliceBlueBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://ant.aliceblueonline.com/rest/AliceBlueAPIService"

class FivePaisaBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://openapi.5paisa.com"

class FlatTradeBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://piconnect.flattrade.in/PiConnectTP"

class KotakNeoBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://gw-napi.kotaksecurities.com"

class MotilalOswalBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://openapi.motilaloswal.com"

class PaytmMoneyBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://developer.paytmmoney.com"

class TradejiniBroker(BaseBroker):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.tradejini.com"

# Signal processing
class SignalProcessor:
    def __init__(self, broker_manager: BrokerManager):
        self.broker_manager = broker_manager
        self.paper_trading = True  # Default to paper trading
    
    def process_chartink_signal(self, signal_data: Dict[str, Any]):
        """Process signals from Chartink"""
        try:
            # Extract signal information
            symbol = signal_data.get('symbol')
            signal_type = signal_data.get('signal_type')  # BUY/SELL
            price = signal_data.get('price')
            
            # Find matching strategies
            strategies = self._get_matching_strategies(symbol, 'chartink')
            
            for strategy in strategies:
                self._execute_strategy(strategy, signal_type, price)
                
        except Exception as e:
            print(f"Error processing Chartink signal: {e}")
    
    def process_tradingview_signal(self, signal_data: Dict[str, Any]):
        """Process signals from TradingView"""
        try:
            symbol = signal_data.get('symbol')
            signal_type = signal_data.get('signal_type')
            price = signal_data.get('price')
            
            strategies = self._get_matching_strategies(symbol, 'tradingview')
            
            for strategy in strategies:
                self._execute_strategy(strategy, signal_type, price)
                
        except Exception as e:
            print(f"Error processing TradingView signal: {e}")
    
    def _get_matching_strategies(self, symbol: str, signal_source: str):
        conn = sqlite3.connect('trading_platform.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM strategies 
            WHERE symbol = ? AND signal_source = ? AND is_active = 1
        ''', (symbol, signal_source))
        
        strategies = cursor.fetchall()
        conn.close()
        
        return strategies
    
    def _execute_strategy(self, strategy, signal_type: str, price: float):
        # Calculate position size
        if strategy[6] == 'quantity':  # position_size_type
            quantity = int(strategy[7])  # position_size
        else:  # amount
            quantity = int(strategy[7] / price)
        
        # Create signal record
        conn = sqlite3.connect('trading_platform.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO signals (strategy_id, signal_type, symbol, price, quantity)
            VALUES (?, ?, ?, ?, ?)
        ''', (strategy[0], signal_type, strategy[4], price, quantity))
        
        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Execute trade
        if self.paper_trading:
            self._execute_paper_trade(signal_id, strategy, signal_type, quantity, price)
        else:
            self._execute_live_trade(signal_id, strategy, signal_type, quantity, price)
    
    def _execute_paper_trade(self, signal_id: int, strategy, signal_type: str, quantity: int, price: float):
        """Simulate trade execution for paper trading"""
        conn = sqlite3.connect('trading_platform.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (signal_id, broker, symbol, side, quantity, price, status, trading_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (signal_id, 'paper', strategy[4], signal_type, quantity, price, 'filled', 'paper'))
        
        conn.commit()
        conn.close()
        
        print(f"Paper trade executed: {signal_type} {quantity} {strategy[4]} at {price}")
    
    def _execute_live_trade(self, signal_id: int, strategy, signal_type: str, quantity: int, price: float):
        """Execute actual trade through broker API"""
        # Implementation for live trading
        pass

# Trading engine
class TradingEngine:
    def __init__(self):
        self.broker_manager = BrokerManager()
        self.signal_processor = SignalProcessor(self.broker_manager)
        self.running = False
    
    def start(self):
        self.running = True
        # Start background threads for signal monitoring
        threading.Thread(target=self._monitor_signals, daemon=True).start()
    
    def stop(self):
        self.running = False
    
    def _monitor_signals(self):
        """Monitor and process incoming signals"""
        while self.running:
            # Check for new signals and process them
            time.sleep(1)

# Initialize components
init_db()
trading_engine = TradingEngine()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/strategies')
def strategies():
    return render_template('strategies.html')

@app.route('/api/create_strategy', methods=['POST'])
def create_strategy():
    data = request.json
    
    conn = sqlite3.connect('trading_platform.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO strategies (
            name, exchange, instrument_type, symbol, signal_source,
            position_size_type, position_size, order_type, product_type,
            stop_loss, target, trailing_stop_loss, entry_condition, exit_condition
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'], data['exchange'], data['instrument_type'], data['symbol'],
        data['signal_source'], data['position_size_type'], data['position_size'],
        data['order_type'], data['product_type'], data.get('stop_loss'),
        data.get('target'), data.get('trailing_stop_loss'),
        data.get('entry_condition'), data.get('exit_condition')
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Strategy created successfully'})

@app.route('/api/webhook/chartink', methods=['POST'])
def chartink_webhook():
    """Webhook endpoint for Chartink signals"""
    signal_data = request.json
    trading_engine.signal_processor.process_chartink_signal(signal_data)
    return jsonify({'status': 'received'})

@app.route('/api/webhook/tradingview', methods=['POST'])
def tradingview_webhook():
    """Webhook endpoint for TradingView signals"""
    signal_data = request.json
    trading_engine.signal_processor.process_tradingview_signal(signal_data)
    return jsonify({'status': 'received'})

@app.route('/api/toggle_trading_mode', methods=['POST'])
def toggle_trading_mode():
    mode = request.json.get('mode')  # 'paper' or 'live'
    trading_engine.signal_processor.paper_trading = (mode == 'paper')
    return jsonify({'status': 'success', 'mode': mode})

@app.route('/api/broker_config', methods=['POST'])
def configure_broker():
    data = request.json
    
    conn = sqlite3.connect('trading_platform.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO broker_configs (broker_name, api_key, api_secret, access_token, is_active)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['broker_name'], data['api_key'], data['api_secret'], 
          data.get('access_token'), data.get('is_active', False)))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'message': 'Broker configured successfully'})

if __name__ == "__main__":
    trading_engine.start()
    app.run(host='0.0.0.0', port=8080, debug=True)
