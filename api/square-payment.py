#!/usr/bin/env python3
"""
Copyright (c) 2025 Joshua Hendricks Cole (DBA: Corporation of Light). All Rights Reserved. PATENT PENDING.

Square Payment Processing for TheGAVL
Serverless function for Vercel deployment
"""

import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler
from typing import Dict, Any

# Square API Configuration
# Set these in Vercel environment variables:
# SQUARE_ACCESS_TOKEN - Your Square access token
# SQUARE_LOCATION_ID - Your Square location ID
# SQUARE_ENVIRONMENT - 'sandbox' or 'production'

SQUARE_ACCESS_TOKEN = os.environ.get('SQUARE_ACCESS_TOKEN', '')
SQUARE_LOCATION_ID = os.environ.get('SQUARE_LOCATION_ID', '')
SQUARE_ENVIRONMENT = os.environ.get('SQUARE_ENVIRONMENT', 'sandbox')

# Pricing configuration
PACKAGES = {
    'single': {
        'name': 'Single Verdict',
        'verdicts': 1,
        'amount': 3900,  # $39.00 in cents
        'validity_days': 30
    },
    'professional': {
        'name': 'Professional Package',
        'verdicts': 40,
        'amount': 39900,  # $399.00 in cents
        'validity_days': 90
    },
    'firm': {
        'name': 'Firm Package',
        'verdicts': 125,
        'amount': 99900,  # $999.00 in cents
        'validity_days': 180
    }
}


class handler(BaseHTTPRequestHandler):
    """Serverless function handler for Square payments"""

    def send_json_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response with CORS headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle payment processing"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            request_data = json.loads(body)

            action = request_data.get('action', 'process_payment')

            if action == 'create_payment':
                # Create payment intent
                result = self.create_payment_intent(request_data)
                self.send_json_response(200, result)

            elif action == 'process_payment':
                # Process the payment with Square
                result = self.process_square_payment(request_data)
                self.send_json_response(200, result)

            elif action == 'verify_payment':
                # Verify payment status
                result = self.verify_payment_status(request_data)
                self.send_json_response(200, result)

            else:
                self.send_json_response(400, {
                    'success': False,
                    'error': f'Unknown action: {action}'
                })

        except Exception as e:
            self.send_json_response(500, {
                'success': False,
                'error': str(e),
                'message': 'Payment processing failed'
            })

    def create_payment_intent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment intent for the specified package"""
        try:
            package_type = data.get('package')
            user_email = data.get('email')
            user_name = data.get('name')

            if not package_type or package_type not in PACKAGES:
                return {
                    'success': False,
                    'error': 'Invalid package type'
                }

            package_info = PACKAGES[package_type]

            # Generate unique idempotency key
            idempotency_key = str(uuid.uuid4())

            return {
                'success': True,
                'payment_intent': {
                    'idempotency_key': idempotency_key,
                    'package': package_type,
                    'package_name': package_info['name'],
                    'amount': package_info['amount'],
                    'verdicts': package_info['verdicts'],
                    'validity_days': package_info['validity_days'],
                    'currency': 'USD',
                    'user_email': user_email,
                    'user_name': user_name
                },
                'square_config': {
                    'application_id': self.get_square_application_id(),
                    'location_id': SQUARE_LOCATION_ID,
                    'environment': SQUARE_ENVIRONMENT
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create payment intent: {str(e)}'
            }

    def process_square_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment with Square API"""
        try:
            # Extract payment details
            source_id = data.get('source_id')  # Card nonce from Square SDK
            idempotency_key = data.get('idempotency_key')
            package_type = data.get('package')
            user_email = data.get('email')
            user_name = data.get('name')

            if not source_id or not idempotency_key or not package_type:
                return {
                    'success': False,
                    'error': 'Missing required payment information'
                }

            package_info = PACKAGES.get(package_type)
            if not package_info:
                return {
                    'success': False,
                    'error': 'Invalid package type'
                }

            # In production, this would call Square's Payments API
            if SQUARE_ACCESS_TOKEN and SQUARE_ENVIRONMENT == 'production':
                payment_result = self.call_square_api(
                    source_id=source_id,
                    idempotency_key=idempotency_key,
                    amount=package_info['amount'],
                    currency='USD',
                    note=f"{package_info['name']} - {user_email}"
                )
            else:
                # Demo mode - simulate successful payment
                payment_result = {
                    'success': True,
                    'payment_id': f'DEMO-{uuid.uuid4().hex[:12]}',
                    'status': 'COMPLETED',
                    'amount': package_info['amount'],
                    'timestamp': time.time()
                }

            if payment_result.get('success'):
                # Allocate verdicts to user
                allocation_result = self.allocate_verdicts(
                    user_email=user_email,
                    user_name=user_name,
                    package_type=package_type,
                    verdicts=package_info['verdicts'],
                    validity_days=package_info['validity_days'],
                    payment_id=payment_result['payment_id'],
                    amount_paid=package_info['amount'] / 100.0  # Convert cents to dollars
                )

                return {
                    'success': True,
                    'payment_id': payment_result['payment_id'],
                    'verdicts_added': package_info['verdicts'],
                    'validity_days': package_info['validity_days'],
                    'message': f'Payment successful! {package_info["verdicts"]} verdict(s) added to your account.',
                    'allocation': allocation_result
                }
            else:
                return {
                    'success': False,
                    'error': payment_result.get('error', 'Payment failed')
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Payment processing error: {str(e)}'
            }

    def call_square_api(self, source_id: str, idempotency_key: str,
                       amount: int, currency: str, note: str) -> Dict[str, Any]:
        """Call Square Payments API (production implementation)"""
        try:
            import requests

            url = f'https://connect.squareup{"sandbox" if SQUARE_ENVIRONMENT == "sandbox" else ""}.com/v2/payments'

            headers = {
                'Authorization': f'Bearer {SQUARE_ACCESS_TOKEN}',
                'Content-Type': 'application/json',
                'Square-Version': '2024-10-17'
            }

            payload = {
                'source_id': source_id,
                'idempotency_key': idempotency_key,
                'amount_money': {
                    'amount': amount,
                    'currency': currency
                },
                'location_id': SQUARE_LOCATION_ID,
                'note': note
            }

            response = requests.post(url, json=payload, headers=headers)
            result = response.json()

            if response.status_code == 200:
                payment = result.get('payment', {})
                return {
                    'success': True,
                    'payment_id': payment.get('id'),
                    'status': payment.get('status'),
                    'amount': payment.get('amount_money', {}).get('amount'),
                    'timestamp': time.time()
                }
            else:
                return {
                    'success': False,
                    'error': result.get('errors', [{}])[0].get('detail', 'Payment failed')
                }

        except ImportError:
            return {
                'success': False,
                'error': 'Square API library not available. Install with: pip install requests'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Square API error: {str(e)}'
            }

    def allocate_verdicts(self, user_email: str, user_name: str,
                         package_type: str, verdicts: int, validity_days: int,
                         payment_id: str, amount_paid: float) -> Dict[str, Any]:
        """Allocate verdicts to user's account"""
        try:
            # Get current user data
            import json

            # In production, this would update Supabase
            # For now, return allocation details that frontend can store

            import datetime
            expiration_date = datetime.datetime.now() + datetime.timedelta(days=validity_days)

            allocation = {
                'user_email': user_email,
                'user_name': user_name,
                'package_type': package_type,
                'verdicts_purchased': verdicts,
                'amount_paid': amount_paid,
                'payment_id': payment_id,
                'purchase_date': datetime.datetime.now().isoformat(),
                'expiration_date': expiration_date.isoformat(),
                'validity_days': validity_days,
                'status': 'active'
            }

            return {
                'success': True,
                'allocation': allocation
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Allocation error: {str(e)}'
            }

    def verify_payment_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify payment status with Square"""
        try:
            payment_id = data.get('payment_id')

            if not payment_id:
                return {
                    'success': False,
                    'error': 'Missing payment_id'
                }

            # In demo mode, assume payment is completed
            if payment_id.startswith('DEMO-'):
                return {
                    'success': True,
                    'status': 'COMPLETED',
                    'verified': True
                }

            # In production, query Square API for payment status
            if SQUARE_ACCESS_TOKEN:
                return self.query_square_payment(payment_id)
            else:
                return {
                    'success': False,
                    'error': 'Square API not configured'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Verification error: {str(e)}'
            }

    def query_square_payment(self, payment_id: str) -> Dict[str, Any]:
        """Query Square for payment status"""
        try:
            import requests

            url = f'https://connect.squareup{"sandbox" if SQUARE_ENVIRONMENT == "sandbox" else ""}.com/v2/payments/{payment_id}'

            headers = {
                'Authorization': f'Bearer {SQUARE_ACCESS_TOKEN}',
                'Square-Version': '2024-10-17'
            }

            response = requests.get(url, headers=headers)
            result = response.json()

            if response.status_code == 200:
                payment = result.get('payment', {})
                return {
                    'success': True,
                    'status': payment.get('status'),
                    'verified': payment.get('status') == 'COMPLETED'
                }
            else:
                return {
                    'success': False,
                    'error': 'Payment not found'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Query error: {str(e)}'
            }

    def get_square_application_id(self) -> str:
        """Get Square Application ID based on environment"""
        # You need to set this based on your Square application
        if SQUARE_ENVIRONMENT == 'sandbox':
            return os.environ.get('SQUARE_APPLICATION_ID_SANDBOX', 'sandbox-sq0idb-XXXXXX')
        else:
            return os.environ.get('SQUARE_APPLICATION_ID', 'sq0idp-XXXXXX')


# For local testing
if __name__ == '__main__':
    print("Square Payment API - Local Test Mode")
    print("=" * 50)

    # Test creating payment intent
    test_request = {
        'action': 'create_payment',
        'package': 'single',
        'email': 'test@example.com',
        'name': 'Test User'
    }

    print("\nTest Request:", json.dumps(test_request, indent=2))

    # This would be handled by the handler in production
    print("\nNote: This is the serverless function. Deploy to Vercel to use.")
    print("Set environment variables: SQUARE_ACCESS_TOKEN, SQUARE_LOCATION_ID, SQUARE_ENVIRONMENT")
