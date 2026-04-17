## Orders
Creates an order --> reserve_stock
payment sucessful --> confirm_stock
payment unsuccessful --> nothing happens (This is because, a user can attempt to pay again or re-use that payment data)
order expires --> release_stocks 

Note: Stocks are only reserved when a user places an Order, rather than just adding the Item to their carts. This is to avoid tying up stocks even in cart abandonment, and to ensure a good Customer Experience.