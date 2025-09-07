import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class JSONDataOperations:
    def __init__(self):
        self.customers_file = "data/customers.json"
        self.orders_file = "data/orders.json"
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_files()
    
    def _init_files(self):
        """Initialize JSON files if they don't exist"""
        if not os.path.exists(self.customers_file):
            with open(self.customers_file, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(self.orders_file):
            with open(self.orders_file, 'w') as f:
                json.dump([], f)
    
    def _load_customers(self) -> List[Dict]:
        """Load customers from JSON file"""
        with open(self.customers_file, 'r') as f:
            return json.load(f)
    
    def _load_orders(self) -> List[Dict]:
        """Load orders from JSON file"""
        with open(self.orders_file, 'r') as f:
            return json.load(f)
    
    def _save_orders(self, orders: List[Dict]):
        """Save orders to JSON file"""
        with open(self.orders_file, 'w') as f:
            json.dump(orders, f, indent=2)
    
    def get_customer_by_email(self, email: str) -> Optional[Dict]:
        """Get customer by email"""
        customers = self._load_customers()
        for customer in customers:
            if customer['email'] == email:
                return customer
        return None
    
    def get_orders_by_email(self, email: str) -> Optional[List[Dict]]:
        """Get all orders for a customer by email"""
        customer = self.get_customer_by_email(email)
        if not customer:
            return None
        
        orders = self._load_orders()
        customer_orders = []
        for order in orders:
            if order['customer_id'] == customer['customer_id']:
                # Add customer info to order for easy access
                order_with_customer = order.copy()
                order_with_customer['customer'] = customer
                customer_orders.append(order_with_customer)
        
        return customer_orders if customer_orders else None
    
    def get_order_by_id(self, order_id: str, email: str) -> Optional[Dict]:
        """Get specific order by ID and email verification"""
        customer = self.get_customer_by_email(email)
        if not customer:
            return None
        
        orders = self._load_orders()
        for order in orders:
            if order['order_id'] == order_id and order['customer_id'] == customer['customer_id']:
                # Add customer info to order
                order_with_customer = order.copy()
                order_with_customer['customer'] = customer
                return order_with_customer
        
        return None
    
    def can_cancel_order(self, order: Dict) -> bool:
        """Check if order can be cancelled based on business rules"""
        if not order:
            return False
        
        try:
            # Parse order date - handle both with and without timezone
            order_date_str = order['order_date']
            if order_date_str.endswith('Z'):
                order_date = datetime.fromisoformat(order_date_str.replace('Z', '+00:00'))
            elif '+' in order_date_str or order_date_str.endswith('00:00'):
                order_date = datetime.fromisoformat(order_date_str)
            else:
                # Assume local timezone if no timezone info
                order_date = datetime.fromisoformat(order_date_str)
            
            # Calculate days difference
            days_old = (datetime.now() - order_date).days
            
            # Check if order is within 10 days
            if days_old > 10:
                return False
            
            # Check status - orders cannot be cancelled if shipped, delivered, or already cancelled
            non_cancellable_statuses = ['shipped', 'delivered', 'cancelled']
            if order['status'] in non_cancellable_statuses:
                return False
            
            return True
            
        except Exception as e:
            print(f"Error parsing date for order {order.get('order_id', 'unknown')}: {e}")
            return False
    
    def update_order_status(self, order_id: str, new_status: str) -> bool:
        """Update order status"""
        orders = self._load_orders()
        for order in orders:
            if order['order_id'] == order_id:
                order['status'] = new_status
                self._save_orders(orders)
                return True
        return False