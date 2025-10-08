function addToCart(productId) {
  fetch(`/add-to-cart/${productId}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": "{{ csrf_token }}",
      "X-Requested-With": "XMLHttpRequest",
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: "qty=1"
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      document.getElementById("cart-count").innerText = data.cart_count;
      alert(data.message); // 🔔 replace with a toast/snackbar later
    } else {
      alert(data.message);
    }
  })
  .catch(err => console.error(err));
}