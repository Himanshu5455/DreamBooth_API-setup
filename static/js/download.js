$(document).ready(function() {
    $('.download-image').click(function() {
      const url = $(this).siblings('img').attr('src');
      downloadImage(url);
    });
  
    function downloadImage(url) {
      fetch(url, {
        mode: 'no-cors'
      })
      .then(response => response.blob())
      .then(blob => {
        const filename = url.split('/').pop();
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.download = filename;
        a.href = blobUrl;
        document.body.appendChild(a);
        a.click();
        a.remove();
      })
      .catch(error => {
        console.error('Error downloading image:', error);
      });
    }
  });

  