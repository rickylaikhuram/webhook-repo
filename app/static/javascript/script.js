const API_URL = "http://localhost:5000/api/events";
const POLL_INTERVAL = 15000;

function formatDate(timestamp) {
  const date = new Date(timestamp);
  const options = {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
    timeZone: "UTC",
  };
  return date.toLocaleDateString("en-US", options) + " UTC";
}

function createEventElement(event) {
  const eventDiv = document.createElement("div");
  eventDiv.className = `event ${event.action}`;

  const badge = document.createElement("div");
  badge.className = `badge ${event.action}`;
  badge.textContent = event.action.replace("_", " ");

  const text = document.createElement("div");
  text.className = "event-text";

  let message = "";
  if (event.action === "push") {
    message = `<span class="author">${event.author}</span> pushed to <span class="branch">${event.to_branch}</span> on <span class="timestamp">${formatDate(event.timestamp)}</span>`;
  } else if (event.action === "pull_request") {
    message = `<span class="author">${event.author}</span> submitted a pull request from <span class="branch">${event.from_branch}</span> to <span class="branch">${event.to_branch}</span> on <span class="timestamp">${formatDate(event.timestamp)}</span>`;
  } else if (event.action === "merge") {
    message = `<span class="author">${event.author}</span> merged branch <span class="branch">${event.from_branch}</span> to <span class="branch">${event.to_branch}</span> on <span class="timestamp">${formatDate(event.timestamp)}</span>`;
  }

  text.innerHTML = message;

  eventDiv.appendChild(badge);
  eventDiv.appendChild(text);

  return eventDiv;
}

async function fetchEvents() {
  try {
    const response = await fetch(API_URL);
    const events = await response.json();
    const container = document.getElementById("eventsContainer");
    const statusEl = document.getElementById("status");

    statusEl.textContent = "~ Connected";
    statusEl.className = "status active";

    if (events.length === 0) {
      container.innerHTML =
        '<div class="no-events">No events yet. Push, create a PR, or merge in your repository!</div>';
    }

    events.sort(
      (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
    );

    container.innerHTML = "";
    events.forEach((event) => {
      container.appendChild(createEventElement(event));
    });
  } catch (error) {
    console.error("Error fetching events:", error);
    const statusEl = document.getElementById("status");
    statusEl.textContent = "~ Connection Error";
    statusEl.className = "status";
  }
}

// Initial fetch
fetchEvents();

// Poll every 15 seconds
setInterval(fetchEvents, POLL_INTERVAL);
