// Carousel functionality
const slides = document.querySelectorAll("#carousel > div");
let current = 0;

function showSlide(index) {
  slides.forEach((slide, i) => {
    // Hide all slides
    slide.classList.remove(
      "opacity-100",
      "slide-active",
      "pointer-events-auto"
    );
    slide.classList.add("opacity-0", "pointer-events-none");

    // Show the active one
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
  const card = button.closest(".group"); // get parent card

  if (index > -1) {
    wishlist.splice(index, 1);
    card.classList.remove("active"); // toggle on parent
  } else {
    wishlist.push(productId);
    card.classList.add("active");
  }
}

function addToCart(productId) {
  cart.push(productId);

  const button = event.target.closest(".btn-primary, button");
  const originalText = button.innerHTML;

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
