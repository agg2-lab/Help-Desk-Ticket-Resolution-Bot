const bodyEl = document.getElementById("tickets-body");
const refreshBtn = document.getElementById("refresh-btn");

function statusOptions(currentStatus) {
  const statuses = ["open", "in_progress", "resolved", "closed"];
  return statuses
    .map((s) => `<option value="${s}" ${s === currentStatus ? "selected" : ""}>${s}</option>`)
    .join("");
}

async function updateStatus(ticketId, status) {
  const res = await fetch(`/tickets/${ticketId}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) {
    throw new Error(`Unable to update ticket #${ticketId}`);
  }
}

function renderRows(tickets) {
  bodyEl.innerHTML = "";
  tickets.forEach((ticket) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${ticket.id}</td>
      <td>${ticket.user_id}</td>
      <td>${ticket.category}</td>
      <td>${ticket.priority}</td>
      <td>
        <select data-ticket-id="${ticket.id}" class="status-select">
          ${statusOptions(ticket.status)}
        </select>
      </td>
      <td>${ticket.summary}</td>
      <td>${new Date(ticket.created_at).toLocaleString()}</td>
      <td><button type="button" data-ticket-id="${ticket.id}" class="save-btn">Save</button></td>
    `;
    bodyEl.appendChild(tr);
  });

  document.querySelectorAll(".save-btn").forEach((btn) => {
    btn.addEventListener("click", async (event) => {
      const ticketId = event.target.getAttribute("data-ticket-id");
      const select = document.querySelector(`select[data-ticket-id="${ticketId}"]`);
      try {
        await updateStatus(ticketId, select.value);
        await loadTickets();
      } catch (err) {
        alert(err.message);
      }
    });
  });
}

async function loadTickets() {
  const res = await fetch("/tickets?limit=200");
  if (!res.ok) {
    throw new Error("Unable to load tickets");
  }
  const tickets = await res.json();
  renderRows(tickets);
}

refreshBtn.addEventListener("click", async () => {
  try {
    await loadTickets();
  } catch (err) {
    alert(err.message);
  }
});

loadTickets().catch((err) => {
  bodyEl.innerHTML = `<tr><td colspan="8">Error loading tickets: ${err.message}</td></tr>`;
});
