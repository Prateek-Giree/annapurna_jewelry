// Carousel functionality
const slides = document.querySelectorAll("#carousel > div");
let current = 0;

function showSlide(index) {
  slides.forEach((slide, i) => {
    slide.classList.remove(
      "opacity-100",
      "slide-active",
      "pointer-events-auto"
    );
    slide.classList.add("opacity-0", "pointer-events-none");

    if (i === index) {
      slide.classList.remove("opacity-0", "pointer-events-none");
      slide.classList.add("opacity-100", "slide-active", "pointer-events-auto");
    }
  });
}

function nextSlide() {
  current = (current + 1) % slides.length;
  showSlide(current);
}

function prevSlide() {
  current = (current - 1 + slides.length) % slides.length;
  showSlide(current);
}
setInterval(nextSlide, 3000);
showSlide(current);


// Wishlist and Cart functionality
let wishlist = [];
let cart = [];

function toggleWishlist(button, productId) {
  const index = wishlist.indexOf(productId);
  const card = button.closest(".group");

  if (index > -1) {
    wishlist.splice(index, 1);
    card.classList.remove("active");
  } else {
    wishlist.push(productId);
    card.classList.add("active");
  }
}

function addToCart(productId, event) {
  event.preventDefault(); 
    const button = event.currentTarget;
    if (!isAuthenticated) {
        const loginUrl = button.dataset.loginUrl; 
        window.location.href = loginUrl;
        return;
    }

  button.innerHTML = `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="w-[16px] h-[16px]">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
    </svg>
    Added!
  `;
  button.style.backgroundColor = "#22c55e";

  setTimeout(() => {
    button.innerHTML = originalText;
    button.style.backgroundColor = "#000";
  }, 1500);

  fetch("/add-to-cart/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({ product_id: productId })
  })
  .then(res => res.json())
  .then(data => {
    console.log("Cart updated:", data);
    // optionally update cart count in navbar
    if (data.cart_count !== undefined) {
      document.querySelector("#cart-count").textContent = data.cart_count;
    }
  })
  .catch(err => console.error("Error adding to cart:", err));
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}


// Password show or hide
function togglePassword(fieldId) {
  const field = document.getElementById(fieldId);

  if (field.type === "password") {
    field.type = "text";
  } else {
    field.type = "password";
  }
}

// Check password strength
function checkPasswordStrength(password) {
  let strength = 0;
  let feedback = "";

  // If password is empty, reset to default state
  if (password.length === 0) {
    const strengthElement = document.getElementById("passwordStrength");
    const strengthText = strengthElement.querySelector(".strength-text");
    strengthElement.className = "password-strength";
    strengthText.textContent = "Password strength: Not entered";
    return;
  }

  // Check different criteria
  if (password.length >= 8) strength += 1;
  if (/[a-z]/.test(password)) strength += 1;
  if (/[A-Z]/.test(password)) strength += 1;
  if (/[0-9]/.test(password)) strength += 1;
  if (/[^A-Za-z0-9]/.test(password)) strength += 1;

  const strengthElement = document.getElementById("passwordStrength");
  const strengthText = strengthElement.querySelector(".strength-text");

  // Reset all classes
  strengthElement.className = "password-strength";

  // Apply appropriate strength class and feedback
  switch (strength) {
    case 0:
    case 1:
      strengthElement.classList.add("strength-weak");
      feedback = "Password strength: Weak";
      break;
    case 2:
      strengthElement.classList.add("strength-medium");
      feedback = "Password strength: Medium";
      break;
    case 3:
    case 4:
      strengthElement.classList.add("strength-strong");
      feedback = "Password strength: Strong";
      break;
    case 5:
      strengthElement.classList.add("strength-very-strong");
      feedback = "Password strength: Very Strong";
      break;
  }

  strengthText.textContent = feedback;
}

function resetForm() {
  if (
    confirm(
      "Are you sure you want to cancel? All unsaved changes will be lost."
    )
  ) {
    document.getElementById("profileForm").reset();
    location.reload();
  }
}

// Event listeners for password strength check
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("newPassword").addEventListener("input", function () {
    checkPasswordStrength(this.value);
  });
});


// Cart functionality
document.addEventListener("DOMContentLoaded", () => {
  const checkboxes = document.querySelectorAll("input[name='selected_items']");
  const quantityInputs = document.querySelectorAll(".quantity-input");

  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", updateCartTotal);
  });

  quantityInputs.forEach((input) => {
    input.addEventListener("input", () => {
      const row = input.closest("tr");
      updateRowSubtotal(row);
      updateCartTotal();
    });
  });

  document
    .querySelectorAll("tbody tr")
    .forEach((row) => updateRowSubtotal(row));
  updateCartTotal();
});

function updateRowSubtotal(row) {
  const priceText = row
    .querySelector(".unit-price")
    .textContent.replace("Rs", "")
    .trim();
  const price = parseFloat(priceText) || 0;
  const qtyInput = row.querySelector(".quantity-input");
  const qty = parseInt(qtyInput.value) || 0;
  const subtotal = (price * qty).toFixed(2);
  row.querySelector(".subtotal").textContent = `Rs ${subtotal}`;
}

function updateCartTotal() {
  let total = 0;
  document.querySelectorAll("tbody tr").forEach((row) => {
    const checkbox = row.querySelector("input[type='checkbox']");
    if (checkbox.checked) {
      const subtotalText = row
        .querySelector(".subtotal")
        .textContent.replace("Rs", "")
        .trim();
      total += parseFloat(subtotalText) || 0;
    }
  });

  total = total.toFixed(2);
  document.getElementById("cart-subtotal").textContent = `Rs ${total}`;
  document.getElementById("cart-total").textContent = `Rs ${total}`;
}
