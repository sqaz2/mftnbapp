// inventory.js – client‑side script for building a move inventory

document.addEventListener('DOMContentLoaded', () => {
  const items = [];
  const itemsBody = document.getElementById('items-body');
  const inventoryInput = document.getElementById('inventory_data');
  const funMessageDiv = document.getElementById('fun-message');

  // Light‑hearted messages to make the process more enjoyable
  const messages = [
    "Nice! That’ll fit like a Tetris pro.",
    "Keep ’em coming – our trucks love a challenge!",
    "Another treasure for the voyage. Moving is our workout!",
    "Your sofa called – it’s excited for its road trip.",
    "Great! We’ve added that to our magic moving list.",
    "One step closer to your new beginning!"
  ];

  function showFunMessage() {
    const msg = messages[Math.floor(Math.random() * messages.length)];
    funMessageDiv.textContent = msg;
    funMessageDiv.style.opacity = 1;
    clearTimeout(funMessageDiv._timeout);
    funMessageDiv._timeout = setTimeout(() => {
      funMessageDiv.style.opacity = 0;
    }, 3000);
  }

  function renderTable() {
    itemsBody.innerHTML = '';
    items.forEach((itm, index) => {
      const tr = document.createElement('tr');
      const roomTd = document.createElement('td');
      roomTd.textContent = itm.room;
      const itemTd = document.createElement('td');
      itemTd.textContent = itm.item;
      const qtyTd = document.createElement('td');
      qtyTd.textContent = itm.quantity;
      const actionTd = document.createElement('td');
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-sm btn-danger';
      btn.textContent = 'Remove';
      btn.addEventListener('click', () => {
        items.splice(index, 1);
        renderTable();
      });
      actionTd.appendChild(btn);
      tr.appendChild(roomTd);
      tr.appendChild(itemTd);
      tr.appendChild(qtyTd);
      tr.appendChild(actionTd);
      itemsBody.appendChild(tr);
    });
    // Update hidden input with JSON representation
    inventoryInput.value = JSON.stringify(items);
  }

  document.getElementById('add-item').addEventListener('click', () => {
    const room = document.getElementById('room').value;
    const item = document.getElementById('item').value.trim();
    const quantityVal = document.getElementById('quantity').value;
    const quantity = parseInt(quantityVal, 10);
    if (!item || isNaN(quantity) || quantity < 1) {
      return;
    }
    items.push({ room, item, quantity });
    renderTable();
    showFunMessage();
    // Clear item description and quantity fields for next entry
    document.getElementById('item').value = '';
    document.getElementById('quantity').value = 1;
  });

  // Ensure hidden input is populated on form submit
  document.getElementById('inventory-form').addEventListener('submit', () => {
    inventoryInput.value = JSON.stringify(items);
  });
});