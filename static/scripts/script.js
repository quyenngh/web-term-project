// menu page

// Subtracts 1 from the quantity input field
function subtractOne(button) {
  var input = button.nextElementSibling;
  var value = parseInt(input.value);
  if (value >= 1) {
    input.value = value - 1;
  }
}

// Adds 1 to the quantity input field
function addOne(button) {
  var input = button.previousElementSibling;
  var value = parseInt(input.value);
  input.value = value + 1;
}

// Retrieves the order summary from the menu page
function getOrderSummary() {
  var orderSummary = {};

  // Get customer name and address
  var name = document.getElementById("name").value;
  var address = document.getElementById("address").value;
  orderSummary.name = name;
  orderSummary.address = address;
  orderSummary.products = {};

  // Iterate through each category and item to gather selected products
  var categories = document
    .getElementsByClassName("menuItem")[0]
    .getElementsByTagName("h2");

  for (var i = 0; i < categories.length; i++) {
    var category = categories[i];
    var categoryName = category.id;
    var itemsContainer = category.nextElementSibling;
    var items = itemsContainer.querySelectorAll(".itemType li");

    for (var j = 0; j < items.length; j++) {
      var item = items[j];
      var itemName = item.getElementsByTagName("h3")[0].textContent;
      var countInput = item.getElementsByClassName("count")[0];
      var itemCount = parseInt(countInput.value);

      // Add selected items to the order summary
      if (itemCount > 0) {
        if (!orderSummary.products[categoryName]) {
          orderSummary.products[categoryName] = [];
        }

        orderSummary.products[categoryName].push({
          name: itemName,
          count: itemCount,
        });
      }
    }
  }

  return JSON.stringify(orderSummary);
}

// Submits the order to the server
async function submitOrder() {
  const order_summary = getOrderSummary();
  const authStatus = document.getElementById("authStatus").value;

  // Check if the user is authenticated
  if (authStatus === "false") {
    alert("Login required. Please log in first.");
    return;
  }

  try {
    // Send a POST request to create the order
    const response = await fetch("/order", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(order_summary),
    });

    if (response.ok) {
      alert("Thank you for your ordering!");
      const data = await response.json();
      window.location.href = data.location;
    } else {
      const errorData = await response.json();
      alert(errorData.error);
    }
  } catch (error) {
    console.error("Error ordering:", error);
  }
}

// customize page

// Selects an item and manages selected items based on category
var selectedItems = {};

function selectItem(button, itemName, itemCategory) {
  if (itemCategory !== "Toppings") {
    // Deselect all buttons in the category except for Toppings
    var buttons = document.querySelectorAll(
      `button[data-category="${itemCategory}"]`
    );

    buttons.forEach(function (btn) {
      if (btn.dataset.category !== "Toppings") {
        btn.classList.remove("selected");
        delete selectedItems[btn.dataset.category];
      }
    });
  }

  if (button.classList.contains("selected")) {
    // Deselect the item
    button.classList.remove("selected");
    if (itemCategory in selectedItems) {
      const categoryItems = selectedItems[itemCategory];
      const itemIndex = categoryItems.indexOf(itemName);
      if (itemIndex !== -1) {
        categoryItems.splice(itemIndex, 1);
        if (categoryItems.length === 0) {
          delete selectedItems[itemCategory];
        }
      }
    }
  } else {
    if (itemCategory === "Toppings") {
      // Limit the toppings to 3 items
      var toppingsCount = Object.keys(selectedItems["Toppings"] || {}).length;
      if (toppingsCount >= 3) {
        alert("You can select up to 3 toppings.");
        return;
      }
    }

    // Select the item
    button.classList.add("selected");
    if (!(itemCategory in selectedItems)) {
      selectedItems[itemCategory] = [];
    }
    selectedItems[itemCategory].push(itemName);
  }
}

// Creates a custom drink by sending selected items to the server
async function createDrink() {
  const authStatus = document.getElementById("authStatus").value;

  // Check if the user is authenticated
  if (authStatus === "false") {
    alert("Login required. Please log in first.");
    return;
  }

  try {
    // Send a POST request to create the custom drink
    const response = await fetch("/customize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(selectedItems),
    });

    if (response.ok) {
      const result = await response.json();
      alert("Item added to Menu!");
      window.location.href = result.url;
    } else {
      const errorData = await response.json();
      alert(errorData.error);
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

// Clears the text area for feedback
function clearTextArea() {
  document.getElementById("feedback-textarea").value = "";
}

// Submits the feedback to the server
async function submitFeedback(event) {
  event.preventDefault();
  const message = document.getElementById("feedback-textarea").value;

  if (!message.trim()) {
    alert("Please enter a message.");
    return;
  }

  const feedback = {
    message: message,
  };

  try {
    // Send a POST request to submit the feedback
    const response = await fetch("/feedback", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(feedback),
    });
    clearTextArea();
    alert("Thank you for your feedback!");
  } catch (error) {
    console.error("Error saving feedback:", error);
  }
}
