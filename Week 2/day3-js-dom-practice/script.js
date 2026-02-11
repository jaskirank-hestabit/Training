const accordionItems = document.querySelectorAll(".accordion-item");

accordionItems.forEach((item) => {
  const header = item.querySelector(".accordion-header");

  header.addEventListener("click", () => {

    const isActive = item.classList.contains("active");

    // Close all items
    accordionItems.forEach((el) => {
      el.classList.remove("active");
      el.querySelector(".toggle-btn").textContent = "+";
    });

    // If it was NOT active before → open it
    if (!isActive) {
      item.classList.add("active");
      item.querySelector(".toggle-btn").textContent = "-";
    }
  });
});
