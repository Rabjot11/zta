function showSection(section) {
  // Hide all sections
  document.querySelectorAll("main > div").forEach((div) => {
    div.style.display = "none";
  });

  // Show the selected section
  document.getElementById(section + "-section").style.display = "block";

  // Update the page title
  document.getElementById("page-title").innerText =
    section.charAt(0).toUpperCase() + section.slice(1);
}

// Function to simulate document upload
function uploadDocument() {
  let fileInput = document.getElementById("uploadDocument");
  if (fileInput.files.length > 0) {
    let fileName = fileInput.files[0].name;
    let date = new Date().toLocaleDateString();

    let newRow = `<tr>
      <td>${fileName}</td>
      <td>${date}</td>
      <td><button onclick="deleteDocument(this)">Delete</button></td>
    </tr>`;

    document.getElementById("document-list").innerHTML += newRow;
    fileInput.value = ""; // Reset file input
  } else {
    alert("Please select a file to upload.");
  }
}

// Function to delete a document row
function deleteDocument(button) {
  button.closest("tr").remove();
}
