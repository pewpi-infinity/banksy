#!/usr/bin/env python3
import os
import sys
import subprocess

print("∞ Run-Cart Engine (Python3 clean)\n")

# Make sure a cart was provided
if len(sys.argv) < 2:
    print("Usage: python3 run_cart.py cart_name.py")
    sys.exit(1)

cart = sys.argv[1]

if not os.path.exists(cart):
    print(f"Cart not found: {cart}")
    sys.exit(1)

print(f"∞ Running cart: {cart}\n")

# Execute the cart using python3 only
result = subprocess.run(["python3", cart])

print("\n∞ Cart finished.")
