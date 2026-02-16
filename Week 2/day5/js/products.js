const container = document.getElementById("productContainer");
const searchInput = document.getElementById("searchInput");
const sortSelect = document.getElementById("sortSelect");

let allProducts = [];

// Fetch Products
async function fetchProducts() {
  try {
    const res = await fetch("https://dummyjson.com/products");
    const data = await res.json();
    allProducts = data.products;
    renderProducts(allProducts);
  } catch (error) {
    console.error("Error fetching products:", error);
  }
}

// Render Products
function renderProducts(products) {
  container.innerHTML = "";

  if (!products || products.length === 0) {
    container.innerHTML = "<p>No products found.</p>";
    return;
  }

  products.forEach(product => {
    const card = document.createElement("div");
    card.classList.add("card");

    // Safe handling
    const title = product.title || "No Title";
    const price = Number(product.price) || 0;
    const rating =
      product.rating !== undefined && product.rating !== null
        ? Number(product.rating).toFixed(1)
        : "No rating";
    const image = product.thumbnail || "https://via.placeholder.com/300";

    card.innerHTML = `
      <img src="${image}" alt="${title}" />
      <h3>${title}</h3>
      <p class="rating-text">Rating: ${rating}</p>
      <p class="price">$${price.toFixed(2)}</p>
    `;

    container.appendChild(card);
  });
}

// Search Filter
searchInput.addEventListener("input", () => {
  const searchTerm = searchInput.value.toLowerCase();

  const filtered = allProducts.filter(product =>
    product.title.toLowerCase().includes(searchTerm)
  );

  renderProducts(filtered);
});

// Sort High → Low
sortSelect.addEventListener("change", () => {
  if (sortSelect.value === "high") {
    const sorted = [...allProducts].sort((a, b) => b.price - a.price);
    renderProducts(sorted);
  } else {
    renderProducts(allProducts);
  }
});

fetchProducts();
