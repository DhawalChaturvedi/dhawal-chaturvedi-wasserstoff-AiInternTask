/**
 * Append a chat message (from user or bot) to the chat window.
 * Automatically scrolls the chat window to the newest message.
 * 
 * @param {string} sender - Either "user" or "bot" to apply styling.
 * @param {string} text - Message content to display.
 * @param {boolean} [isHTML=false] - Whether to treat text as HTML or plain text.
 */
function appendMessage(sender, text, isHTML = false) {
  const chatWindow = document.getElementById("chat-window");
  const msg = document.createElement("div");
  msg.className = `message ${sender}`;
  if (isHTML) {
    msg.innerHTML = text;
  } else {
    msg.textContent = text;
  }
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

/**
 * Format an array of query result objects into an HTML table string.
 * Each result object should have doc_id, answer, and citation properties.
 * 
 * @param {Array} results - List of result objects.
 * @returns {string} HTML string representing the table.
 */
function formatResults(results) {
  let html = `<table style="width: 100%; border-collapse: collapse; font-size: 14px;">
    <thead><tr style="background: #f0f0f0;">
      <th style="padding: 8px; border: 1px solid #ddd;">Document ID</th>
      <th style="padding: 8px; border: 1px solid #ddd;">Extracted Answer</th>
      <th style="padding: 8px; border: 1px solid #ddd;">Citation</th>
    </tr></thead><tbody>`;
  results.forEach(entry => {
    html += `<tr>
      <td style="padding: 8px; border: 1px solid #ddd;">${entry.doc_id}</td>
      <td style="padding: 8px; border: 1px solid #ddd;">${entry.answer}</td>
      <td style="padding: 8px; border: 1px solid #ddd;">${entry.citation}</td>
    </tr>`;
  });
  html += "</tbody></table>";
  return html;
}

/**
 * Fetch the list of uploaded documents from backend API.
 * Populate the dropdown select element with id "doc-select" with the documents.
 * Logs errors to console if fetch fails.
 */
async function fetchDocuments() {
  try {
    const res = await fetch("/api/documents");
    const docs = await res.json();
    const select = document.getElementById("doc-select");
    select.innerHTML = "";
    docs.forEach(doc => {
      const option = document.createElement("option");
      option.value = doc.id;
      option.textContent = doc.name || doc.id;
      select.appendChild(option);
    });
  } catch (e) {
    console.error("Error fetching documents:", e);
  }
}

/**
 * Handle querying a single document based on user's input question.
 * Sends POST request to backend API with query and selected document ID.
 * Displays results in chat window or error messages accordingly.
 */
async function queryDocument() {
  const input = document.getElementById("user-input");
  const docSelect = document.getElementById("doc-select");
  const query = input.value.trim();

  if (!query) return alert("Please enter a question.");

  const docId = docSelect.value;
  appendMessage("user", query);

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, doc_id: docId }),
    });
    const data = await res.json();

    if (data.results && data.results.length > 0) {
      const formatted = formatResults(data.results);
      appendMessage("bot", formatted, true);
    } else {
      appendMessage("bot", "No relevant answers found.");
    }
  } catch (err) {
    console.error(err);
    appendMessage("bot", "Error querying document.");
  }
}

/**
 * Fetch common themes for the current user query.
 * Sends POST request with the query to the backend.
 * Displays the list of identified themes or appropriate messages in chat.
 */
async function fetchThemes() {
  const input = document.getElementById("user-input");
  const query = input.value.trim();

  if (!query) return alert("Please enter a question.");

  appendMessage("user", query);

  try {
    const res = await fetch("/api/themes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();

    if (data.themes && data.themes.length > 0) {
      let html = "<strong>Identified Themes:</strong><br>";
      data.themes.forEach((theme, i) => {
        html += `<div style="margin: 10px 0; padding: 10px; background: #444654; border-radius: 8px;">
          <strong>Theme ${i + 1}:</strong> ${theme}
        </div>`;
      });
      appendMessage("bot", html, true);
    } else {
      appendMessage("bot", "No themes found.");
    }
  } catch (err) {
    console.error(err);
    appendMessage("bot", "Error fetching themes.");
  }
}

/**
 * Fetch cross-document synthesis of themes with citations.
 * Sends GET request to backend API with a fixed number of clusters.
 * Displays synthesized themes with document citations in the chat window.
 */
async function fetchSynthesis() {
  appendMessage("user", "Synthesize themes across all documents");

  try {
    const res = await fetch("/api/synthesize?n_clusters=4");
    const data = await res.json();

    if (data.themes && data.themes.length > 0) {
      let html = `<strong>🤖 Final Synthesized Response:</strong><br><br>`;
      data.themes.forEach((theme, i) => {
        html += `
        <div style="margin-bottom:16px; padding:12px; background:#444654; border-radius:8px;">
          <strong>🟦 Theme ${i + 1} – ${theme.summary.split(":")[0]}</strong><br>
          <div style="margin-top:4px;"><strong>📄 Documents:</strong> ${theme.citations.join(", ")}</div>
          <div style="margin-top:4px;">${theme.summary}</div>
        </div>`;
      });

      appendMessage("bot", html, true);
    } else {
      appendMessage("bot", "No synthesis available.");
    }
  } catch (err) {
    console.error("Synthesis fetch error:", err);
    appendMessage("bot", "Error fetching synthesis.");
  }
}

/**
 * Upload selected files from the file input to the backend API.
 * Sends files as multipart/form-data via POST request.
 * Shows alerts for success or failure and refreshes document list on success.
 */
async function uploadFiles() {
  const input = document.getElementById("file-input");
  const files = input.files;

  if (!files.length) return alert("Please select files to upload.");

  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }

  try {
    const res = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      throw new Error(`Upload failed with status ${res.status}`);
    }

    const data = await res.json();

    if (data.uploaded_documents && data.uploaded_documents.length > 0) {
      alert("Files uploaded successfully.");
      input.value = "";
      document.getElementById("file-names").textContent = "No files selected.";
      fetchDocuments();
    } else {
      alert("Upload failed: no valid files processed.");
    }
  } catch (err) {
    console.error("Upload error:", err);
    alert("Error uploading files.");
  }
}

/**
 * Update the UI below the file input to show names of selected files.
 * Shows "No files selected." if no files are chosen.
 */
document.getElementById("file-input").addEventListener("change", (event) => {
  const fileList = event.target.files;
  const fileNamesDiv = document.getElementById("file-names");

  if (fileList.length === 0) {
    fileNamesDiv.textContent = "No files selected.";
  } else {
    const names = Array.from(fileList).map(file => file.name);
    fileNamesDiv.textContent = "Selected files: " + names.join(", ");
  }
});

/**
 * Set up event listeners after the DOM content is fully loaded:
 * - Fetch and populate document dropdown
 * - Attach button click handlers for querying, fetching themes, synthesis, and file uploads
 * - Enable sending query on pressing Enter key in the input box
 */
document.addEventListener("DOMContentLoaded", () => {
  fetchDocuments();

  document.getElementById("send-btn").addEventListener("click", queryDocument);
  document.getElementById("theme-btn").addEventListener("click", fetchThemes);
  document.getElementById("synthesize-btn").addEventListener("click", fetchSynthesis);
  document.getElementById("upload-btn").addEventListener("click", uploadFiles);

  document.getElementById("user-input").addEventListener("keypress", e => {
    if (e.key === "Enter") {
      queryDocument();
      e.preventDefault();
    }
  });
});
