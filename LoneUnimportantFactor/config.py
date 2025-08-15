
import os
from typing import Dict, Any

class Config:
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    
    # Database configuration
    DATABASE_PATH = 'trading_platform.db'
    
    # Trading configuration
    DEFAULT_TRADING_MODE = 'paper'  # 'paper' or 'live'
    
    # Webhook URLs for signal sources
    CHARTINK_WEBHOOK_URL = '/api/webhook/chartink'
    TRADINGVIEW_WEBHOOK_URL = '/api/webhook/tradingview'
    
    # Exchange configurations
    EXCHANGES = {
        'NSE': {
            'name': 'National Stock Exchange',
            'segments': ['EQ', 'FUT', 'CE', 'PE'],
            'trading_hours': {
                'start': '09:15',
                'end': '15:30'
            }
        },
        'BSE': {
            'name': 'Bombay Stock Exchange',
            'segments': ['EQ'],
            'trading_hours': {
                'start': '09:15',
                'end': '15:30'
            }
        },
        'MCX': {
            'name': 'Multi Commodity Exchange',
            'segments': ['COMMODITY'],
            'trading_hours': {
                'start': '09:00',
                'end': '23:30'
            }
        },
        'NFO': {
            'name': 'NSE F&O',
            'segments': ['FUT', 'CE', 'PE'],
            'trading_hours': {
                'start': '09:15',
                'end': '15:30'
            }
        }
    }
    
    # Broker API configurations
    BROKER_CONFIGS = {
        'angel_one': {
            'name': 'Angel One',
            'base_url': 'https://apiconnect.angelbroking.com',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE', 'NFO', 'MCX'],
            'order_types': ['MARKET', 'LIMIT', 'SL', 'SL-M'],
            'product_types': ['INTRADAY', 'DELIVERY', 'MARGIN', 'BO', 'CO']
        },
        'upstox': {
            'name': 'Upstox',
            'base_url': 'https://api.upstox.com/v2',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE', 'NFO', 'MCX'],
            'order_types': ['MARKET', 'LIMIT', 'SL', 'SL-M'],
            'product_types': ['I', 'D', 'CO', 'OCO']
        },
        'zerodha': {
            'name': 'Zerodha Kite',
            'base_url': 'https://api.kite.trade',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE', 'NFO', 'MCX'],
            'order_types': ['MARKET', 'LIMIT', 'SL', 'SL-M'],
            'product_types': ['MIS', 'CNC', 'NRML']
        },
        'fyers': {
            'name': 'Fyers',
            'base_url': 'https://api.fyers.in/api/v2',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE', 'NFO', 'MCX'],
            'order_types': ['1', '2', '3', '4'],  # Market, Limit, Stop, Stop-limit
            'product_types': ['INTRADAY', 'CNC', 'MARGIN']
        },
        'dhan': {
            'name': 'Dhan',
            'base_url': 'https://api.dhan.co',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE', 'NFO', 'MCX'],
            'order_types': ['MARKET', 'LIMIT', 'STOP_LOSS', 'STOP_LOSS_MARKET'],
            'product_types': ['INTRA', 'CNC', 'MARGIN']
        },
        'groww': {
            'name': 'Groww',
            'base_url': 'https://groww.in/v1/api',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE'],
            'order_types': ['MARKET', 'LIMIT'],
            'product_types': ['INTRADAY', 'DELIVERY']
        },
        'axis_direct': {
            'name': 'Axis Direct',
            'base_url': 'https://apiconnect.axisdirect.in',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE', 'NFO', 'MCX'],
            'order_types': ['MARKET', 'LIMIT', 'SL', 'SL-M'],
            'product_types': ['MIS', 'CNC', 'NRML']
        },
        'alice_blue': {
            'name': 'Alice Blue',
            'base_url': 'https://ant.aliceblueonline.com/rest/AliceBlueAPIService',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE', 'NFO', 'MCX'],
            'order_types': ['MARKET', 'LIMIT', 'SL', 'SL-M'],
            'product_types': ['MIS', 'CNC', 'NRML']
        },
        'five_paisa': {
            'name': '5Paisa',
            'base_url': 'https://openapi.5paisa.com',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE', 'NFO', 'MCX'],
            'order_types': ['MARKET', 'LIMIT', 'SL', 'SL-M'],
            'product_types': ['INTRADAY', 'DELIVERY', 'MARGIN']
        },
        'flattrade': {
            'name': 'FlatTrade',
            'base_url': 'https://piconnect.flattrade.in/PiConnectTP',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE', 'NFO', 'MCX'],
            'order_types': ['MARKET', 'LIMIT', 'SL', 'SL-M'],
            'product_types': ['M', 'C', 'H']
        },
        'kotak_neo': {
            'name': 'Kotak Neo',
            'base_url': 'https://gw-napi.kotaksecurities.com',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE', 'NFO', 'MCX'],
            'order_types': ['MARKET', 'LIMIT', 'SL', 'SL-M'],
            'product_types': ['MIS', 'CNC', 'NRML']
        },
        'motilal_oswal': {
            'name': 'Motilal Oswal',
            'base_url': 'https://openapi.motilaloswal.com',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE', 'NFO', 'MCX'],
            'order_types': ['MARKET', 'LIMIT', 'SL', 'SL-M'],
            'product_types': ['INTRADAY', 'DELIVERY', 'MARGIN']
        },
        'paytm_money': {
            'name': 'Paytm Money',
            'base_url': 'https://developer.paytmmoney.com',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE'],
            'order_types': ['MARKET', 'LIMIT'],
            'product_types': ['INTRADAY', 'DELIVERY']
        },
        'tradejini': {
            'name': 'Tradejini',
            'base_url': 'https://api.tradejini.com',
            'auth_required': True,
            'supported_exchanges': ['NSE', 'BSE', 'NFO', 'MCX'],
            'order_types': ['MARKET', 'LIMIT', 'SL', 'SL-M'],
            'product_types': ['MIS', 'CNC', 'NRML']
        }
    }
    
    # Risk management settings
    RISK_MANAGEMENT = {
        'max_daily_loss': 10000,  # Maximum daily loss in INR
        'max_position_size': 50000,  # Maximum position size in INR
        'max_orders_per_minute': 10,  # Rate limiting
        'allowed_symbols': [],  # Empty means all allowed
        'blocked_symbols': [],  # Symbols to block
    }
    
    # Signal processing settings
    SIGNAL_SETTINGS = {
        'chartink': {
            'enabled': True,
            'webhook_secret': os.getenv('CHARTINK_WEBHOOK_SECRET', ''),
            'timeout': 30,
            'retry_attempts': 3
        },
        'tradingview': {
            'enabled': True,
            'webhook_secret': os.getenv('TRADINGVIEW_WEBHOOK_SECRET', ''),
            'timeout': 30,
            'retry_attempts': 3
        }
    }
    
    # Logging configuration
    LOGGING = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'trading_platform.log'
    }

# Environment-specific configurations
class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_PATH = 'trading_platform_dev.db'

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Production-specific settings
    RISK_MANAGEMENT = {
        **Config.RISK_MANAGEMENT,
        'max_daily_loss': 50000,
        'max_position_size': 100000
    }

class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = ':memory:'  # In-memory database for testing

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
