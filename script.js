document.addEventListener('DOMContentLoaded', function () {
    const video = document.getElementById('videoElement');
    const canvas = document.getElementById('canvasElement');
    const predictionDiv = document.getElementById('prediction');

    // Inicialização da câmera
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                video.srcObject = stream;
                video.play();
                video.onloadeddata = function () {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    setInterval(processVideo, 1000); // Chama a função processVideo a cada 1s
                };
            })
            .catch(function (err) {
                console.error("Erro ao acessar a câmera: " + err);
                predictionDiv.innerText = "Erro ao acessar a câmera: " + err;
            });
    } else {
        console.error("getUserMedia não é suportado no seu navegador.");
        predictionDiv.innerText = "getUserMedia não é suportado no seu navegador.";
    }

    // Função para processar o vídeo e enviar a imagem ao servidor
    function processVideo() {
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Capturar a imagem do canvas
        canvas.toBlob(function (blob) {
            const formData = new FormData();
            formData.append('image', blob, 'frame.png');

            fetch('/predict', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                predictionDiv.innerText = `Tradução da libra: ${data.prediction}`;
            })
            .catch(error => console.error('Erro:', error));
        }, 'image/png');
    }
});
