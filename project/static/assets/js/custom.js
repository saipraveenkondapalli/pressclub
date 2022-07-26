
    value = document.getElementById("report").value
    function grammarCheck(){
        document.getElementById("grammar").innerHTML = "<div class = \"text-center\"><div class=\"spinner-border\" role=\"status\"><span class=\"sr-only\">Loading...</span></div></div>"
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                document.getElementById("grammar").innerHTML =  this.responseText;
            }
        };

        xhttp.open("GET", "/grammar_check/"+value, true);
        xhttp.send();

    };

    function fileValidation() {
            var fileInput =
                document.getElementById('file');

            var filePath = fileInput.value;

            // Allowing file type
            var allowedExtensions =
                    /(\.jpg|\.jpeg|\.png|\.gif)|\.webp|\.raw$/i;

            if (!allowedExtensions.exec(filePath)) {
                alert('Invalid file type');
                fileInput.value = '';
                return false;
            }
            else
            {
                    reader.readAsDataURL(fileInput.files[0]);
                }
            };