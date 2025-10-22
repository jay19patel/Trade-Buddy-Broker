#!/usr/bin/env python3
"""
MongoDB utility functions for position management
"""

from pymongo import MongoClient
from app.config import config
from datetime import datetime
import json

class PositionManager:
    def __init__(self):
        self.mongo_client = MongoClient(config.mongodb_url)
        self.db = self.mongo_client[config.mongodb_database]
        self.positions_collection = self.db[config.mongodb_positions_collection]
    
    def get_all_positions(self, status=None):
        """Get all positions, optionally filtered by status"""
        query = {}
        if status:
            query['status'] = status
        return list(self.positions_collection.find(query))
    
    def get_position_by_symbol(self, symbol, status='open'):
        """Get position by symbol and status"""
        return self.positions_collection.find_one({
            'symbol': symbol,
            'status': status
        })
    
    def get_positions_summary(self):
        """Get summary of all positions"""
        pipeline = [
            {
                '$group': {
                    '_id': '$status',
                    'count': {'$sum': 1},
                    'total_pnl': {'$sum': '$total_pnl'},
                    'total_commission': {'$sum': '$total_commission'},
                    'avg_holding_time': {'$avg': '$holding_time_minutes'}
                }
            }
        ]
        return list(self.positions_collection.aggregate(pipeline))
    
    def get_profitable_positions(self):
        """Get all profitable positions"""
        return list(self.positions_collection.find({
            'status': 'closed',
            'total_pnl': {'$gt': 0}
        }))
    
    def get_losing_positions(self):
        """Get all losing positions"""
        return list(self.positions_collection.find({
            'status': 'closed',
            'total_pnl': {'$lt': 0}
        }))
    
    def get_positions_by_date_range(self, start_date, end_date):
        """Get positions within date range"""
        return list(self.positions_collection.find({
            'entry_datetime': {
                '$gte': start_date,
                '$lte': end_date
            }
        }))
    
    def delete_position(self, position_id):
        """Delete a position by ID"""
        result = self.positions_collection.delete_one({'_id': position_id})
        return result.deleted_count > 0
    
    def close_position_manually(self, symbol, close_price=None):
        """Manually close a position"""
        position = self.get_position_by_symbol(symbol, 'open')
        if not position:
            return False
        
        close_datetime = datetime.now()
        holding_time_minutes = (close_datetime - position['entry_datetime']).total_seconds() / 60
        
        update_data = {
            'status': 'closed',
            'close_datetime': close_datetime,
            'close_price': close_price or position['entry_price'],
            'holding_time_minutes': round(holding_time_minutes, 2),
            'updated_at': close_datetime
        }
        
        result = self.positions_collection.update_one(
            {'_id': position['_id']},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def print_positions_table(self, positions=None):
        """Print positions in a formatted table"""
        if positions is None:
            positions = self.get_all_positions()
        
        if not positions:
            print("No positions found.")
            return
        
        print(f"{'Symbol':<12} {'Side':<4} {'Status':<6} {'Entry Price':<12} {'PnL':<10} {'Commission':<12} {'Holding Time':<12}")
        print("-" * 80)
        
        for pos in positions:
            symbol = pos.get('symbol', 'N/A')[:11]
            side = pos.get('side', 'N/A')
            status = pos.get('status', 'N/A')
            entry_price = f"{pos.get('entry_price', 0):.4f}"
            pnl = f"{pos.get('total_pnl', 0):.4f}"
            commission = f"{pos.get('total_commission', 0):.4f}"
            holding_time = f"{pos.get('holding_time_minutes', 0):.1f}m"
            
            print(f"{symbol:<12} {side:<4} {status:<6} {entry_price:<12} {pnl:<10} {commission:<12} {holding_time:<12}")
    
    def export_positions_to_json(self, filename=None):
        """Export all positions to JSON file"""
        if filename is None:
            filename = f"positions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        positions = self.get_all_positions()
        # Convert ObjectId to string for JSON serialization
        for pos in positions:
            pos['_id'] = str(pos['_id'])
            if 'entry_datetime' in pos:
                pos['entry_datetime'] = pos['entry_datetime'].isoformat()
            if 'close_datetime' in pos and pos['close_datetime']:
                pos['close_datetime'] = pos['close_datetime'].isoformat()
            if 'created_at' in pos:
                pos['created_at'] = pos['created_at'].isoformat()
            if 'updated_at' in pos:
                pos['updated_at'] = pos['updated_at'].isoformat()
        
        with open(filename, 'w') as f:
            json.dump(positions, f, indent=2)
        
        print(f"Positions exported to {filename}")
        return filename
    
    def close(self):
        """Close MongoDB connection"""
        self.mongo_client.close()

def main():
    """Main function for command line usage"""
    manager = PositionManager()
    
    try:
        print("=== Position Manager ===")
        print("1. View all positions")
        print("2. View open positions")
        print("3. View closed positions")
        print("4. View positions summary")
        print("5. Export to JSON")
        print("6. Exit")
        
        while True:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                positions = manager.get_all_positions()
                manager.print_positions_table(positions)
            
            elif choice == '2':
                positions = manager.get_all_positions('open')
                manager.print_positions_table(positions)
            
            elif choice == '3':
                positions = manager.get_all_positions('closed')
                manager.print_positions_table(positions)
            
            elif choice == '4':
                summary = manager.get_positions_summary()
                print("\n=== Positions Summary ===")
                for item in summary:
                    print(f"Status: {item['_id']}")
                    print(f"  Count: {item['count']}")
                    print(f"  Total PnL: {item['total_pnl']:.4f}")
                    print(f"  Total Commission: {item['total_commission']:.4f}")
                    print(f"  Avg Holding Time: {item['avg_holding_time']:.2f} minutes")
                    print()
            
            elif choice == '5':
                filename = manager.export_positions_to_json()
                print(f"Exported to {filename}")
            
            elif choice == '6':
                break
            
            else:
                print("Invalid choice. Please try again.")
    
    finally:
        manager.close()

if __name__ == "__main__":
    main()
