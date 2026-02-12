const input = document.getElementById("todo-input");
const addBtn = document.getElementById("add-btn");
const list = document.getElementById("todo-list");

let todos = [];

// Load from LocalStorage on page load
window.addEventListener("DOMContentLoaded", () => {
  const saved = localStorage.getItem("todos");
  if (saved) {
    todos = JSON.parse(saved);
    renderTodos();
  }
});

// Save to LocalStorage
function saveTodos() {
  localStorage.setItem("todos", JSON.stringify(todos));
}

// Render todos
function renderTodos() {
  list.innerHTML = "";

  todos.forEach((todo, index) => {
    const li = document.createElement("li");

    const span = document.createElement("span");
    span.textContent = todo;
    span.className = "task-text";
    span.contentEditable = true;

    // Edit
    span.addEventListener("input", () => {
      todos[index] = span.textContent.trim();
      saveTodos();
    });

    const delBtn = document.createElement("button");
    delBtn.textContent = "Delete";

    // Delete
    delBtn.addEventListener("click", () => {
      todos.splice(index, 1);
      saveTodos();
      renderTodos();
    });

    li.appendChild(span);
    li.appendChild(delBtn);
    list.appendChild(li);
  });
}

// Add todo
addBtn.addEventListener("click", () => {
  const value = input.value.trim();
  if (!value) return;

  todos.push(value);
  input.value = "";
  saveTodos();
  renderTodos();
});
