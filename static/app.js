var form = document.getElementById('upload-form');
var fileInput = document.getElementById('pdf-file');

// Prevent default drag behaviors
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  form.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults (e) {
  e.preventDefault();
  e.stopPropagation();
}

// Highlight drop area when item is dragged over it
['dragenter', 'dragover'].forEach(eventName => {
  form.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
  form.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
  form.classList.add('highlight');
}

function unhighlight(e) {
  form.classList.remove('highlight');
}

// Handle drop
form.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
  var dt = e.dataTransfer;
  var files = dt.files;

  handleFiles(files);
}

function handleFiles(files) {
  ([...files]).forEach(uploadFile);
}

form.addEventListener('submit', function(event) {
  event.preventDefault();

  var files = fileInput.files;
  handleFiles(files);
});

function uploadFile(file) {
  var formData = new FormData();
  formData.append('pdf', file);
  document.getElementById('loading').style.display = 'block';

  fetch('/upload', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById('upload-form').style.display = 'none';
    document.getElementById('loading').style.display = 'none';
    document.getElementById('upload-another').style.display = 'block';
    document.getElementById('response').style.display = 'block';
    
    // Replace newline characters with <br> tags
    var responseText = data["response"].replace(/\n/g, '<br>');
    
    // Replace double asterisks with <b> tags
    responseText = responseText.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
    
    document.getElementById('response').innerHTML = responseText;
})
  .catch(error => {
    console.error('Error:', error);
    document.getElementById('loading').style.display = 'none';
    // Show an alert
    alert('Failed to upload file. Please try again.');
  });
}

document.getElementById('upload-another').addEventListener('click', function() {
    location.reload();
});