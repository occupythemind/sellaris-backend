### Handles stocks disputes to prevent business losses
A simple scenerio like this could have been:

```context
User A adds item (stock = 10)
User B adds item (stock = 10)

Both carts look valid ✔

User A creates order → reserves 8
User B creates order → now only 2 left 
```
So, Cart ≠ guaranteed stock

But, because sellaris check the availabilty of a stock at reserve_order() in order creation:
```py
--snip--
if quantity > available:
    raise Exception("Insufficient stock")
--snip--
```
We get to avoid this coincidence. Because:
✔ Uses select_for_update() (locks row)
✔ Checks real-time availability
✔ Rejects if insufficient
✔ Runs inside transaction

Therefore, we are able to prevent:
❌ Overselling
❌ Race conditions
❌ Stock corruption

But to improve User UX, we:
✔ Don’t fail hard
✔ Adjust cart automatically
✔ Inform user what changed
✔ Still allow order creation (even if some items go to 0)


