import sys
import os

# Add src to path so we can import from it
sys.path.append('src')

from apis.order_apis import OrderAPIs

def test_order_apis():
    """Test the OrderAPIs functionality"""
    api = OrderAPIs()
    
    print("=" * 50)
    print("TESTING ORDER APIS")
    print("=" * 50)
    
    # Test 1: Order tracking for existing customer
    print("\n1. Testing order tracking for john@example.com:")
    result = api.orderTracking("john@example.com")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['success']:
        print(f"Total orders: {result['data']['total_orders']}")
        for order in result['data']['orders']:
            print(f"  - Order {order['order_id']}: {order['status']}")
    
    # Test 2: Order tracking for specific order
    print("\n2. Testing specific order tracking (ORD001):")
    result = api.orderTracking("john@example.com", "ORD001")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['success']:
        print(f"Order ID: {result['data']['order_id']}")
        print(f"Status: {result['data']['status']}")
        print(f"Total: ${result['data']['total_amount']}")
    
    # Test 3: Order tracking for non-existent customer
    print("\n3. Testing order tracking for non-existent customer:")
    result = api.orderTracking("nonexistent@example.com")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Test 4: Order cancellation for already cancelled order
    print("\n4. Testing cancellation of already cancelled order (ORD001):")
    result = api.orderCancellation("john@example.com", "ORD001")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Test 5: Order cancellation for shipped order (should fail)
    print("\n5. Testing cancellation of shipped order (ORD002):")
    result = api.orderCancellation("john@example.com", "ORD002")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    # Test 6: Order tracking for Jane
    print("\n6. Testing order tracking for jane@example.com:")
    result = api.orderTracking("jane@example.com")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if result['success']:
        print(f"Total orders: {result['data']['total_orders']}")
        for order in result['data']['orders']:
            print(f"  - Order {order['order_id']}: {order['status']}")

if __name__ == "__main__":
    test_order_apis()