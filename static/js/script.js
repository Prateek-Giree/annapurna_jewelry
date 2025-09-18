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
