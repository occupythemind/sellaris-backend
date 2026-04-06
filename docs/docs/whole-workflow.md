## Orders
Creates an order --> reserve_stock
payment sucessful --> confirm_stock
payment unsuccessful --> nothing happens (This is because, a user can attempt to pay again or re-use that payment data)
order expires --> release_stocks 