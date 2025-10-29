#!/usr/bin/env python3
"""
Copyright (c) 2025 Joshua Hendricks Cole (DBA: Corporation of Light). All Rights Reserved. PATENT PENDING.

Visit Counter API for TheGAVL
Tracks page visits, unique visitors, and generates analytics
"""

import json
import time
from http.server import BaseHTTPRequestHandler
from datetime import datetime
from collections import defaultdict
import hashlib

# In-memory storage (for production, use Redis or database)
VISIT_DATA = defaultdict(int)
UNIQUE_VISITORS = set()
PAGE_VIEWS = defaultdict(int)
DAILY_STATS = defaultdict(lambda: defaultdict(int))


class handler(BaseHTTPRequestHandler):
    """Serverless function handler for visit tracking"""

    def send_json_response(self, status_code: int, data: dict):
        """Send JSON response with CORS headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Track a visit"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            visit_data = json.loads(body)

            # Extract visit information
            page = visit_data.get('page', 'unknown')
            url = visit_data.get('url', '')
            timestamp = visit_data.get('timestamp', datetime.now().isoformat())
            referrer = visit_data.get('referrer', 'direct')
            ip_address = self.headers.get('X-Forwarded-For', 'unknown')

            # Create unique visitor ID (hash of IP + user agent)
            user_agent = self.headers.get('User-Agent', '')
            visitor_id = hashlib.md5(f"{ip_address}{user_agent}".encode()).hexdigest()

            # Track visit
            VISIT_DATA['total_visits'] += 1
            PAGE_VIEWS[page] += 1
            UNIQUE_VISITORS.add(visitor_id)

            # Track daily stats
            today = datetime.now().strftime('%Y-%m-%d')
            DAILY_STATS[today]['visits'] += 1
            DAILY_STATS[today]['unique_visitors'] = len(UNIQUE_VISITORS)

            # Log to console (visible in Vercel logs)
            print(f"Visit tracked: {page} | Visitor: {visitor_id[:8]}... | Referrer: {referrer}")

            self.send_json_response(200, {
                'success': True,
                'message': 'Visit tracked',
                'stats': {
                    'total_visits': VISIT_DATA['total_visits'],
                    'unique_visitors': len(UNIQUE_VISITORS),
                    'page_views': dict(PAGE_VIEWS)
                }
            })

        except Exception as e:
            self.send_json_response(500, {
                'success': False,
                'error': str(e)
            })

    def do_GET(self):
        """Get visit statistics"""
        try:
            # Return current statistics
            today = datetime.now().strftime('%Y-%m-%d')

            stats = {
                'total_visits': VISIT_DATA['total_visits'],
                'unique_visitors': len(UNIQUE_VISITORS),
                'page_views': dict(PAGE_VIEWS),
                'daily_stats': dict(DAILY_STATS),
                'today': today,
                'top_pages': sorted(PAGE_VIEWS.items(), key=lambda x: x[1], reverse=True)[:10]
            }

            self.send_json_response(200, {
                'success': True,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            self.send_json_response(500, {
                'success': False,
                'error': str(e)
            })


# For local testing
if __name__ == '__main__':
    print("Visit Counter API - Local Test Mode")
    print("=" * 50)
    print("This tracks page visits and unique visitors")
    print("Deploy to Vercel to use in production")
