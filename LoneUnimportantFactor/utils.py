
import hashlib
import hmac
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re

class SignalValidator:
    """Validate incoming signals from different sources"""
    
    @staticmethod
    def validate_chartink_signal(data: Dict[str, Any]) -> bool:
        """Validate Chartink signal format"""
        required_fields = ['symbol', 'signal_type', 'price', 'timestamp']
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Validate signal type
        if data['signal_type'] not in ['BUY', 'SELL']:
            return False
        
        # Validate price
        try:
            float(data['price'])
        except (ValueError, TypeError):
            return False
        
        # Validate symbol format
        if not re.match(r'^[A-Z0-9_-]+$', data['symbol']):
            return False
        
        return True
    
    @staticmethod
    def validate_tradingview_signal(data: Dict[str, Any]) -> bool:
        """Validate TradingView signal format"""
        required_fields = ['symbol', 'action', 'price']
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Validate action
        if data['action'] not in ['BUY', 'SELL', 'buy', 'sell']:
            return False
        
        # Validate price
        try:
            float(data['price'])
        except (ValueError, TypeError):
            return False
        
        return True

class RiskManager:
    """Risk management utilities"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def validate_position_size(self, symbol: str, quantity: int, price: float) -> bool:
        """Validate if position size is within limits"""
        position_value = quantity * price
        
        if position_value > self.config['max_position_size']:
            return False
        
        return True
    
    def check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit has been reached"""
        conn = sqlite3.connect('trading_platform.db')
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT SUM((price * quantity) * CASE WHEN side = 'SELL' THEN 1 ELSE -1 END) as pnl
            FROM trades 
            WHERE DATE(timestamp) = ? AND trading_mode = 'live' AND status = 'filled'
        ''', (today,))
        
        result = cursor.fetchone()
        conn.close()
        
        daily_pnl = result[0] if result[0] else 0
        
        return daily_pnl > -self.config['max_daily_loss']
    
    def check_symbol_allowed(self, symbol: str) -> bool:
        """Check if symbol is allowed for trading"""
        if self.config['blocked_symbols'] and symbol in self.config['blocked_symbols']:
            return False
        
        if self.config['allowed_symbols'] and symbol not in self.config['allowed_symbols']:
            return False
        
        return True

class DatabaseManager:
    """Database utility functions"""
    
    @staticmethod
    def get_active_strategies(symbol: str = None, signal_source: str = None) -> List[Dict]:
        """Get active strategies with optional filters"""
        conn = sqlite3.connect('trading_platform.db')
        cursor = conn.cursor()
        
        query = "SELECT * FROM strategies WHERE is_active = 1"
        params = []
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        
        if signal_source:
            query += " AND signal_source = ?"
            params.append(signal_source)
        
        cursor.execute(query, params)
        strategies = cursor.fetchall()
        conn.close()
        
        # Convert to dictionaries
        columns = ['id', 'name', 'exchange', 'instrument_type', 'symbol', 'signal_source',
                  'position_size_type', 'position_size', 'order_type', 'product_type',
                  'stop_loss', 'target', 'trailing_stop_loss', 'entry_condition', 
                  'exit_condition', 'is_active', 'created_at']
        
        return [dict(zip(columns, strategy)) for strategy in strategies]
    
    @staticmethod
    def get_recent_signals(limit: int = 50) -> List[Dict]:
        """Get recent signals"""
        conn = sqlite3.connect('trading_platform.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, st.name as strategy_name 
            FROM signals s 
            LEFT JOIN strategies st ON s.strategy_id = st.id 
            ORDER BY s.timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        signals = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'strategy_id', 'signal_type', 'symbol', 'price', 
                  'quantity', 'timestamp', 'status', 'strategy_name']
        
        return [dict(zip(columns, signal)) for signal in signals]
    
    @staticmethod
    def get_recent_trades(limit: int = 50) -> List[Dict]:
        """Get recent trades"""
        conn = sqlite3.connect('trading_platform.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, s.symbol as signal_symbol 
            FROM trades t 
            LEFT JOIN signals s ON t.signal_id = s.id 
            ORDER BY t.timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        trades = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'signal_id', 'broker', 'order_id', 'symbol', 'side',
                  'quantity', 'price', 'status', 'trading_mode', 'timestamp', 'signal_symbol']
        
        return [dict(zip(columns, trade)) for trade in trades]
    
    @staticmethod
    def get_broker_configs(active_only: bool = True) -> List[Dict]:
        """Get broker configurations"""
        conn = sqlite3.connect('trading_platform.db')
        cursor = conn.cursor()
        
        query = "SELECT * FROM broker_configs"
        if active_only:
            query += " WHERE is_active = 1"
        
        cursor.execute(query)
        configs = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'broker_name', 'api_key', 'api_secret', 'access_token', 
                  'is_active', 'created_at']
        
        return [dict(zip(columns, config)) for config in configs]

class NotificationManager:
    """Handle notifications for trades, signals, and alerts"""
    
    @staticmethod
    def send_trade_notification(trade_data: Dict[str, Any]):
        """Send notification for trade execution"""
        # Implementation for sending notifications
        # Could integrate with email, SMS, Slack, Discord, etc.
        print(f"Trade executed: {trade_data}")
    
    @staticmethod
    def send_signal_notification(signal_data: Dict[str, Any]):
        """Send notification for new signals"""
        print(f"New signal: {signal_data}")
    
    @staticmethod
    def send_error_notification(error_message: str):
        """Send error notification"""
        print(f"Error: {error_message}")

class SymbolMapper:
    """Map symbols between different formats (broker-specific)"""
    
    SYMBOL_MAPPINGS = {
        'NSE': {
            'RELIANCE': 'RELIANCE-EQ',
            'INFY': 'INFY-EQ',
            'TCS': 'TCS-EQ',
            'NIFTY': 'NIFTY50_INDEX'
        },
        'BSE': {
            'RELIANCE': '500325',
            'INFY': '500209',
            'TCS': '532540'
        }
    }
    
    @staticmethod
    def get_broker_symbol(symbol: str, exchange: str, broker: str) -> str:
        """Get broker-specific symbol format"""
        # This would contain mappings for different brokers
        # For now, return as-is
        return symbol
    
    @staticmethod
    def normalize_symbol(symbol: str, exchange: str) -> str:
        """Normalize symbol to standard format"""
        # Remove exchange suffixes and normalize
        symbol = symbol.upper()
        symbol = re.sub(r'[-_]EQ$', '', symbol)
        symbol = re.sub(r'[-_]INDEX$', '', symbol)
        return symbol

class PositionCalculator:
    """Calculate position sizes and quantities"""
    
    @staticmethod
    def calculate_quantity_from_amount(amount: float, price: float, lot_size: int = 1) -> int:
        """Calculate quantity based on amount and lot size"""
        base_quantity = int(amount / price)
        return (base_quantity // lot_size) * lot_size
    
    @staticmethod
    def calculate_stop_loss_price(entry_price: float, stop_loss_percent: float, side: str) -> float:
        """Calculate stop loss price"""
        if side.upper() == 'BUY':
            return entry_price * (1 - stop_loss_percent / 100)
        else:  # SELL
            return entry_price * (1 + stop_loss_percent / 100)
    
    @staticmethod
    def calculate_target_price(entry_price: float, target_percent: float, side: str) -> float:
        """Calculate target price"""
        if side.upper() == 'BUY':
            return entry_price * (1 + target_percent / 100)
        else:  # SELL
            return entry_price * (1 - target_percent / 100)

class WebhookVerifier:
    """Verify webhook signatures for security"""
    
    @staticmethod
    def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        if not secret:
            return True  # If no secret is set, skip verification
        
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

def format_currency(amount: float) -> str:
    """Format amount as Indian currency"""
    return f"₹{amount:,.2f}"

def parse_signal_time(timestamp_str: str) -> datetime:
    """Parse timestamp from signal"""
    # Handle different timestamp formats
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%d/%m/%Y %H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    # If no format matches, return current time
    return datetime.now()

def is_market_open(exchange: str = 'NSE') -> bool:
    """Check if market is open for the given exchange"""
    from config import Config
    
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    
    exchange_config = Config.EXCHANGES.get(exchange, {})
    trading_hours = exchange_config.get('trading_hours', {})
    
    start_time = trading_hours.get('start', '09:15')
    end_time = trading_hours.get('end', '15:30')
    
    # Check if it's a weekday (Monday = 0, Sunday = 6)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    
    return start_time <= current_time <= end_time

def log_trade_activity(activity_type: str, data: Dict[str, Any]):
    """Log trading activity for audit purposes"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'activity_type': activity_type,
        'data': data
    }
    
    # In production, this would write to a proper logging system
    print(f"AUDIT LOG: {json.dumps(log_entry)}")
