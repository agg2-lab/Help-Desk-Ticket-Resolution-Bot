const form = document.getElementById("chat-form");
const responseCard = document.getElementById("response-card");
const responseText = document.getElementById("response-text");
const stepsList = document.getElementById("steps-list");
const meta = document.getElementById("meta");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const user_id = document.getElementById("user_id").value.trim();
  const issue_text = document.getElementById("issue_text").value.trim();
  const context = document.getElementById("context").value.trim();

  if (!user_id || !issue_text) {
    return;
  }

  responseText.textContent = "Processing request...";
  stepsList.innerHTML = "";
  meta.textContent = "";
  responseCard.classList.remove("hidden");

  try {
    const payload = { user_id, issue_text, context: context || null };
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`Request failed (${res.status})`);
    }

    const data = await res.json();

    responseText.textContent = data.response_text;
    stepsList.innerHTML = "";
    (data.recommended_steps || []).forEach((step) => {
      const li = document.createElement("li");
      li.textContent = step;
      stepsList.appendChild(li);
    });

    const ticketLabel = data.ticket_created
      ? `Ticket created: #${data.ticket_id}`
      : "No ticket created";
    const confidencePct = `${Math.round((data.confidence || 0) * 100)}%`;
    const escalationLabel = data.escalated_to_human ? "Escalated to human: yes" : "Escalated to human: no";
    const snLabel = data.servicenow_incident_number
      ? `ServiceNow incident: ${data.servicenow_incident_number}`
      : "ServiceNow incident: not created";
    meta.textContent = `Category: ${data.category} | Priority: ${data.priority} | Solved: ${data.solved} | Confidence: ${confidencePct} | ${escalationLabel} | ${ticketLabel} | ${snLabel}`;
  } catch (error) {
    responseText.textContent = `Error: ${error.message}`;
    meta.textContent = "Try again or contact support.";
  }
});
