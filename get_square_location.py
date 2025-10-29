#!/usr/bin/env python3
"""
Copyright (c) 2025 Joshua Hendricks Cole (DBA: Corporation of Light). All Rights Reserved. PATENT PENDING.

Quick script to get your Square Location ID
"""

import requests
import json

# Your Square credentials
ACCESS_TOKEN = "EAAAl4MaYIoE7Z9VBatUCF445AGOMiPCwT1oQN-jRlPMguXhHmXPqzdMhu7OHXHS"

# Determine if this is sandbox or production based on token prefix
is_sandbox = ACCESS_TOKEN.startswith("EAAAl")  # Sandbox tokens start with EAAAl
environment = "sandbox" if is_sandbox else "production"

# API endpoint
base_url = "https://connect.squareup.com" if not is_sandbox else "https://connect.squareupsandbox.com"
url = f"{base_url}/v2/locations"

# Make request
headers = {
    "Square-Version": "2024-10-17",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 60)
print(f"Fetching Square Locations ({environment} mode)...")
print("=" * 60)

try:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        locations = data.get('locations', [])

        if not locations:
            print("\n⚠️  No locations found!")
            print("You may need to create a location in your Square dashboard.")
        else:
            print(f"\n✅ Found {len(locations)} location(s):\n")

            for i, loc in enumerate(locations, 1):
                print(f"Location {i}:")
                print(f"  Name:        {loc.get('name', 'N/A')}")
                print(f"  ID:          {loc.get('id', 'N/A')}")
                print(f"  Status:      {loc.get('status', 'N/A')}")
                print(f"  Currency:    {loc.get('currency', 'N/A')}")
                print(f"  Country:     {loc.get('country', 'N/A')}")
                print(f"  Address:     {loc.get('address', {}).get('address_line_1', 'N/A')}")
                print()

            # Show the primary location ID
            primary_location = locations[0]
            location_id = primary_location.get('id')

            print("=" * 60)
            print("📋 USE THIS LOCATION ID:")
            print("=" * 60)
            print(f"\n{location_id}\n")
            print("=" * 60)

    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 401:
            print("\n⚠️  Access token may be invalid or expired.")
        elif response.status_code == 403:
            print("\n⚠️  Access token doesn't have permission to view locations.")

except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 60)
print("Next Steps:")
print("=" * 60)
print("1. Copy the Location ID shown above")
print("2. Add it to Vercel environment variables")
print("3. Complete the Square integration setup")
print("=" * 60)
