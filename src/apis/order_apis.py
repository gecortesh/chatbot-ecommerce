from datetime import datetime
from typing import Dict, Optional
from database.json_operations import JSONDataOperations

class OrderAPIs:
    def __init__(self):
        self.db = JSONDataOperations()
    
    def orderTracking(self, email: str, order_id: Optional[str] = None) -> Dict:
        """
        Track orders for a customer
        
        Args:
            email: Customer email address
            order_id: Optional specific order ID to track
            
        Returns:
            Dict with success status, data, and message
        """
        try:
            if not email:
                return {
                    "success": False,
                    "data": None,
                    "message": "Email address is required for order tracking"
                }
            
            # Check if customer exists
            customer = self.db.get_customer_by_email(email)
            if not customer:
                return {
                    "success": False,
                    "data": None,
                    "message": f"No customer found with email: {email}"
                }
            
            if order_id:
                # Get specific order
                order = self.db.get_order_by_id(order_id, email)
                if not order:
                    return {
                        "success": False,
                        "data": None,
                        "message": f"Order {order_id} not found for {email}"
                    }
                
                return {
                    "success": True,
                    "data": {
                        "order_id": order["order_id"],
                        "status": order["status"],
                        "customer_name": order["customer"]["name"],
                        "order_date": order["order_date"][:10],  # Just date part
                        "items": order["items"],
                        "total_amount": order["total_amount"],
                        "payment_method": order["payment_method"]
                    },
                    "message": "Order found"
                }
            else:
                # Get all orders for customer
                orders = self.db.get_orders_by_email(email)
                if not orders:
                    return {
                        "success": False,
                        "data": None,
                        "message": f"No orders found for {email}"
                    }
                
                return {
                    "success": True,
                    "data": {
                        "orders": orders,
                        "customer": customer,
                        "total_orders": len(orders)
                    },
                    "message": f"Found {len(orders)} order(s) for {email}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"Error tracking order: {str(e)}"
            }
    
    def orderCancellation(self, email: str, order_id: str) -> Dict:
        """
        Cancel an order for a customer
        
        Args:
            email: Customer email address
            order_id: Order ID to cancel
            
        Returns:
            Dict with success status, data, and message
        """
        try:
            if not email or not order_id:
                return {
                    "success": False,
                    "data": None,
                    "message": "Both email and order ID are required for cancellation"
                }
            
            # Get the order
            order = self.db.get_order_by_id(order_id, email)
            if not order:
                return {
                    "success": False,
                    "data": None,
                    "message": f"Order {order_id} not found for {email}"
                }
            
            # Check if order can be cancelled
            if not self.db.can_cancel_order(order):
                # Determine specific reason
                order_date = datetime.fromisoformat(order['order_date'].replace('Z', '+00:00'))
                days_old = (datetime.now() - order_date).days
                
                if days_old > 10:
                    return {
                        "success": False,
                        "data": {
                            "order": order,
                            "days_old": days_old
                        },
                        "message": f"Order {order_id} cannot be cancelled. It was placed {days_old} days ago (limit: 10 days)"
                    }
                elif order['status'] in ['shipped', 'delivered', 'cancelled']:
                    return {
                        "success": False,
                        "data": {
                            "order": order
                        },
                        "message": f"Order {order_id} cannot be cancelled. Current status: {order['status']}"
                    }
            
            # Cancel the order
            success = self.db.update_order_status(order_id, 'cancelled')
            if success:
                # Get updated order
                updated_order = self.db.get_order_by_id(order_id, email)
                return {
                    "success": True,
                    "data": {
                        "order": updated_order,
                        "previous_status": order['status']
                    },
                    "message": f"Order {order_id} has been successfully cancelled"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"Failed to cancel order {order_id}. Please try again"
                }
                
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"Error cancelling order: {str(e)}"
            }
